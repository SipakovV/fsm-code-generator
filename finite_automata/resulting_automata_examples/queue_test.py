from queue import Queue, Empty

queue = Queue()


if __name__ == '__main__':

    for i in range(5):
        print(i)
        queue.put(i)
        print(queue)

    print(queue.get(block=False))
    print(queue.get(block=False))
    print(queue.get(block=False))
    print(queue.get(block=False))
    print(queue.get(block=False))
    try:
        event = queue.get(block=False)
    except Empty:
        event = None
    print(event)
