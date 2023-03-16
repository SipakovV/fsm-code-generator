from threading import Thread

from fsm_runtime_gui import FSMRuntimeApp
from fsm_compile_gui import FSMEditApp
from timer import TimerThread


class GuiThread(Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.timer_thread = TimerThread(self)
        self.timer_thread.daemon = True

    def run(self):
        #logger.debug('GUI thread started!')
        self.app = FSMRuntimeApp()
        self.app.master.title('FSM GUI: Traffic Lights')
        self.app.master.minsize(1000, 620)
        self.app.master.maxsize(1000, 620)

        self.timer_thread.start()
        self.app.mainloop()
        #logger.debug('GUI thread ended!')

    def execute_instruction(self, instr):
        if instr['instruction'] == 'set_timeout':
            self.timer_thread.set_timer(instr['parameter'])
        elif instr['instruction'] in self.app.instructions_dict:
            self.app.instructions_dict[instr['instruction']]()
            #logger.debug(f'instruction executed: {instr}')
        else:
            pass
            #logger.debug(f'unknown instruction: {instr}')

    def get_event(self):
        if self.app.queue.empty():
            return None
        else:
            return self.app.queue.get()

    def timeout_event(self):
        self.app.update_timer(0)
        self.app.queue.put('timeout')

    def update_timer(self, timeout_seconds):
        self.app.update_timer(timeout_seconds)

    def activate(self, config):
        self.app.activate(config)