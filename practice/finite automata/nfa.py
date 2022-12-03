from copy import deepcopy
from typing import Union
import itertools


class NFA:
    def __init__(self, alphabet: set[str], state_set: set[Union[str, int]], init_state: Union[str, int], final_states: set[Union[str, int]], transition_map: dict, epsilon_mode: bool = False):
        assert len(transition_map) == len(state_set) + 1
        assert (row in state_set for row in transition_map)

        if not epsilon_mode:
            #assert (all(len(alphabet) == len(row) for row in transition_map.values()))
            assert set(transition_map['HEADER']) == alphabet
        else:
            #assert (all(len(alphabet) + 1 == len(row) for row in transition_map.values()))
            assert transition_map['HEADER'][-1] == 'EPS'
            assert set(transition_map['HEADER']) == set().union(alphabet, {'EPS'})
        assert init_state in state_set
        assert final_states.issubset(state_set)

        self.alphabet = alphabet
        self.state_set = state_set
        self.init_state = init_state
        self.final_states = final_states

        if not epsilon_mode:
            self.transition_map = transition_map
        else:
            self.transition_map = {
                'HEADER': transition_map['HEADER'][:-1]
            }
            for q in list(transition_map.keys())[1:]:
                q_closed = self.epsilon_closure(q, transition_map)
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
                        #print('added', res_entry[char])
                #print('res entry = ', res_entry)
                self.transition_map[q] = res_entry
                #for target_q_set in transition_map[q]:
                if q not in self.final_states:
                    for p in q_closed:
                        if p in self.final_states:
                            self.final_states.add(q)
                            break

        #self.char_index = {}
        #for i, char in enumerate(self.transition_map['HEADER']):
        #    self.char_index[char] = i

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

    def epsilon_closure(self, state: Union[str, int], transition_map: dict) -> set[Union[str, int]]:
        res = {state}
        try:
            q_set = transition_map[state]['EPS']
        except KeyError:
            return res

        for q in q_set:
            res.add(q)
            res.update(self.epsilon_closure(q, transition_map))
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
            #print('\n', char, q_set)

        for q in q_set:
            if q in self.final_states:
                return True
        return False

