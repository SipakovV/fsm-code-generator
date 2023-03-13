from typing import Union

import graphviz

import event_queue


class FSM:
    def __init__(self, *args, **kwargs):
        if 'fsm' in kwargs:
                orig = kwargs['fsm']
                assert isinstance(orig, FSM), "can only copy instances of FSM"
                self._init(orig.alphabet, orig.state_set, orig.init_state, orig.final_states, orig.transition_map)
        else:
            self._init(*args)

    def __repr__(self):
        try:
            out = f'{self.__name__}\n'
        except AttributeError:
            out = f'DFA:\n'

        for k, v in self.__dict__.items():
            out += '{:>4s}: {}\n'.format(k, v)
        return out

    def __eq__(self, other) -> bool:
        assert isinstance(other, FSM)
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

    def _init(self, alphabet: set[str], instructions_set: set[str], state_set: set[Union[str, int]], init_state: Union[str, int], init_instructions: list[Union[str, tuple]], final_states: set[Union[str, int]], transition_map: dict, name: str = 'sample_fsm'):
        self._name = name

        self.alphabet = alphabet
        self.instructions_set = instructions_set
        self.state_set = state_set
        self.init_state = init_state
        self.init_instructions = init_instructions
        self.final_states = final_states
        self.transition_map = transition_map

    def send_instruction(self, *instruction):
        event_queue.put_instruction(*instruction)

    def run(self):
        q = self.init_state

        for char in string:
            q = self.transition_map[q][char]

        if q in self.final_states:
            return True
        else:
            return False

    def visualize(self):
        dot = graphviz.Digraph('fsm', comment=self._name)

        dot.node('START')

        for state in self.state_set:
            dot.node(state)

        for state in self.transition_map:
            print('state:', state)
            for event in self.transition_map[state]:
                print('event:', event)
                target_state, instruction_list = self.transition_map[state][event]
                label = event
                for instr in instruction_list:
                    if type(instr) is str:
                        label += ' | <' + instr + '>'
                    else:
                        label += ' | <' + instr[0] + ', ' + str(instr[1]) + '>'
                dot.edge(state, target_state, label=label)

        label = ''
        for instr in self.init_instructions:
            if type(instr) is str:
                label += ' | <' + instr + '>'
            else:
                label += ' | <' + instr[0] + ', ' + str(instr[1]) + '>'
        dot.edge('START', self.init_state, label=label)

        print(dot)
        dot.render(directory='doctest-output', view=True).replace('\\', '/')

    def generate_code_python(self):
        pass