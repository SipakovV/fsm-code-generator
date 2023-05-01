import os
from typing import Union, List, Set

import graphviz

from fsm_core.code_generator import CodeGeneratorBackend


class AcceptorFSM:
    def __init__(self, alphabet: Set[str], state_set: Set[Union[str, int]],
                 initial_state: Union[str, int], transition_map: dict,
                 final_states: Set[Union[str, int]] = None,
                 name: str = 'unnamed_fsm', title: str = 'Unnamed', description: str = '',):
        self._name = name
        self._title = title
        if description:
            self._description = description
        else:
            self._description = self._name

        self.alphabet = alphabet
        self.state_set = state_set
        self.init_state = initial_state

        if not final_states:
            self.final_states = set()
        else:
            assert final_states.issubset(state_set)
            self.final_states = final_states
        self.transition_map = transition_map

        assert initial_state in state_set

        assert all(state in state_set for state in transition_map), \
            'Transition map contains states not in state set'
        assert all(all(transition_map[state][event][0] in state_set for event in transition_map[state]) for state in
                   transition_map), \
            'Transition map contains target states not in state set'
        assert all(all(event in alphabet for event in transition_map[state]) for state in transition_map), \
            'Transition map contains events not in alphabet'

    def __repr__(self):
        try:
            out = f'{self.__name__}\n'
        except AttributeError:
            out = f'DFA:\n'

        for k, v in self.__dict__.items():
            out += '{:>4s}: {}\n'.format(k, v)
        return out

    def __eq__(self, other) -> bool:
        assert isinstance(other, AcceptorFSM)
        if self.alphabet != other.alphabet:
            print('Alphabets don\'t match')
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

    """
    Decision properties
    """
    def is_empty(self) -> bool:
        # if final states unreachable
        marked_states = set()
        stack = []

        state = self.init_state
        traversed_arcs = set()

        print()

        if not self.final_states:
            return True

        while True:
            arcs = set(self.transition_map[state])
            print(f'{state=}: {arcs=}, {traversed_arcs=}, {marked_states=}, {stack=}')
            if traversed_arcs == arcs:
                if stack:
                    # return up
                    state, traversed_arcs = stack.pop()
                    continue
                else:
                    # exit tree
                    break

            marked_states.add(state)
            if marked_states == self.state_set:
                break

            for transition_arc in arcs.difference(traversed_arcs):
                new_state = self.transition_map[state][transition_arc]
                if new_state in marked_states:
                    continue
                else:
                    break
            else:
                # if all remaining states are marked
                if stack:
                    # return up
                    state, traversed_arcs = stack.pop()
                    continue
                else:
                    # exit tree
                    break

            traversed_arcs.add(transition_arc)

            stack.append((state, traversed_arcs))
            traversed_arcs = set()
            state = new_state

        if marked_states.intersection(self.final_states):
            return False
        else:
            return True

    def is_infinite(self) -> bool:
        # if contains cycles on the path from init state to final states

        # marked_states = set()
        stack = []
        state = self.init_state
        traversed_arcs = set()
        has_cycle_on_path = False

        print()

        while True:
            arcs = set(self.transition_map[state])
            print(f'{state=}: {arcs=}, {traversed_arcs=}, {stack=}')

            # current_cycle = False

            if traversed_arcs == arcs:
                if stack:
                    # return up
                    state, traversed_arcs, has_cycle_on_path = stack.pop()
                    continue
                else:
                    # no cycles found
                    return False

            # marked_states.add(state)

            if state in self.final_states:
                if has_cycle_on_path:
                    print('found final state with cycles on path:', state)
                    return True

            for transition_arc in arcs.difference(traversed_arcs):
                new_state = self.transition_map[state][transition_arc]

                if has_cycle_on_path:
                    continue
                else:
                    if new_state == state:
                        has_cycle_on_path = True
                        print('found cycle', new_state)
                    for item in stack:
                        if new_state == item[0]:
                            has_cycle_on_path = True
                            print('found cycle', new_state)
                            break
                    break
            else:
                if stack:
                    # return up
                    state, traversed_arcs, has_cycle_on_path = stack.pop()
                    continue
                else:
                    # no cycles found
                    return False

            traversed_arcs.add(transition_arc)

            stack.append((state, traversed_arcs, has_cycle_on_path))
            traversed_arcs = set()
            state = new_state

    def parse(self, string: str) -> bool:

        q = self.init_state

        for char in string:
            q = self.transition_map[q][char]

        if q in self.final_states:
            return True
        else:
            return False

    def _generate_graph(self) -> graphviz.Digraph:
        #dot = graphviz.Digraph(self._name, comment=self._title + ': ' + self._description)
        dot = graphviz.Digraph(self._name, comment=self._name)
        #size='15,16',
        dot.attr(pad='0.5', nodesep='1', ranksep='0')

        dot.node('START', shape='diamond')

        for state in self.state_set:
            if state in self.final_states:
                dot.node(state, shape='doublecircle')
            else:
                dot.node(state)

        for state in self.transition_map:
            #print('state:', state)
            for event in self.transition_map[state]:
                #print('event:', event)
                label = '<<b>' + event + '</b>>'
                dot.edge(state, self.transition_map[state][event], label=label)

        dot.edge('START', self.init_state)

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
        base_graph.render('_base', directory=path, format='png').replace('\\', '/')

        if all_states:
            for state in self.state_set:
                dot = self._generate_graph(state)
                filename = state
                dot.render(filename, directory=path, format='png').replace('\\', '/')

    def generate_code_python(self, file_path: str = None):
        code_gen = CodeGeneratorBackend()
        code_gen.begin(tab='    ')

        """Metadata config (for GUI)"""
        conf_string = f"'type': 'acceptor', 'title': '{self._title}', 'description': '{self._description}'"
        code_gen.write("config = {" + conf_string + "}")
        code_gen.write(f"alphabet = {list(self.alphabet)}")
        code_gen.write("")
        code_gen.write("")

        """Main parse() function"""
        code_gen.write("def parse(string):")
        code_gen.indent()
        code_gen.write(f"state = '{self.init_state}'")
        code_gen.write("for ch in string:")
        code_gen.indent()
        code_gen.write("if ch not in alphabet:")
        code_gen.indent()
        code_gen.write("raise ValueError('Error: Invalid character')")
        code_gen.dedent()
        i = 0
        for state in self.transition_map:
            if i == 0:
                code_gen.write(f"if state == '{state}':")
            else:
                code_gen.write(f"elif state == '{state}':")
            code_gen.indent()
            transitions = self.transition_map[state]
            for ch in self.transition_map[state]:
                code_gen.write(f"if ch == '{ch}':")
                code_gen.indent()
                code_gen.write(f"state = '{transitions[ch]}'")
                code_gen.dedent()
            code_gen.dedent()
            i += 1
        code_gen.dedent()

        if self.final_states:
            if_statement = "if state in {"
            for state in self.final_states:
                if_statement += f'{state}, '
            if_statement += '}:'
            code_gen.write(if_statement)
            code_gen.indent()
            code_gen.write("return True")
            code_gen.dedent()
            code_gen.write("else:")
            code_gen.indent()
            code_gen.write("return False")
            code_gen.dedent()
        else:
            code_gen.write("return False")
        code_gen.dedent()

        if not file_path:
            file_name = self._name + '.py'
            file_path = 'python_fsm_generated/' + file_name
        f = open(file_path, 'w')
        f.write(code_gen.end())
        f.close()
