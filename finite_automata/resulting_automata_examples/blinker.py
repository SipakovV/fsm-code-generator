import time as tm
from queue import Queue, Empty
from enum import Enum
from datetime import datetime, timedelta


state_set = {'off', 'on'}
#states = Enum()
alphabet = {'timeout'}
#alphabet = Enum()
initial_state = 'off'

queue = Queue()
timeout = None
state = initial_state


def turn_on():
    print('on')


def turn_off():
    print('off')


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

    turn_off()
    set_timeout(1)

    while True:
        event = get_next_event()

        if state == 'off':
            if event == 'timeout':
                turn_on()
                set_timeout(0.3)
                state = 'on'
                continue

        if state == 'on':
            if event == 'timeout':
                turn_off()
                set_timeout(1)
                state = 'off'
                continue
