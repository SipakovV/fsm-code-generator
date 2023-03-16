import importlib
import importlib.util
import socket
import sys
import time
from threading import Thread, enumerate
from _thread import interrupt_main
import traceback
import json
import logging

from app.python_server import event_queue


ADDRESS = ("127.0.0.1", 12345)
MAX_BUFFER_SIZE = 4096

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s| %(name)-40s: %(levelname)s] %(message)s'))
logger.addHandler(handler)

fsm_module = None




#from fsm import FSM

#logging.basicConfig(filename='debug.log', level=logging.DEBUG)



'''
class_based_fsm = FSM(alphabet={'timeout', 'button1'},
                      instructions_set={'set_timeout', 'p1_red', 'p1_green', 'p1_blinking',
                                        't1_red', 't1_red_yellow', 't1_yellow', 't1_green', 't1_blinking'},
                      state_set={'traffic_go', 'traffic_go_ready', 'traffic_go_change', 'traffic_stopping1',
                                 'traffic_stopping2',
                                 'p_go', 'p_stopping', 'traffic_ready'},
                      initial_state='traffic_go',
                      initial_instructions=[('set_timeout', 15), 't1_green', 'p1_red'],
                      final_states=set(),
                      transition_map={
                          'traffic_go': {'timeout': ('traffic_go_ready', []), 'button1': ('traffic_go_change', [])},
                          'traffic_go_ready': {'button1': ('traffic_stopping1', [('set_timeout', 3), 't1_blinking'])},
                          'traffic_go_change': {'timeout': ('traffic_stopping1', [('set_timeout', 3), 't1_blinking'])},
                          'traffic_stopping1': {'timeout': ('traffic_stopping2', [('set_timeout', 3), 't1_yellow'])},
                          'traffic_stopping2': {'timeout': ('p_go', [('set_timeout', 10), 't1_red', 'p1_green'])},
                          'p_go': {'timeout': ('p_stopping', [('set_timeout', 3), 'p1_blinking'])},
                          'p_stopping': {'timeout': ('traffic_ready', [('set_timeout', 3), 't1_yellow_red', 'p1_red'])},
                          'traffic_ready': {'timeout': ('traffic_go', [('set_timeout', 30), 't1_green'])},
                      })
'''


def instruction_listening_thread(conn):  # thread for listening at queue for instructions
    while True:
        try:
            instruction = event_queue.get_next_instruction()
            instruction_dict = {
                'instruction': instruction[0],
                'parameter': instruction[1],
            }
            print(f'{instruction_dict=}')
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
            # process_query(conn, input_from_client, get_ident())
        except:
            # traceback.print_exc()
            break

    conn.close()
    print('Connection ' + ip + ':' + port + ' closed')
    interrupt_main()
    # logging.info('Connection ' + ip + ':' + port + " closed")


def run(fsm_code_file):  # запуск сервера
    # fsm_module_path = 'generated_automata.' + args.fsm_code_file
    fsm_module_path = '.' + fsm_code_file
    print(fsm_module_path, fsm_module_path[-3:])
    if fsm_module_path[-3:] == '.py':
        fsm_module_path = fsm_module_path[:-3]

    # try:
    fsm_module = importlib.import_module(fsm_module_path, package='python_fsm_generated')
    # fsm_module = importlib.import_module('settings', package='..')
    # fsm_module = importlib.import_module(fsm_module_path, package='finite_automata.transducers.app.python_fsm_generated')

    # spec = importlib.util.find_spec(fsm_module_path, package='temp')
    # print('Loader:', spec.loader)

    # m = spec.loader.load_module()
    # print('Module:', m)
    # fsm_module = importlib.import_module('.example_module', package='finite_automata')
    # except ImportError as exc:
    #    print(exc)
    #    print(traceback)
    #    print(f'Invalid automaton file: {fsm_module_path}')
    #    exit(1)
    # logger.info('Server started')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # logger.info('Socket created')

    try:
        sock.bind(ADDRESS)
        print('Socket bind complete')
    except socket.error:
        print('Bind failed. Error: ' + str(sys.exc_info()))
        # logging.error('Bind failed. Error: ' + str(sys.exc_info()))
        sys.exit()

    sock.listen(1)
    sock.settimeout(0.5)
    print(f'Socket now listening at {ADDRESS[0]}:{ADDRESS[1]}')

    conn = None

    try:
        while True:
            try:
                conn, addr = sock.accept()
                ip, port = str(addr[0]), str(addr[1])
                print('Accepting connection from ' + ip + ':' + port)
                try:
                    Thread(target=event_listening_thread, args=(conn, ip, port), daemon=True).start()
                    Thread(target=instruction_listening_thread, args=(conn,), daemon=True).start()
                    for thread in enumerate():
                        print(f'Hello from thread {thread}')
                        # logging.debug(f'Hello from thread {thread}')
                except:
                    print("Error while starting threads")
                    traceback.print_exc()

                fsm_module.run_fsm()
                #class_based_fsm.run()
            except socket.timeout:
                pass

    except KeyboardInterrupt:
        if conn:
            conn.close()

    print("\nServer stopped")


#if __name__ == '__main__':
#    run()
