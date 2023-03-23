from fsm_core import fsm


def generate_fsm_with_button():
    alphabet = {'timeout', 'button1'}
    instructions_set = {'timer_set', 'p1_red', 'p1_green', 'p1_blinking',
                        't1_red', 't1_yellow_red', 't1_yellow', 't1_green', 't1_blinking'}
    state_set = {'traffic_go', 'traffic_go_ready', 'traffic_go_change', 'traffic_stopping1', 'traffic_stopping2',
                 'p_go', 'p_stopping', 'traffic_ready'}
    initial_state = 'traffic_go'
    initial_instructions = [('timer_set', 30), 't1_green', 'p1_red']
    transition_map = {
        'traffic_go': {'timeout': ('traffic_go_ready', []), 'button1': ('traffic_go_change', [])},
        'traffic_go_ready': {'button1': ('traffic_stopping1', [('timer_set', 3), 't1_blinking'])},
        'traffic_go_change': {'timeout': ('traffic_stopping1', [('timer_set', 3), 't1_blinking'])},
        'traffic_stopping1': {'timeout': ('traffic_stopping2', [('timer_set', 3), 't1_yellow'])},
        'traffic_stopping2': {'timeout': ('p_go', [('timer_set', 20), 't1_red', 'p1_green'])},
        'p_go': {'timeout': ('p_stopping', [('timer_set', 3), 'p1_blinking'])},
        'p_stopping': {'timeout': ('traffic_ready', [('timer_set', 3), 't1_yellow_red', 'p1_red'])},
        'traffic_ready': {'timeout': ('traffic_go', [('timer_set', 30), 't1_green'])},
    }

    assert (row in state_set for row in transition_map)
    assert initial_state in state_set

    fsm_TL_4way_1button = fsm.FSM(alphabet=alphabet, instructions_set=instructions_set, state_set=state_set,
                                  initial_state=initial_state, initial_instructions=initial_instructions, transition_map=transition_map,
                                  name='fsm_with_button',
                                  title='FSM with button',
                                  description='FSM for testing the buttons')
    print()
    print(fsm_TL_4way_1button)
    fsm_TL_4way_1button.visualize(all_states=True)
    fsm_TL_4way_1button.generate_code_python()


def generate_fsm_without_button():
    alphabet = {'timeout'}
    instructions_set = {'timer_set',
                        'p1_red', 'p1_green', 'p1_blinking',
                        't1_red', 't1_yellow_red', 't1_yellow', 't1_green', 't1_blinking',
                        'p2_red', 'p2_green', 'p2_blinking',
                        't2_red', 't2_yellow_red', 't2_yellow', 't2_green', 't2_blinking',
                        }
    state_set = {'ns_go', 'ns_stopping', 'ns_stopped',
                 'ew_go', 'ew_stopping', 'ew_stopped'}
    initial_state = 'ns_go'
    initial_instructions = [('timer_set', 30), 't1_green', 'p1_green', 't2_red', 'p2_red']
    transition_map = {
        'ns_go': {'timeout': ('ns_stopping', [('timer_set', 3), 't1_blinking', 'p1_blinking']), },
        'ns_stopping': {'timeout': ('ns_stopped', [('timer_set', 3), 't1_yellow', 'p1_red', 't2_yellow_red'])},
        'ns_stopped': {'timeout': ('ew_go', [('timer_set', 20), 't1_red', 't2_green', 'p2_green'])},
        'ew_go': {'timeout': ('ew_stopping', [('timer_set', 3), 't2_blinking', 'p2_blinking'])},
        'ew_stopping': {'timeout': ('ew_stopped', [('timer_set', 3), 't1_yellow_red', 't2_yellow', 'p2_red'])},
        'ew_stopped': {'timeout': ('ns_go', [('timer_set', 30), 't1_green', 'p1_green', 't2_red'])},
    }

    assert (row in state_set for row in transition_map)
    assert initial_state in state_set

    test_FSM_TL_4way_p_and_t = fsm.FSM(alphabet=alphabet, instructions_set=instructions_set, state_set=state_set,
                                       initial_state=initial_state, initial_instructions=initial_instructions,
                                       transition_map=transition_map,
                                       name='fsm_without_button',
                                       title='FSM without button',
                                       description='FSM for testing the timeouts')
    print()
    print(test_FSM_TL_4way_p_and_t)
    test_FSM_TL_4way_p_and_t.visualize(all_states=True)
    test_FSM_TL_4way_p_and_t.generate_code_python()


def generate_fsm_microwave():
    alphabet = {'timeout', 'door_open', 'door_close', 'button_run', 'button_reset'}
    instructions_set = {'timer_set', 'timer_add',
                        'timer_pause', 'timer_resume',
                        'power_on', 'power_off',
                        'lamp_on', 'lamp_off',
                        'beeping_on', 'beeping_off'}
    state_set = {'door_closed', 'door_open',
                 'cooking', 'cooking_completed', 'cooking_interrupted'}
    initial_state = 'door_closed'
    initial_instructions = ['power_off', 'lamp_off', 'beeping_off']
    transition_map = {
        'door_closed': {
            'door_open': ('door_open', ['lamp_on']),
            'button_run': ('cooking', [('timer_set', 30), 'lamp_on', 'power_on'])},
        'door_open': {
            'door_close': ('door_closed', ['lamp_off'])},
        'cooking': {
            'button_reset': ('door_closed', [('timer_set', 0), 'lamp_off', 'power_off']),
            'button_run': ('cooking', [('timer_add', 30)]),
            'door_open': ('cooking_interrupted', ['timer_pause', 'power_off']),
            'timeout': ('cooking_completed', ['power_off', 'beeping_on'])},
        'cooking_interrupted': {
            'door_close': ('cooking', ['timer_resume', 'lamp_off'])},
        'cooking_completed': {
            'door_open': ('door_open', ['beeping_off']),
            'button_reset': ('door_closed', ['lamp_off', 'beeping_off'])},
    }

    assert (row in state_set for row in transition_map)
    assert initial_state in state_set

    microwave_fsm = fsm.FSM(alphabet=alphabet, instructions_set=instructions_set, state_set=state_set,
                                       initial_state=initial_state, initial_instructions=initial_instructions,
                                       transition_map=transition_map,
                                       name='microwave_fsm',
                                       title='FSM for microwave',
                                       description='FSM for testing the microwave widgets')
    print()
    print(microwave_fsm)
    microwave_fsm.visualize(all_states=True)
    microwave_fsm.generate_code_python()


if __name__ == '__main__':
    generate_fsm_microwave()
    generate_fsm_with_button()
    generate_fsm_without_button()
