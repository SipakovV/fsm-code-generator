from copy import deepcopy
from typing import Union
import itertools


class NFA:
    def __init__(self, alphabet: set[str], state_set: set[Union[str, int]], init_state: Union[str, int], final_states: set[Union[str, int]], transition_map: dict):
        self.alphabet = alphabet
        self.state_set = state_set
        self.init_state = init_state
        self.final_states = final_states
        self.transition_map = transition_map

        self.char_index = {}
        for i, char in enumerate(transition_map['HEADER']):
            self.char_index[char] = i

    def __repr__(self):
        try:
            out = f'{self.__name__}\n'
        except AttributeError:
            pass
        out = f'DFA:\n'

        for k, v in self.__dict__.items():
            out += '{:>4s}: {}\n'.format(k, v)
        return out

    def parse(self, string: str) -> bool:
        q_set = {self.init_state}

        for char in string:
            q_res = set()
            for q in q_set:
                q_res.update(self.transition_map[q][self.char_index[char]])
            q_set = q_res
            print(char, q_set)

        for q in q_set:
            if q in self.final_states:
                return True
        return False
