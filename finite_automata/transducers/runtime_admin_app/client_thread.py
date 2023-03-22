import json
import traceback
from json.decoder import JSONDecodeError
import logging
from threading import Thread, Event
import time


MAX_BUFFER_SIZE = 4096

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: client %(levelname)-7s] %(message)s'))
logger.addHandler(handler)


def get_instruction_from_server(sock):
    instruction_json = sock.recv(MAX_BUFFER_SIZE)
    # TODO: split multiple jsons received (or handle otherwise)

    #dict_list = [d.strip() for d in instruction_json.splitlines()]
    #for d in dict_list:
    instruction = json.loads(instruction_json)
    logger.debug(instruction)
    return instruction


def connecting_thread(sock, gui):
    for _ in range(3):
        try:
            sock.connect(SERVER_ADDRESS)
        except ConnectionRefusedError:
            logger.info('Connecting...')
            time.sleep(0.01)
        else:
            gui.activate()
            break
    else:
        logger.error('Couldn\'t connect to server')
        gui.reset()


class ClientThread(Thread):
    def __init__(self, parent, socket):
        Thread.__init__(self)
        self.parent = parent
        self.sock = socket

    def run(self):
        while True:
            try:
                instruction = get_instruction_from_server(sock)
            except (ConnectionResetError, ConnectionAbortedError) as exc:
                logger.info('Server closed')
                gui.reset()
                break
            except JSONDecodeError as exc:
                traceback.print_exc()
                continue
            except:
                logger.error('Error while getting data from server')
                traceback.print_exc()
                break
            else:
                if type(instruction) is dict:
                    gui.set_fsm_info(instruction)
                else:
                    try:
                        gui.execute_instruction(instruction)
                    except:
                        logger.error('Error while executing instruction')
                        traceback.print_exc()
                        break

