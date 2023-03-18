from threading import Thread, Event
import time


class TimerThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.seconds_remaining = 0
        self.is_active = False
        self._stop_event = Event()
        #self.run()

    def set_timer(self, timeout_seconds):
        self.seconds_remaining = timeout_seconds
        self.is_active = True
        #logger.debug(f'Timer is set: {timeout_seconds}s')

    def run(self):
        #logger.debug(f'Timer is running')
        while True:
            if not self.stopped():
                if self.is_active:
                    self.parent.update_timer(self.seconds_remaining)
                    time.sleep(1)
                    self.seconds_remaining -= 1
                    if self.seconds_remaining == 0:
                        self.parent.timeout_event()
                        self.is_active = False
                else:
                    time.sleep(0.01)

    def stop(self):
        self._stop_event.set()
        #self.seconds_remaining = 0
        #self.is_active = False

    def stopped(self):
        return self._stop_event.is_set()
