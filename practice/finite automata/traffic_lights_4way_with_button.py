import sys
#from enum import Enum
import logging

import event_queue


#state_set = {'traffic_go', 'traffic_go_ready', 'traffic_go_change', 'traffic_stopping1',
#             'traffic_stopping2', 'p_go', 'p'}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s| %(name)-40s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


#states = Enum()
alphabet = {'timeout', 'button'}
#alphabet = Enum()
initial_state = 'traffic_go'


def traffic_red():
    event_queue.put_instruction('t1_red')


def traffic_yellow_red():
    event_queue.put_instruction('t1_yellow_red')


def traffic_yellow():
    event_queue.put_instruction('t1_yellow')


def traffic_green():
    event_queue.put_instruction('t1_green')


def traffic_blinking():
    event_queue.put_instruction('t1_blinking')


def p_red():
    event_queue.put_instruction('p1_red')


def p1_blinking():
    event_queue.put_instruction('p1_blinking')


def p1_green():
    event_queue.put_instruction('p1_green')


def set_timeout(timeout_seconds: int):
    #global timeout
    #timeout = datetime.now() + timedelta(seconds=timeout_seconds)
    event_queue.put_instruction('set_timeout', timeout_seconds)


def run_fsm():
    state = initial_state
    logger.info(f'== FSM started')
    logger.info(f'==\t\tState: {state}')
    traffic_green()
    p_red()
    set_timeout(30)

    while True:
        event = event_queue.get_next_event()

        old_state = state

        if state == 'traffic_go':
            if event == 'timeout':
                state = 'traffic_go_ready'
            if event == 'button1':
                state = 'traffic_go_change'

        elif state == 'traffic_go_ready':
            if event == 'button1':
                set_timeout(3)
                traffic_blinking()
                state = 'traffic_stopping1'

        elif state == 'traffic_go_change':
            if event == 'timeout':
                set_timeout(3)
                traffic_blinking()
                state = 'traffic_stopping1'

        elif state == 'traffic_stopping1':
            if event == 'timeout':
                set_timeout(3)
                traffic_yellow()
                state = 'traffic_stopping2'

        elif state == 'traffic_stopping2':
            if event == 'timeout':
                set_timeout(20)
                traffic_red()
                p1_green()
                state = 'p_go'

        elif state == 'p_go':
            if event == 'timeout':
                set_timeout(3)
                p1_blinking()
                state = 'p_stopping'

        elif state == 'p_stopping':
            if event == 'timeout':
                set_timeout(3)
                traffic_yellow_red()
                p_red()
                state = 'traffic_ready'

        elif state == 'traffic_ready':
            if event == 'timeout':
                set_timeout(30)
                traffic_green()
                state = 'traffic_go'

        if event and state != old_state:
            logger.info(f'== State change: {old_state} -{event}-> {state}')


if __name__ == '__main__':
    run_fsm()
