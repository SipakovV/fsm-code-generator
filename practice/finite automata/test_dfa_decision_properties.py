import pytest

from dfa import DFA


def test_DFA_emptiness():
    # empty
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3, 4, 5}
    initial_state = 0
    final_states = {5}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 0, '1': 3},
        2: {'0': 0, '1': 3},
        3: {'0': 1, '1': 2},
        4: {'0': 4, '1': 5},
        5: {'0': 5, '1': 4},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    empty_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert empty_dfa.is_empty()

    # not empty
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3, 4, 5}
    initial_state = 0
    final_states = {5}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 0, '1': 3},
        2: {'0': 0, '1': 4},
        3: {'0': 1, '1': 2},
        4: {'0': 4, '1': 5},
        5: {'0': 5, '1': 4},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    empty_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert not empty_dfa.is_empty()

    # explicitly empty
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3, 4, 5}
    initial_state = 0
    final_states = set()
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 0, '1': 3},
        2: {'0': 0, '1': 4},
        3: {'0': 1, '1': 2},
        4: {'0': 4, '1': 5},
        5: {'0': 5, '1': 4},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    empty_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert empty_dfa.is_empty()


def test_DFA_infiniteness():
    # non-infinite
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3, 4}
    initial_state = 0
    final_states = {4}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 3, '1': 2},
        2: {'0': 3, '1': 4},
        3: {'0': 3, '1': 3},
        4: {'0': 3, '1': 3},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    non_infinite_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert not non_infinite_dfa.is_infinite()

    # infinite
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3, 4, 5}
    initial_state = 0
    final_states = {5}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 3, '1': 2},
        2: {'0': 3, '1': 4},
        3: {'0': 5, '1': 5},
        4: {'0': 5, '1': 5},
        5: {'0': 4, '1': 2},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    infinite_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert infinite_dfa.is_infinite()
