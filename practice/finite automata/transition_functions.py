import time


class Transition:
    def sleep(self, sleep_seconds: int):
        time.sleep(sleep_seconds)

    def print_string(self, s: str):
        print(s)
