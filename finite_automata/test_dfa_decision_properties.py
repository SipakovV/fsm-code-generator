import pytest

from dfa import DFA, are_equivalent_DFA, contains_DFA


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


def test_DFA_infiniteness_negative():
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


def test_DFA_infiniteness_positive():
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


def test_DFA_equivalence_negative():
    # first DFA - even ones
    alphabet = {'0', '1'}
    state_set = {0, 1}
    initial_state = 0
    final_states = {0}
    transition_map = {
        0: {'0': 0, '1': 1},
        1: {'0': 1, '1': 0},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    even_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    # second DFA - alternation
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3}
    initial_state = 0
    final_states = {0, 1, 2}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 3, '1': 2},
        2: {'0': 1, '1': 3},
        3: {'0': 3, '1': 3},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert not are_equivalent_DFA(even_ones_dfa, alternation_dfa)


def test_DFA_equivalence_positive():
    # first DFA - alternation
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3}
    initial_state = 0
    final_states = {0, 1, 2}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 3, '1': 2},
        2: {'0': 1, '1': 3},
        3: {'0': 3, '1': 3},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa1 = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    # second DFA - alternation
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3, 4}
    initial_state = 0
    final_states = {0, 1, 2}
    transition_map = {
        0: {'0': 2, '1': 1},
        1: {'0': 2, '1': 4},
        2: {'0': 3, '1': 1},
        3: {'0': 3, '1': 4},
        4: {'0': 3, '1': 4},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa2 = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert are_equivalent_DFA(alternation_dfa1, alternation_dfa2)


def test_DFA_containment_positive_equivalence():
    # first DFA - alternation
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3}
    initial_state = 0
    final_states = {0, 1, 2}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 3, '1': 2},
        2: {'0': 1, '1': 3},
        3: {'0': 3, '1': 3},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa1 = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    # second DFA - alternation
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3, 4}
    initial_state = 0
    final_states = {0, 1, 2}
    transition_map = {
        0: {'0': 2, '1': 1},
        1: {'0': 2, '1': 4},
        2: {'0': 3, '1': 1},
        3: {'0': 3, '1': 4},
        4: {'0': 3, '1': 4},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa2 = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert contains_DFA(alternation_dfa1, alternation_dfa2)
    assert contains_DFA(alternation_dfa2, alternation_dfa1)


def test_DFA_containment_negative():
    # first DFA - even ones
    alphabet = {'0', '1'}
    state_set = {0, 1}
    initial_state = 0
    final_states = {0}
    transition_map = {
        0: {'0': 0, '1': 1},
        1: {'0': 1, '1': 0},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    even_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    # second DFA - alternation
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3}
    initial_state = 0
    final_states = {0, 1, 2}
    transition_map = {
        0: {'0': 1, '1': 2},
        1: {'0': 3, '1': 2},
        2: {'0': 1, '1': 3},
        3: {'0': 3, '1': 3},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert not contains_DFA(even_ones_dfa, alternation_dfa)
    assert not contains_DFA(alternation_dfa, even_ones_dfa)


def test_DFA_containment_positive():
    # first DFA - even ones
    alphabet = {'0', '1'}
    state_set = {0, 1}
    initial_state = 0
    final_states = {0}
    transition_map = {
        0: {'0': 0, '1': 1},
        1: {'0': 1, '1': 0},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    even_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    # second DFA - multiple of four ones
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3}
    initial_state = 0
    final_states = {0}
    transition_map = {
        0: {'0': 0, '1': 1},
        1: {'0': 1, '1': 2},
        2: {'0': 2, '1': 3},
        3: {'0': 3, '1': 0},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert contains_DFA(even_ones_dfa, alternation_dfa)
    assert not contains_DFA(alternation_dfa, even_ones_dfa)