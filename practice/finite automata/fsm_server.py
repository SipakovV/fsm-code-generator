import socket
import sys
import time
from threading import Thread, enumerate
import traceback
import json
import logging


import event_queue
from traffic_lights_4way_with_button import run_fsm  # TODO: make dependant on input parameter

logging.basicConfig(filename='debug.log', level=logging.DEBUG)

ADDRESS = ("127.0.0.1", 12345)
MAX_BUFFER_SIZE = 4096


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s| %(name)-40s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


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
                logger.warning("The length of input is probably too long: {}".format(siz))

            event_dict = json.loads(event_json)
            event_queue.put_event(event_dict['event'])
            #process_query(conn, input_from_client, get_ident())
        except:
            #traceback.print_exc()
            break

    conn.close()
    print('Connection ' + ip + ':' + port + " closed")
    #logging.info('Connection ' + ip + ':' + port + " closed")


def start_server():  # запуск сервера

    #logger.info('Server started')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #logger.info('Socket created')

    try:
        sock.bind(ADDRESS)
        print('Socket bind complete')
    except socket.error:
        print('Bind failed. Error: ' + str(sys.exc_info()))
        #logging.error('Bind failed. Error: ' + str(sys.exc_info()))
        sys.exit()

    sock.listen(1)
    print(f'Socket now listening at {ADDRESS[0]}:{ADDRESS[1]}')

    try:
        conn, addr = sock.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=event_listening_thread, args=(conn, ip, port), daemon=True).start()
            Thread(target=instruction_listening_thread, args=(conn,), daemon=True).start()
            for thread in enumerate():
                print(f'Hello from thread {thread}')
                #logging.debug(f'Hello from thread {thread}')
        except:
            print("Terrible error!")
            traceback.print_exc()

        run_fsm()

    except KeyboardInterrupt:
        print("\nServer stopped")
        return


if __name__ == '__main__':
    start_server()
