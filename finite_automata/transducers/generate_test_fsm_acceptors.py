from fsm_core.acceptor_fsm import AcceptorFSM


def generate_fsm_even_ones():
    alphabet = {'0', '1'}
    state_set = {'0', '1'}
    initial_state = '0'
    final_states = {'0'}
    transition_map = {
        '0': {'0': '0', '1': '1'},
        '1': {'0': '1', '1': '0'},
    }

    even_ones_fsm = AcceptorFSM(alphabet=alphabet,
                                state_set=state_set,
                                initial_state=initial_state,
                                final_states=final_states,
                                transition_map=transition_map,
                                name='even_ones_fsm',
                                title='Even ones FSM',
                                description='FSM that accepts strings with even ones only')

    assert (row in state_set for row in transition_map)
    assert initial_state in state_set

    print()
    print(even_ones_fsm)
    even_ones_fsm.visualize()
    even_ones_fsm.generate_code_python()


if __name__ == '__main__':
    generate_fsm_even_ones()
