import threading
import time


def print_work_a():
    print('Starting of thread :', threading.current_thread().name)
    time.sleep(2)
    print('Finishing of thread :', threading.current_thread().name)


def print_work_b():
    print('Starting of thread :', threading.current_thread().name)
    print('Finishing of thread :', threading.current_thread().name)


a = threading.Thread(target=print_work_a, name='Thread-a', daemon=True)
b = threading.Thread(target=print_work_b, name='Thread-b')

a.start()
b.start()
