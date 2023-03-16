import time as tm
from queue import Queue, Empty
from enum import Enum
from datetime import datetime, timedelta


state_set = {'NS_go', 'NS_stopping', 'NS_stopped', 'EW_go', 'EW_stopping', 'EW_stopped'}
#states = Enum()
alphabet = {'timeout'}
#alphabet = Enum()
initial_state = 'NS_go'

queue = Queue()
timeout = None
state = initial_state


def ns_green():
    print(f'{datetime.now()}: ns_green')


def ew_green():
    print(f'{datetime.now()}: ew_green')


def ns_blinking():
    print(f'{datetime.now()}: ns_blinking')


def ew_blinking():
    print(f'{datetime.now()}: ew_blinking')


def ns_yellow():
    print(f'{datetime.now()}: ns_yellow')


def ew_yellow():
    print(f'{datetime.now()}: ew_yellow')


def ns_red():
    print(f'{datetime.now()}: ns_red')


def ew_red():
    print(f'{datetime.now()}: ew_red')


def ns_yellow_red():
    print(f'{datetime.now()}: ns_yellow_red')


def ew_yellow_red():
    print(f'{datetime.now()}: ew_yellow_red')


def get_next_event():
    global timeout
    #print('sefsef')
    while True:
        try:
            event = queue.get(block=False)
        except Empty:
            event = None
        #print(event)
        if not event:
            if timeout:
                if datetime.now() >= timeout:
                    timeout = None
                    return 'timeout'
            tm.sleep(0.001)
        else:
            #print('returned event', event)
            return event


def set_timeout(timeout_seconds: float):
    global timeout
    timeout = datetime.now() + timedelta(seconds=timeout_seconds)


if __name__ == '__main__':

    ew_red()
    ns_green()
    set_timeout(10)

    while True:
        event = get_next_event()

        if state == 'NS_go':
            if event == 'timeout':
                set_timeout(2)
                ns_blinking()
                state = 'NS_stopping'

        elif state == 'NS_stopping':
            if event == 'timeout':
                set_timeout(2)
                ns_yellow()
                ew_yellow_red()
                state = 'NS_stopped'

        elif state == 'NS_stopped':
            if event == 'timeout':
                set_timeout(10)
                ns_red()
                ew_green()
                state = 'EW_go'

        elif state == 'EW_go':
            if event == 'timeout':
                set_timeout(2)
                ew_blinking()
                state = 'EW_stopping'

        elif state == 'EW_stopping':
            if event == 'timeout':
                set_timeout(2)
                ew_yellow()
                ns_yellow_red()
                state = 'EW_stopped'

        elif state == 'EW_stopped':
            if event == 'timeout':
                set_timeout(10)
                ew_red()
                ns_green()
                state = 'NS_go'
