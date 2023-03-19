import logging
import sys
from queue import Queue, Empty
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: server %(levelname)-7s] %(message)s'))
logger.addHandler(handler)


input_queue = Queue()
output_queue = Queue()


def get_next_event():
    while True:
        try:
            event = input_queue.get(block=False)
        except Empty:
            event = None
        return event


def put_event(event: str):
    input_queue.put(event)
    logger.info(f'++       Event: {event}')


def get_next_instruction():
    try:
        instruction = output_queue.get(block=True)
    except Empty:
        instruction = None
    return instruction


def put_instruction(instr: str, value: int = 0):
    output_queue.put((instr, value))
    if value:
        logger.info(f'-- Instruction: {instr}, {value}')
    else:
        logger.info(f'-- Instruction: {instr}')

