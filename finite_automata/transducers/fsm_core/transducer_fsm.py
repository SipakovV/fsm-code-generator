import os
from typing import Union, List, Set

import graphviz

from fsm_core.code_generator import CodeGeneratorBackend


class TransducerFSM:
    def __init__(self, alphabet: Set[str], instructions_set: Set[str], state_set: Set[Union[str, int]],
              initial_state: Union[str, int], transition_map: dict,
              initial_instructions: List[Union[str, tuple]] = None, final_states: Set[Union[str, int]] = None,
              name: str = 'unnamed_fsm', title: str = 'Unnamed', description: str = '',):
        self._name = name
        self._title = title
        if description:
            self._description = description
        else:
            self._description = self._name

        self.alphabet = alphabet
        self.instructions_set = instructions_set
        self.state_set = state_set
        self.init_state = initial_state
        if not initial_instructions:
            self.init_instructions = list()
        else:
            assert all(instr in instructions_set if type(instr) is str else instr[0] in instructions_set for instr in initial_instructions)
            self.init_instructions = initial_instructions

        if not final_states:
            self.final_states = set()
        else:
            assert final_states.issubset(state_set)
            self.final_states = final_states
        self.transition_map = transition_map

        assert initial_state in state_set
        assert all(instr in instructions_set or type(instr) is tuple and instr[0] in instructions_set for instr in
                   self.init_instructions)

        assert all(state in state_set for state in transition_map), \
            'Transition map contains states not in state set'
        assert all(all(transition_map[state][event][0] in state_set for event in transition_map[state]) for state in
                   transition_map), \
            'Transition map contains target states not in state set'
        assert all(all(event in alphabet for event in transition_map[state]) for state in transition_map), \
            'Transition map contains events not in alphabet'
        assert all(all(all(
            instr in instructions_set or (type(instr) is tuple and instr[0] in instructions_set) for instr in
            transition_map[state][event][1]) for event in transition_map[state]) for state in transition_map), \
            'Transition map contains instructions not in instructions set'

    def __repr__(self):
        try:
            out = f'{self.__name__}\n'
        except AttributeError:
            out = f'DFA:\n'

        for k, v in self.__dict__.items():
            out += '{:>4s}: {}\n'.format(k, v)
        return out

    def __eq__(self, other) -> bool:
        assert isinstance(other, TransducerFSM)
        if self.alphabet != other.alphabet:
            print('Alphabets don\'t match')
            return False
        if self.instructions_set != other.instructions_set:
            print('Instruction sets don\'t match')
            return False
        if self.state_set != other.state_set:
            print('Statesets don\'t match')
            return False
        if self.init_state != other.init_state:
            print('Init states don\'t match')
            return False
        if self.final_states != other.final_states:
            print('Final states don\'t match')
            return False
        if self.transition_map != other.transition_map:
            print('Transition maps don\'t match')
            print(self.transition_map)
            print(other.transition_map)
            return False
        return True

    def _send_instruction(self, instruction, queue):
        if type(instruction) is tuple:
            queue.put_instruction(instruction[0], instruction[1])
        else:
            queue.put_instruction(instruction)

    def run(self, event_queue):
        state = self.init_state
        for instr in self.init_instructions:
            self._send_instruction(instr, event_queue)

        while True:
            if state in self.final_states:
                print('final state reached:', state)
                break

            event = event_queue.get_next_event()
            old_state = state

            if state in self.transition_map:
                transitions_available = self.transition_map[state]
                if event in transitions_available:
                    target_state, instruction_list = transitions_available[event]
                    for instr in instruction_list:
                        self._send_instruction(instr, event_queue)
                    state = target_state
                    print(f'== State change: {old_state} -{event}-> {state}')

    def _generate_graph(self, selected_state: str = '') -> graphviz.Digraph:
        #dot = graphviz.Digraph(self._name, comment=self._title + ': ' + self._description)
        dot = graphviz.Digraph(self._name, comment=self._name)
        #size='15,16',
        dot.attr(pad='0.5', nodesep='1', ranksep='0')

        dot.node('START', shape='diamond')

        for state in self.state_set:
            if state == selected_state:
                dot.node(state, fillcolor='yellow', style='filled')
            else:
                dot.node(state)

        for state in self.transition_map:
            #print('state:', state)
            for event in self.transition_map[state]:
                #print('event:', event)
                target_state, instruction_list = self.transition_map[state][event]
                label = '<<b>' + event + '</b><br/>'
                for instr in instruction_list:
                    if type(instr) is str:
                        label += '<i>' + instr + '</i><br/>'
                    else:
                        label += '<i>' + instr[0] + ' ' + str(instr[1]) + '</i><br/>'
                label += '>'
                dot.edge(state, target_state, label=label)

        label = '<'
        for instr in self.init_instructions:
            if type(instr) is str:
                label += '<i>' + instr + '</i><br/>'
            else:
                label += '<i>' + instr[0] + ', ' + str(instr[1]) + '</i><br/>'
        label += '>'
        dot.edge('START', self.init_state, label=label)

        return dot

    def visualize(self, directory: str = None, all_states: bool = False):
        if not directory:
            directory = 'generated_graph_images'

        try:
            os.mkdir(directory)
        except FileExistsError as exc:
            pass

        path = os.path.join(directory, self._name)
        #print(path)
        try:
            os.mkdir(path)
        except FileExistsError as exc:
            pass

        base_graph = self._generate_graph()
        base_graph.save('_base.dot', directory=path).replace('\\', '/')
        base_graph.render('_base', directory=path, format='png').replace('\\', '/')

        if all_states:
            for state in self.state_set:
                dot = self._generate_graph(state)
                filename = state
                dot.render(filename, directory=path, format='png').replace('\\', '/')

    def generate_code_python(self, file_path: str = None):
        code_gen = CodeGeneratorBackend()
        code_gen.begin(tab='    ')

        """Import statements"""
        code_gen.write("from python_server import event_queue")
        code_gen.write("")
        code_gen.write("")

        """Metadata config (for GUI)"""
        conf_string = f"'type': 'transducer', 'title': '{self._title}', 'description': '{self._description}', " \
                      f"'instructions_set': {list(self.instructions_set)}, 'events_set': {list(self.alphabet)}"
        code_gen.write("config = {" + conf_string + "}")
        code_gen.write("")
        code_gen.write("")

        """Main run_fsm() function"""
        code_gen.write("def run_fsm():")
        code_gen.indent()
        code_gen.write(f"state = '{self.init_state}'")
        code_gen.write(f"event_queue.put_config(config)")
        for instr in self.init_instructions:
            if type(instr) is tuple:
                code_gen.write(f"event_queue.put_instruction('{instr[0]}', {str(instr[1])})")
            elif type(instr) is str:
                code_gen.write(f"event_queue.put_instruction('{instr}')")
            else:
                raise TypeError('Unknown instruction type')
        code_gen.write("event_queue.put_state(state)")
        code_gen.write("while True:")
        code_gen.indent()
        code_gen.write("old_state = state")
        code_gen.write("event = event_queue.get_next_event()")
        i = 0
        for state in self.transition_map:
            if i == 0:
                code_gen.write(f"if state == '{state}':")
            else:
                code_gen.write(f"elif state == '{state}':")
            code_gen.indent()
            transitions = self.transition_map[state]
            for event in self.transition_map[state]:
                code_gen.write(f"if event == '{event}':")
                code_gen.indent()
                target_state, instruction_list = transitions[event]
                for instr in instruction_list:
                    if type(instr) is tuple:
                        code_gen.write(f"event_queue.put_instruction('{instr[0]}', {str(instr[1])})")
                    elif type(instr) is str:
                        code_gen.write(f"event_queue.put_instruction('{instr}')")
                    else:
                        raise TypeError('Unknown instruction type')
                code_gen.write(f"state = '{target_state}'")
                code_gen.dedent()
            code_gen.dedent()
            i += 1
        code_gen.write("if old_state != state:")
        code_gen.indent()
        code_gen.write("event_queue.put_state(state)")
        code_gen.dedent()
        code_gen.dedent()
        code_gen.dedent()
        if not file_path:
            file_name = self._name + '.py'
            file_path = 'python_fsm_generated/' + file_name
        f = open(file_path, 'w')
        f.write(code_gen.end())
        f.close()
