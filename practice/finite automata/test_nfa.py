import pytest

from nfa import NFA


@pytest.mark.parametrize(
    argnames="entry, accepts",
    argvalues=[
        # Entry:          Accepts:
        ('',              False),
        ('r',             False),
        ('b',             False),
        ('bb',            True),
        ('brb',           True),
        ('rb',            False),
        ('rbbr',          False),
        ('bbb',           False),
        ('bbbb',          True),
        ('bbbbb',         False),
        ('bbrb',          True),
        ('bbrbb',         True),
        ('brbbb',         True),
        ('brbb',          True),
        ('brbbbbb',       True),
        ('rr',            False),
        ('rrrrb',         True),
])
def test_NFA_3x3_chessboard(entry, accepts):
    alphabet = {'r', 'b'}
    state_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    initial_state = 1
    final_states = {9}
    transition_map = {
        'HEADER': ('r', 'b'),
        1: ({2, 4},         {5}),
        2: ({4, 6},         {1, 3, 5}),
        3: ({2, 6},         {5}),
        4: ({2, 8},         {1, 5, 7}),
        5: ({2, 4, 6, 8},   {1, 3, 7, 9}),
        6: ({2, 8},         {3, 5, 9}),
        7: ({4, 8},         {5}),
        8: ({4, 6},         {5, 7, 9}),
        9: ({6, 8},         {5}),
    }

    assert len(transition_map) == len(state_set) + 1
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))
    assert set(transition_map['HEADER']) == alphabet
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    chessboard_3x3_nfa = NFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert chessboard_3x3_nfa.parse(entry) == accepts
