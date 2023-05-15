import logging
import socket
import sys
import traceback
from threading import Thread
from _thread import interrupt_main
from time import sleep
import json


SERVER_ADDRESS = ("127.0.0.1", 12345)
MAX_BUFFER_SIZE = 4096


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s| %(name)-40s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


def instruction_listening_thread(soc):
    while True:
        try:
            instruction_list = get_instruction_from_server(soc)
            logger.debug(f'Instruction received: {instruction_list}')
        except ConnectionResetError:
            logger.info('Server closed')
            interrupt_main()
        except:
            logger.error('Error while getting data from server')
            traceback.print_exc()
            interrupt_main()
        process_instruction(instruction_list)


def send_event(event, sock):
    event_dict = {
        'event': event,
    }
    event_json = json.dumps(event_dict)
    sock.send(bytes(event_json, encoding='utf-8'))


def get_instruction_from_server(sock):
    instruction_json = sock.recv(MAX_BUFFER_SIZE)
    obj_list = [d.strip() for d in instruction_json.splitlines()]
    instr_list = []
    for d in obj_list:
        instr_list.append(json.loads(d))
        logger.debug(d)
    return instr_list


def process_instruction(instr_list):
    for instr in instr_list:
        if instr[1]:
            print('>', instr[0], instr[1])
        else:
            print('>', instr[0])


def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected:
        try:
            sock.connect(SERVER_ADDRESS)
            connected = True
            logger.info('Connected to server')
        except KeyboardInterrupt:
            logger.info('Client closed')
            exit(0)
        except ConnectionRefusedError:
            logger.info('Connecting...')
            sleep(1)

    try:
        Thread(target=instruction_listening_thread, args=(sock,), daemon=True).start()
    except Exception:
        logger.error("Error while starting listening thread")
        traceback.print_exc()

    while True:
        event = input()

        send_event(event, sock)


if __name__ == '__main__':
    start_client()
