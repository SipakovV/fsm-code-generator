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
            elif action == 'and not' and (state[0] in first_dfa.final_states and state[1] not in second_dfa.final_states):
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


def are_equivalent_DFA(dfa1: DFA, dfa2: DFA) -> bool:
    # if XOR product is empty

    assert isinstance(dfa1, DFA)
    assert isinstance(dfa2, DFA)

    xor_product_dfa = DFA(dfa_set=(dfa1, dfa2), action='xor')

    print()
    print(xor_product_dfa.final_states)

    if xor_product_dfa.is_empty():
        return True
    else:
        return False


def contains_DFA(dfa: DFA, dfa_sub: DFA) -> bool:
    # if dfa_sub AND NOT dfa product is empty and dfa AND NOT dfa_sub product is not

    assert isinstance(dfa, DFA)
    assert isinstance(dfa_sub, DFA)

    complement_product_dfa = DFA(dfa_set=(dfa_sub, dfa), action='and not')

    print()
    print(complement_product_dfa.final_states)

    if complement_product_dfa.is_empty():
        return True
    else:
        return False