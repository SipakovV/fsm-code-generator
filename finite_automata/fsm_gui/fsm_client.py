# client.py
import logging
import socket
import sys
import traceback
from threading import Thread
from _thread import interrupt_main
from time import sleep
import json

from fsm_gui import App, GuiThread

SERVER_ADDRESS = ("127.0.0.1", 12345)
MAX_BUFFER_SIZE = 4096


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s| %(name)-40s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


def instruction_listening_thread(soc, gui):  # поток, обрабатывающий пакеты с сервера
    while True:
        try:
            instruction_dict = get_instruction_from_server(soc)
            logger.debug(f'instruction received: {instruction_dict}')
        except ConnectionResetError:
            logger.info('Server closed')
            interrupt_main()
        except:
            logger.error('Error while getting data from server')
            traceback.print_exc()
            interrupt_main()
        try:
            gui.execute_instruction(instruction_dict)
        except:
            logger.error('Error while data output to gui')
            traceback.print_exc()
            interrupt_main()


def send_event(event, soc):  # отправка запроса серверу
    event_dict = {
        'event': event,
    }
    event_json = json.dumps(event_dict)
    soc.send(bytes(event_json, encoding='utf-8'))


def get_instruction_from_server(soc):  # принятие пакета от сервера
    instruction_json = soc.recv(MAX_BUFFER_SIZE)
    logger.debug(instruction_json)
    instruction_dict = json.loads(instruction_json)
    return instruction_dict


def start_client():  # запуск программы
    try:
        gui = GuiThread(daemon=True)
        gui.start()
    except:
        logger.error("Error while starting GUI thread")
        traceback.print_exc()

    sleep(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected:
        if not gui.is_alive():
            logger.info('Client closed')
            exit(0)
        try:
            sock.connect(SERVER_ADDRESS)
            connected = True
            config = {
                'title': 'test',
                'description': 'bla bla bla FSM bla bla\nbla bla'
            }
            gui.activate(config)
            logger.info('Connected to server')
        except KeyboardInterrupt:
            logger.info('Client closed')
            exit(0)
        except ConnectionRefusedError:
            logger.info('Connecting...')
            sleep(1)

    try:
        Thread(target=instruction_listening_thread, args=(sock, gui), daemon=True).start()
    except:
        logger.error("Error while starting listening thread")
        traceback.print_exc()

    while True:
        event = gui.get_event()
        if event:
            logger.debug('event: ' + event)
            send_event(event, sock)

        sleep(0.01)
        if not gui.is_alive():
            break


if __name__ == '__main__':
    start_client()
