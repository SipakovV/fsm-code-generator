import pytest

from dfa import DFA


@pytest.mark.parametrize(
    argnames="entry, accepts",
    argvalues=[
        # Entry:          Accepts:
        ('',              False),
        ('0',             False),
        ('1',             False),
        ('00',            False),
        ('01',            False),
        ('10',            False),
        ('11',            False),
        ('111',           True),
        ('11011',         False),
        ('11100001',      True),
        ('0110111',       True),
        ('0110110',       False),
        ('0000000',       False),
])
def test_triple_ones_dfa(entry, accepts):
    alphabet = {'0', '1'}
    state_set = {0, 1, 2, 3}
    initial_state = 0
    final_states = {3}
    transition_map = {
        0: {'0': 0, '1': 1},
        1: {'0': 0, '1': 2},
        2: {'0': 0, '1': 3},
        3: {'0': 3, '1': 3},
    }

    assert len(transition_map) == len(state_set)
    assert (row in state_set for row in transition_map)
    assert (all(len(alphabet) == len(row) for row in transition_map.values()))

    assert initial_state in state_set
    assert final_states.issubset(state_set)

    #print('generating dfa')

    dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    #self.dfa_copy = DFA(dfa_set=(self.dfa,))

    # assert triple_ones_dfa_copy.parse(entry) == accepts
    assert all(char in dfa.alphabet for char in entry)
    assert dfa.parse(entry) == accepts
    #assert self.dfa_copy.parse(entry) == accepts


@pytest.mark.parametrize(
    argnames="entry, accepts",
    argvalues=[
        # Entry:          Accepts:
        ('',              True),
        ('0',             True),
        ('1',             False),
        ('00',            True),
        ('01',            False),
        ('10',            False),
        ('11',            True),
        ('111',           False),
        ('11011',         True),
        ('11100001',      True),
        ('0110111',       False),
        ('0110110',       True),
        ('0000000',       True),
        ('1111111',       False),
])
def test_DFA_even_ones(entry, accepts):
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    even_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert even_ones_dfa.parse(entry) == accepts


@pytest.mark.parametrize(
    argnames="entry, accepts",
    argvalues=[
        # Entry:          Accepts:
        ('',              True),
        ('0',             True),
        ('1',             True),
        ('00',            False),
        ('01',            True),
        ('10',            True),
        ('010',           True),
        ('101',           True),
        ('1010',          True),
        ('11',            False),
        ('111',           False),
        ('11011',         False),
        ('11100001',      False),
        ('0110111',       False),
        ('010101010',     True),
        ('0000000',       False),
        ('1111111',       False),
])
def test_DFA_alternation(entry, accepts):
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    triple_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert triple_ones_dfa.parse(entry) == accepts


@pytest.mark.parametrize(
    argnames="entry, action, accepts",
    argvalues=[
        # Entry:          Action:   Accepts:
        ('',              'and',     True),
        ('0',             'and',     True),
        ('1',             'and',     False),
        ('00',            'and',     False),
        ('01',            'and',     False),
        ('10',            'and',     False),
        ('010',           'and',     False),
        ('101',           'and',     True),
        ('1010',          'and',     True),
        ('11',            'and',     False),
        ('111',           'and',     False),
        ('11011',         'and',     False),
        ('11100001',      'and',     False),
        ('0110111',       'and',     False),
        ('010101010',     'and',     True),
        ('0000000',       'and',     False),
        ('110110101',     'and',     False),
        ('0101010',       'and',     False),
        ('1111111',       'and',     False),

        ('',              'or',      True),
        ('0',             'or',      True),
        ('1',             'or',      True),
        ('00',            'or',      True),
        ('01',            'or',      True),
        ('10',            'or',      True),
        ('010',           'or',      True),
        ('101',           'or',      True),
        ('1010',          'or',      True),
        ('11',            'or',      True),
        ('111',           'or',      False),
        ('11011',         'or',      True),
        ('11100001',      'or',      True),
        ('0110111',       'or',      False),
        ('010101010',     'or',      True),
        ('0000000',       'or',      True),
        ('110110101',     'or',      True),
        ('0101010',       'or',      True),
        ('1111111',       'or',      False),

        ('',              'xor',     False),
        ('0',             'xor',     False),
        ('1',             'xor',     True),
        ('00',            'xor',     True),
        ('01',            'xor',     True),
        ('10',            'xor',     True),
        ('010',           'xor',     True),
        ('101',           'xor',     False),
        ('1010',          'xor',     False),
        ('11',            'xor',     True),
        ('111',           'xor',     False),
        ('11011',         'xor',     True),
        ('11100001',      'xor',     True),
        ('0110111',       'xor',     False),
        ('010101010',     'xor',     False),
        ('0000000',       'xor',     True),
        ('110110101',     'xor',     True),
        ('0101010',       'xor',     True),
        ('1111111',       'xor',     False),
])
def test_DFA_even_ones_and_or_xor_alternation(entry, action, accepts):
    # first DFA
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    even_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    #assert even_ones_dfa.parse(entry) == accepts

    # second DFA
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    #assert alternation_dfa.parse(entry) == accepts

    combined_dfa = DFA(dfa_set=(even_ones_dfa, alternation_dfa), action=action)

    #print()
    #print(combined_dfa)

    assert combined_dfa.parse(entry) == accepts

@pytest.mark.parametrize(
    argnames="entry, action, accepts",
    argvalues=[
        # Entry:          Action:   Accepts:
        ('',              'and not', False),
        ('0',             'and not', False),
        ('1',             'and not', False),
        ('00',            'and not', True),
        ('01',            'and not', False),
        ('10',            'and not', False),
        ('010',           'and not', False),
        ('101',           'and not', False),
        ('1010',          'and not', False),
        ('11',            'and not', True),
        ('111',           'and not', False),
        ('11011',         'and not', True),
        ('11100001',      'and not', True),
        ('0110111',       'and not', False),
        ('010101010',     'and not', False),
        ('0000000',       'and not', True),
        ('110110101',     'and not', True),
        ('0101010',       'and not', False),
        ('1111111',       'and not', False),
])
def test_DFA_even_ones_and_not_alternation(entry, action, accepts):
    # first DFA
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    even_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    #assert even_ones_dfa.parse(entry) == accepts

    # second DFA
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    #assert alternation_dfa.parse(entry) == accepts

    combined_dfa = DFA(dfa_set=(even_ones_dfa, alternation_dfa), action=action)

    #print()
    #print(combined_dfa)

    assert combined_dfa.parse(entry) == accepts


@pytest.mark.parametrize(
    argnames="entry, action, accepts",
    argvalues=[
        # Entry:          Action:   Accepts:
        ('',              'and not', False),
        ('0',             'and not', False),
        ('1',             'and not', True),
        ('00',            'and not', False),
        ('01',            'and not', True),
        ('10',            'and not', True),
        ('010',           'and not', True),
        ('101',           'and not', False),
        ('1010',          'and not', False),
        ('11',            'and not', False),
        ('111',           'and not', False),
        ('11011',         'and not', False),
        ('11100001',      'and not', False),
        ('0110111',       'and not', False),
        ('010101010',     'and not', False),
        ('0000000',       'and not', False),
        ('110110101',     'and not', False),
        ('0101010',       'and not', True),
        ('1111111',       'and not', False),
])
def test_DFA_alternation_and_not_even_ones(entry, action, accepts):
    # first DFA
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    even_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    #assert even_ones_dfa.parse(entry) == accepts

    # second DFA
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    alternation_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    #assert alternation_dfa.parse(entry) == accepts

    combined_dfa = DFA(dfa_set=(alternation_dfa, even_ones_dfa), action=action)

    #print()
    #print(combined_dfa)

    assert combined_dfa.parse(entry) == accepts

'''
@pytest.mark.parametrize(
    argnames="entry, accepts",
    argvalues=[
        # Entry:          Accepts:
        ('',              True),
        ('0',             True),
        ('1',             False),
        ('00',            True),
        ('01',            False),
        ('10',            False),
        ('11',            True),
        ('111',           False),
        ('11011',         True),
        ('11100001',      True),
        ('0110111',       False),
        ('0110110',       True),
        ('0000000',       True),
        ('1111111',       False),
])
def test_DFA_equivalence(entry, accepts):
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
    assert all(char in alphabet for char in entry)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    triple_ones_dfa = DFA(alphabet, state_set, initial_state, final_states, transition_map)

    assert triple_ones_dfa.parse(entry) == accepts
'''