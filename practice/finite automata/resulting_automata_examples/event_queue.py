import logging
import sys
from queue import Queue, Empty
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


input_queue = Queue()
output_queue = Queue()


#def log(string: str):
#    logger.info(string)
    #print(f'{datetime.now()}: {string}')


def get_next_event():
    #global timeout
    while True:
        try:
            event = input_queue.get(block=False)
        except Empty:
            event = None
        '''if not event:
            if timeout:
                if datetime.now() >= timeout:
                    timeout = None
                    return 'timeout'
            time.sleep(0.001)
        else:'''
        return event


def publish_event(event: str):
    input_queue.put(event)
    logger.info(f'++ Event: {event}')


def get_instruction():
    try:
        instruction = output_queue.get(block=False)
    except Empty:
        instruction = None
    return instruction


def publish_instruction(instr: str, value: int = 0):
    output_queue.put((instr, value))
    if value:
        logger.info(f'++ Instruction: {instr}, {value}')
    else:
        logger.info(f'++ Instruction: {instr}')

