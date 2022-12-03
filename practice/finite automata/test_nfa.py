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
class TestDFATripleOnes:
    @pytest.fixture(autouse=True)
    def _setup(self):
        alphabet = {'r', 'b'}
        state_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        initial_state = 1
        final_states = {9}
        transition_map = {
            'HEADER': ('r', 'b'),
            1: {'r': {2, 4},        'b': {5}},
            2: {'r': {4, 6},        'b': {1, 3, 5}},
            3: {'r': {2, 6},        'b': {5}},
            4: {'r': {2, 8},        'b': {1, 5, 7}},
            5: {'r': {2, 4, 6, 8},  'b': {1, 3, 7, 9}},
            6: {'r': {2, 8},        'b': {3, 5, 9}},
            7: {'r': {4, 8},        'b': {5}},
            8: {'r': {4, 6},        'b': {5, 7, 9}},
            9: {'r': {6, 8},        'b': {5}},
        }

        self.nfa = NFA(alphabet, state_set, initial_state, final_states, transition_map)

    def test_NFA_3x3_chessboard(self, entry, accepts):
        assert all(char in self.nfa.alphabet for char in entry)
        assert self.nfa.parse(entry) == accepts

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
class TestEpsilonNFA:
    @pytest.fixture(autouse=True)
    def _setup(self):
        alphabet = {'0', '1'}
        state_set = {'A', 'B', 'C', 'D', 'E', 'F'}
        initial_state = 'A'
        final_states = {'D'}
        transition_map = {
            'HEADER': ('0', '1', 'EPS'),
            'A': {'0': {'E'}, '1': {'B'}},
            'B': {'1': {'C'}, 'EPS': {'D'}},
            'C': {'1': {'D'}},
            'D': {},
            'E': {'0': {'F'}, 'EPS': {'B', 'C'}},
            'F': {'0': {'D'}},
        }

        self.epsilon_nfa = NFA(alphabet, state_set, initial_state, final_states, transition_map, epsilon_mode=True)
        # print()
        # print(example_epsilon_nfa)

        alphabet = {'0', '1'}
        state_set = {'A', 'B', 'C', 'D', 'E', 'F'}
        initial_state = 'A'
        final_states = {'B', 'D', 'E'}
        transition_map = {
            'HEADER': ('0', '1'),
            'A': {'0': {'E'}, '1': {'B'}},
            'B': {'1': {'C'}},
            'C': {'1': {'D'}},
            'D': {},
            'E': {'0': {'F'}, '1': {'C', 'D'}},
            'F': {'0': {'D'}},
        }

        self.non_epsilon_nfa = NFA(alphabet, state_set, initial_state, final_states, transition_map)

        assert self.epsilon_nfa == self.non_epsilon_nfa

    def test_eps_NFA_example(self, entry, accepts):
        assert all(char in self.epsilon_nfa.alphabet for char in entry)
        assert self.non_epsilon_nfa.parse(entry) == accepts
        assert self.epsilon_nfa.parse(entry) == accepts

