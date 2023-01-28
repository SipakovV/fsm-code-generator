from copy import deepcopy
from typing import Union
import itertools


class DFA:
    def __init__(self, *args, **kwargs):
        if 'dfa_set' in kwargs.keys():
            if len(kwargs['dfa_set']) == 1:
                orig, = kwargs['dfa_set']
                assert isinstance(orig, DFA), "can only copy instances of DFA"
                self._init(orig.alphabet, orig.state_set, orig.init_state, orig.final_states, orig.transition_map)
            else:
                assert 'action' in kwargs.keys()
                self._init_cartesian_product(kwargs['dfa_set'], kwargs['action'])
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
        assert isinstance(other, DFA)
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

    def _init_cartesian_product(self, dfa_set: tuple, action: str):
        #assert len(dfa_set) > 1
        assert len(dfa_set) == 2

        alphabet = None
        for dfa in dfa_set:
            assert isinstance(dfa, DFA), "can only init cartesian product from DFAs"
            if not alphabet:
                alphabet = dfa.alphabet
            else:
                assert dfa.alphabet == alphabet
        self.alphabet = alphabet

        self.state_set = set()
        first_dfa, second_dfa = dfa_set

        self.init_state = str((first_dfa.init_state, second_dfa.init_state))

        self.transition_map = {}

        self.final_states = set()

        for state in itertools.product(first_dfa.state_set, second_dfa.state_set):
            state_name = str(state)
            self.state_set.add(state_name)

            map_entry = {}
            first_transition = first_dfa.transition_map[state[0]]
            second_transition = second_dfa.transition_map[state[1]]
            for char in self.alphabet:
                result_state = (first_transition[char], second_transition[char])
                map_entry[char] = str(result_state)
            self.transition_map[state_name] = map_entry

            if action == 'or' and (state[0] in first_dfa.final_states or state[1] in second_dfa.final_states):
                self.final_states.add(state_name)
            elif action == 'and' and (state[0] in first_dfa.final_states and state[1] in second_dfa.final_states):
                self.final_states.add(state_name)
            elif action == 'xor' and (state[0] in first_dfa.final_states and state[1] not in second_dfa.final_states or
                                      state[0] not in first_dfa.final_states and state[1] in second_dfa.final_states):
                self.final_states.add(state_name)

        #print('\n', self.state_set, self.init_state)

    def _init(self, alphabet: set[str], state_set: set[Union[str, int]], init_state: Union[str, int], final_states: set[Union[str, int]], transition_map: dict):
        self.alphabet = alphabet
        self.state_set = state_set
        self.init_state = init_state
        self.final_states = final_states
        self.transition_map = transition_map

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

        while True:
            #print(self.transition_map[state].keys())
            #print(f'{state=}: {traversed_arcs=}, {marked_states=}')
            arcs = set(self.transition_map[state])
            print(f'{state=}: {arcs=}, {traversed_arcs=}, {marked_states=}, {stack=}')
            if traversed_arcs == arcs:
                # return up
                if stack:
                    state, traversed_arcs = stack.pop()
                    continue
                else:
                    break

            marked_states.add(state)

            for transition_arc in arcs.difference(traversed_arcs):
                new_state = self.transition_map[state][transition_arc]
                if new_state in marked_states:
                    continue
                else:
                    break
            else:
                if stack:
                    state, traversed_arcs = stack.pop()
                    continue
                else:
                    break


            #print(new_state)
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
        pass

    def is_equivalent(self, other) -> bool:
        assert isinstance(other, DFA)
        # if
        pass

    def parse(self, string: str) -> bool:

        q = self.init_state

        for char in string:
            q = self.transition_map[q][char]

        if q in self.final_states:
            return True
        else:
            return False
