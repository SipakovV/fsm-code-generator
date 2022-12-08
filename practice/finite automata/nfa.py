from copy import deepcopy
from typing import Union
import itertools


class NFA:
    def __init__(self, alphabet: set[str], state_set: set[Union[str, int]], init_state: Union[str, int], final_states: set[Union[str, int]], transition_map: dict, epsilon_mode: bool = False):
        assert len(transition_map) == len(state_set)
        assert (row in state_set for row in transition_map)
        assert init_state in state_set
        assert final_states.issubset(state_set)

        self.alphabet = alphabet
        self.state_set = state_set
        self.init_state = init_state
        self.final_states = final_states

        if not epsilon_mode:
            self.transition_map = transition_map
        else:
            self.transition_map = {}
            for q in transition_map:
                q_closed = self._epsilon_closure(q, transition_map)
                res_entry = {}
                for char in self.alphabet:
                    q_set = set()
                    for p in q_closed:
                        try:
                            q_set.update(transition_map[p][char])
                        except KeyError:
                            pass
                    if q_set:
                        res_entry[char] = q_set
                self.transition_map[q] = res_entry
                if q not in self.final_states:
                    for p in q_closed:
                        if p in self.final_states:
                            self.final_states.add(q)
                            break

    def __repr__(self):
        try:
            out = f'{self.__name__}\n'
        except AttributeError:
            pass
        out = f'NFA:\n'

        for k, v in self.__dict__.items():
            out += '{:>4s}: {}\n'.format(k, v)
        return out

    def __eq__(self, other) -> bool:
        assert isinstance(other, NFA)
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

    def _epsilon_closure(self, state: Union[str, int], transition_map: dict) -> set[Union[str, int]]:
        res = {state}
        try:
            q_set = transition_map[state]['EPS']
        except KeyError:
            return res

        for q in q_set:
            res.add(q)
            res.update(self._epsilon_closure(q, transition_map))
        return res

    def parse(self, string: str) -> bool:
        q_set = {self.init_state}

        for char in string:
            if not q_set:
                return False
            q_res = set()
            for q in q_set:
                try:
                    q_res.update(self.transition_map[q][char])
                except KeyError:
                    pass
            q_set = q_res

        for q in q_set:
            if q in self.final_states:
                return True
        return False

