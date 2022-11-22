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
            pass
        out = f'DFA:\n'

        for k, v in self.__dict__.items():
            out += '{:>4s}: {}\n'.format(k, v)
        return out

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

        assert first_dfa.transition_map['HEADER'] == second_dfa.transition_map['HEADER']
        self.transition_map = {
            'HEADER': first_dfa.transition_map['HEADER']
        }

        self.char_index = {}
        for i, char in enumerate(self.transition_map['HEADER']):
            self.char_index[char] = i

        self.final_states = set()

        for state in itertools.product(first_dfa.state_set, second_dfa.state_set):
            state_name = str(state)
            self.state_set.add(state_name)

            map_entry = []
            first_transition = first_dfa.transition_map[state[0]]
            second_transition = second_dfa.transition_map[state[1]]
            for char in self.transition_map['HEADER']:
                result_state = (first_transition[self.char_index[char]], second_transition[self.char_index[char]])
                map_entry.append(str(result_state))
            self.transition_map[state_name] = tuple(map_entry)

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

        self.char_index = {}
        for i, char in enumerate(transition_map['HEADER']):
            self.char_index[char] = i

    def parse(self, string: str) -> bool:

        #print('\ninput:', string)

        q = self.init_state

        #print(q, type(q))

        for char in string:
            q = self.transition_map[q][self.char_index[char]]
            #print(q, char)

        if q in self.final_states:
            return True
        else:
            return False


'''
class DFAExtended(DFA):
    def __init__(self, dfa1: DFA, dfa2: DFA):
        state_set
'''