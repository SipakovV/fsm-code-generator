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

    def reset_timer(self):
        self.seconds_remaining = 0
        self.is_active = False
        self.parent.update_timer(0)

    def set_timer(self, timeout_seconds):
        self.seconds_remaining = timeout_seconds
        self.is_active = True
        self.parent.update_timer(self.seconds_remaining)

    def add_timer(self, timeout_seconds):
        self.seconds_remaining += timeout_seconds
        self.parent.update_timer(self.seconds_remaining)

    def pause_timer(self):
        self.is_active = False

    def resume_timer(self):
        self.is_active = True

    def run(self):
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

    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def is_active(self) -> bool:
        return self.is_active
