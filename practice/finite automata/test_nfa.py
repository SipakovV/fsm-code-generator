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

    assert all(char in alphabet for char in entry)

    chessboard_3x3_nfa = NFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert chessboard_3x3_nfa.parse(entry) == accepts


@pytest.mark.parametrize(
    argnames="entry, accepts",
    argvalues=[
        # Entry:          Accepts:
        ('',              False),
        ('1',             True),
        ('11',            False),
        ('111',           True),
        ('1111',          False),
        ('11111',         False),
        ('10',            False),
        ('10010',         False),
        ('0',             True),
        ('00',            False),
        ('000',           True),
        ('0000',          False),
        ('0001',          False),
        ('01',            True),
        ('0110',          False),
        ('0011',          False),
])
def test_eps_NFA_example(entry, accepts):
    alphabet = {'0', '1'}
    state_set = {'A', 'B', 'C', 'D', 'E', 'F'}
    initial_state = 'A'
    final_states = {'D'}
    transition_map = {
        'HEADER':   ('0', '1', 'epsilon'),
        'A':        ({'E'},  {'B'},  set()),
        'B':        (set(),  {'C'},  {'D'}),
        'C':        (set(),  {'D'},  set()),
        'D':        (set(),  set(),  set()),
        'E':        ({'F'},  set(),  {'B', 'C'}),
        'F':        ({'D'},  set(),  set()),
    }

    assert all(char in alphabet for char in entry)

    example_epsilon_nfa = NFA(alphabet, state_set, initial_state, final_states, transition_map, epsilon_mode=True)
    print()
    print(example_epsilon_nfa)

    alphabet = {'0', '1'}
    state_set = {'A', 'B', 'C', 'D', 'E', 'F'}
    initial_state = 'A'
    final_states = {'B', 'D', 'E'}
    transition_map = {
        'HEADER': ('0', '1'),
        'A': ({'E'}, {'B'}),
        'B': (set(), {'C'}),
        'C': (set(), {'D'}),
        'D': (set(), set()),
        'E': ({'F'}, {'C', 'D'}),
        'F': ({'D'}, set()),
    }

    example_non_epsilon_nfa = NFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert example_epsilon_nfa == example_non_epsilon_nfa

    assert example_non_epsilon_nfa.parse(entry) == accepts

    assert example_epsilon_nfa.parse(entry) == accepts

