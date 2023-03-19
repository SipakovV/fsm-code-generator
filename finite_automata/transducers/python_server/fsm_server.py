import importlib
import importlib.util
import os
import socket
import sys
import shutil
import time
from threading import Thread, enumerate
from _thread import interrupt_main
import traceback
import json
import logging

from python_server import event_queue


ADDRESS = ('127.0.0.1', 12345)
MAX_BUFFER_SIZE = 4096

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)-6s] %(message)s'))
logger.addHandler(handler)

fsm_module = None


def instruction_listening_thread(conn):  # thread for listening at queue for instructions
    while True:
        try:
            instruction = event_queue.get_next_instruction()
            instruction_dict = {
                'instruction': instruction[0],
                'parameter': instruction[1],
            }
            instruction_json = json.dumps(instruction_dict)
            conn.sendall(bytes(instruction_json, encoding="utf-8"))
        except:
            traceback.print_exc()
            break
        time.sleep(0.001)


def event_listening_thread(conn, ip, port):  # thread for listening at socket for events
    while True:
        try:
            try:
                event_json = str(conn.recv(MAX_BUFFER_SIZE), encoding='utf-8')
            except:
                logger.error('Error while receiving json')
                break

            siz = sys.getsizeof(event_json)
            if siz >= MAX_BUFFER_SIZE:
                logger.warning('The length of input is probably too long: {}'.format(siz))

            event_dict = json.loads(event_json)
            event_queue.put_event(event_dict['event'])
        except:
            # traceback.print_exc()
            break

    conn.close()
    #print('Connection ' + ip + ':' + port + ' closed')
    interrupt_main()
    # logging.info('Connection ' + ip + ':' + port + " closed")


def run(file_path):  # запуск сервера
    # fsm_module_path = 'generated_automata.' + args.fsm_code_file
    fsm_name = os.path.basename(file_path)

    if fsm_name[-3:] != '.py':
        logger.error(f'File provided is not a Python source file: {fsm_name}')

    temp_file_path = os.path.abspath(os.path.dirname(sys.argv[0])).replace('\\', '/') + '/python_server/temp/' + fsm_name
    shutil.copy(file_path, temp_file_path)
    #file_path
    fsm_module_path = '.' + fsm_name
    #print(fsm_module_path, fsm_module_path[-3:])
    fsm_module_path = fsm_module_path[:-3]

    try:
        fsm_module = importlib.import_module(fsm_module_path, package='python_server.temp')
    except ImportError:
        logger.error(f'Could not import module: {fsm_module_path}')
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # logger.info('Socket created')

    try:
        sock.bind(ADDRESS)
        #print('Socket bind complete')
    except socket.error:
        logging.error('Socket bind failed. Error: ' + str(sys.exc_info()))
        # logging.error('Bind failed. Error: ' + str(sys.exc_info()))
        sys.exit(1)

    sock.listen(1)
    sock.settimeout(0.5)
    logger.info(f'Socket now listening at {ADDRESS[0]}:{ADDRESS[1]}')

    conn = None

    try:
        while True:
            try:
                conn, addr = sock.accept()
                ip, port = str(addr[0]), str(addr[1])
                logger.info('Accepting connection from ' + ip + ':' + port)
                try:
                    Thread(target=event_listening_thread, args=(conn, ip, port), daemon=True).start()
                    Thread(target=instruction_listening_thread, args=(conn,), daemon=True).start()
                    #for thread in enumerate():
                        #print(f'Hello from thread {thread}')
                        # logging.debug(f'Hello from thread {thread}')
                except:
                    logger.error('Error while starting threads')
                    traceback.print_exc()

                try:
                    fsm_module.run_fsm()
                except AttributeError:
                    logger.error('Invalid FSM module (run_fsm() not found)')
                #class_based_fsm.run()
            except socket.timeout:
                pass

    except KeyboardInterrupt:
        if conn:
            conn.close()

    logger.info('Server stopped')


#if __name__ == '__main__':
#    run()
