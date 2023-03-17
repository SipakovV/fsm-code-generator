from threading import Thread
import tkinter as tk

from app.admin_client.fsm_runtime_gui import FSMRuntimeApp
from app.admin_client.fsm_compile_gui import FSMCompileApp
from app.admin_client.timer import TimerThread


def _placeholder():
    pass


class App(tk.Frame):
    def __init__(self, parent_thread):
        super().__init__()

        self.parent_thread = parent_thread

        self.runtime_app = FSMRuntimeApp(self.master)
        self.runtime_app.grid(row=0, column=0, sticky='nsew')

        self.compile_app = FSMCompileApp(self.master)
        self.compile_app.grid(row=0, column=0, sticky='nsew')

        self.runtime_app.tkraise()

        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=_placeholder)
        filemenu.add_command(label="Open", command=_placeholder)
        filemenu.add_command(label="Save", command=_placeholder)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=_placeholder)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.master.config(menu=menubar)

    def execute_instruction(self, instr):
        if instr['instruction'] == 'set_timeout':
            self.parent_thread.timer_thread.set_timer(instr['parameter'])
        elif instr['instruction'] in self.runtime_app.instructions_dict:
            self.runtime_app.instructions_dict[instr['instruction']]()
            #logger.debug(f'instruction executed: {instr}')
        else:
            pass
            #logger.debug(f'unknown instruction: {instr}')

    def get_event(self):
        if self.runtime_app.queue.empty():
            return None
        else:
            return self.runtime_app.queue.get()

    def timeout_event(self):
        self.runtime_app.update_timer(0)
        self.runtime_app.queue.put('timeout')

    def update_timer(self, timeout_seconds):
        self.runtime_app.update_timer(timeout_seconds)

    def activate_runtime(self, config):
        self.runtime_app.activate(config)


class GuiThread(Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.timer_thread = TimerThread(self)
        self.timer_thread.daemon = True

    def run(self):
        #logger.debug('GUI thread started!')
        self.app = App(self)
        self.app.master.title('FSM GUI: Traffic Lights')
        self.app.master.minsize(1000, 620)
        self.app.master.maxsize(1000, 620)

        self.timer_thread.start()
        self.app.mainloop()
        #logger.debug('GUI thread ended!')

    def execute_instruction(self, instr):
        self.app.execute_instruction(instr)

    def get_event(self):
        return self.app.get_event()

    def timeout_event(self):
        self.app.timeout_event()

    def update_timer(self, timeout_seconds):
        self.app.update_timer(timeout_seconds)

    def activate_runtime(self, config):
        self.app.activate_runtime(config)
