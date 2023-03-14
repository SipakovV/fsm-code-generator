import pytest

from fsm import FSM


def test_FSM_TL_4way_1button():
    alphabet = {'timeout', 'button1'}
    instructions_set = {'set_timeout', 'p1_red', 'p1_green', 'p1_blinking',
                        't1_red', 't1_red_yellow', 't1_yellow', 't1_green', 't1_blinking'}
    state_set = {'traffic_go', 'traffic_go_ready', 'traffic_go_change', 'traffic_stopping1', 'traffic_stopping2',
                 'p_go', 'p_stopping', 'traffic_ready'}
    initial_state = 'traffic_go'
    initial_instructions = [('set_timeout', 30), 't1_green', 'p1_red']
    final_states = set()
    transition_map = {
        'traffic_go':           {'timeout': ('traffic_go_ready',    []), 'button1': ('traffic_go_change', [])},
        'traffic_go_ready':     {'button1': ('traffic_stopping1',   [('set_timeout', 3), 't1_blinking'])},
        'traffic_go_change':    {'timeout': ('traffic_stopping1',   [('set_timeout', 3), 't1_blinking'])},
        'traffic_stopping1':    {'timeout': ('traffic_stopping2',   [('set_timeout', 3), 't1_yellow'])},
        'traffic_stopping2':    {'timeout': ('p_go',                [('set_timeout', 20), 't1_red', 'p1_green'])},
        'p_go':                 {'timeout': ('p_stopping',          [('set_timeout', 3), 'p1_blinking'])},
        'p_stopping':           {'timeout': ('traffic_ready',       [('set_timeout', 3), 't1_yellow_red', 'p1_red'])},
        'traffic_ready':        {'timeout': ('traffic_go',          [('set_timeout', 30), 't1_green'])},
    }

    assert (row in state_set for row in transition_map)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    fsm_TL_4way_1button = FSM(alphabet=alphabet, instructions_set=instructions_set, state_set=state_set,
                              initial_state=initial_state, initial_instructions=initial_instructions,
                              final_states=final_states, transition_map=transition_map,
                              name='fsm_TL_4way_1button')
    print()
    print(fsm_TL_4way_1button)
    #fsm_TL_4way_1button.visualize()
    fsm_TL_4way_1button.generate_code_python('fsm_tl_4way_1btn.py')
    #assert triple_ones_dfa.parse(entry) == accepts
