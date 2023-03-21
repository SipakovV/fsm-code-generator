from fsm_core import fsm


def generate_fsm_with_button():
    alphabet = {'timeout', 'button1'}
    instructions_set = {'set_timeout', 'p1_red', 'p1_green', 'p1_blinking',
                        't1_red', 't1_yellow_red', 't1_yellow', 't1_green', 't1_blinking'}
    state_set = {'traffic_go', 'traffic_go_ready', 'traffic_go_change', 'traffic_stopping1', 'traffic_stopping2',
                 'p_go', 'p_stopping', 'traffic_ready'}
    initial_state = 'traffic_go'
    initial_instructions = [('set_timeout', 30), 't1_green', 'p1_red']
    final_states = set()
    transition_map = {
        'traffic_go': {'timeout': ('traffic_go_ready', []), 'button1': ('traffic_go_change', [])},
        'traffic_go_ready': {'button1': ('traffic_stopping1', [('set_timeout', 3), 't1_blinking'])},
        'traffic_go_change': {'timeout': ('traffic_stopping1', [('set_timeout', 3), 't1_blinking'])},
        'traffic_stopping1': {'timeout': ('traffic_stopping2', [('set_timeout', 3), 't1_yellow'])},
        'traffic_stopping2': {'timeout': ('p_go', [('set_timeout', 20), 't1_red', 'p1_green'])},
        'p_go': {'timeout': ('p_stopping', [('set_timeout', 3), 'p1_blinking'])},
        'p_stopping': {'timeout': ('traffic_ready', [('set_timeout', 3), 't1_yellow_red', 'p1_red'])},
        'traffic_ready': {'timeout': ('traffic_go', [('set_timeout', 30), 't1_green'])},
    }

    assert (row in state_set for row in transition_map)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    fsm_TL_4way_1button = fsm.FSM(alphabet=alphabet, instructions_set=instructions_set, state_set=state_set,
                                  initial_state=initial_state, initial_instructions=initial_instructions,
                                  final_states=final_states, transition_map=transition_map,
                                  name='fsm_with_button',
                                  title='FSM with button',
                                  description='FSM for testing the buttons')
    print()
    print(fsm_TL_4way_1button)
    fsm_TL_4way_1button.visualize(all_states=True)
    fsm_TL_4way_1button.generate_code_python()


def generate_fsm_without_button():
    alphabet = {'timeout'}
    instructions_set = {'set_timeout',
                        'p1_red', 'p1_green', 'p1_blinking',
                        't1_red', 't1_yellow_red', 't1_yellow', 't1_green', 't1_blinking',
                        'p2_red', 'p2_green', 'p2_blinking',
                        't2_red', 't2_yellow_red', 't2_yellow', 't2_green', 't2_blinking',
                        }
    state_set = {'ns_go', 'ns_stopping', 'ns_stopped',
                 'ew_go', 'ew_stopping', 'ew_stopped'}
    initial_state = 'ns_go'
    initial_instructions = [('set_timeout', 30), 't1_green', 'p1_green', 't2_red', 'p2_red']
    final_states = set()
    transition_map = {
        'ns_go': {'timeout': ('ns_stopping', [('set_timeout', 3), 't1_blinking', 'p1_blinking']), },
        'ns_stopping': {'timeout': ('ns_stopped', [('set_timeout', 3), 't1_yellow', 'p1_red', 't2_yellow_red'])},
        'ns_stopped': {'timeout': ('ew_go', [('set_timeout', 20), 't1_red', 't2_green', 'p2_green'])},
        'ew_go': {'timeout': ('ew_stopping', [('set_timeout', 3), 't2_blinking', 'p2_blinking'])},
        'ew_stopping': {'timeout': ('ew_stopped', [('set_timeout', 3), 't1_yellow_red', 't2_yellow', 'p2_red'])},
        'ew_stopped': {'timeout': ('ns_go', [('set_timeout', 30), 't1_green', 'p1_green', 't2_red'])},
    }

    assert (row in state_set for row in transition_map)
    assert initial_state in state_set
    assert final_states.issubset(state_set)

    test_FSM_TL_4way_p_and_t = fsm.FSM(alphabet=alphabet, instructions_set=instructions_set, state_set=state_set,
                                       initial_state=initial_state, initial_instructions=initial_instructions,
                                       final_states=final_states, transition_map=transition_map,
                                       name='fsm_without_button',
                                       title='FSM without button',
                                       description='FSM for testing the timeouts')
    print()
    print(test_FSM_TL_4way_p_and_t)
    test_FSM_TL_4way_p_and_t.visualize(all_states=True)
    test_FSM_TL_4way_p_and_t.generate_code_python()


if __name__ == '__main__':
    generate_fsm_with_button()
    generate_fsm_without_button()
