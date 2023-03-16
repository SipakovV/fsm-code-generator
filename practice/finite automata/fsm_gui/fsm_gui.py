import logging
import sys
import time
import tkinter as tk
from tkinter import *
from threading import Thread
from queue import Queue

MAX_BUFFER_SIZE = 4096


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s| %(name)-40s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


"""TL sizes"""
LAMP_SIZE = 40
PADDING_SIZE = 5
CANVAS_SIZE = 150

"""TL colors"""
RED_COLOR = 'red'
YELLOW_COLOR = 'yellow'
GREEN_COLOR = '#30ff30'
OFF_COLOR = 'black'
BASE_COLOR = 'gray'


def _placeholder():
    pass


class TrafficLight:
    def __init__(self, parent_frame, index):
        self.canvas = tk.Canvas(parent_frame, bg='white', height=CANVAS_SIZE, width=CANVAS_SIZE)
        self.canvas.grid(row=0, column=index)

        self.base = self.canvas.create_rectangle(CANVAS_SIZE / 2 - LAMP_SIZE / 2 - PADDING_SIZE,
                                                   PADDING_SIZE,
                                                   CANVAS_SIZE / 2 + LAMP_SIZE / 2 + PADDING_SIZE,
                                                   CANVAS_SIZE - PADDING_SIZE,
                                                   outline='black', fill=BASE_COLOR)
        self.red_light = self.canvas.create_oval(CANVAS_SIZE / 2 - LAMP_SIZE / 2,
                                                 PADDING_SIZE * 2,
                                                 CANVAS_SIZE / 2 + LAMP_SIZE / 2,
                                                 PADDING_SIZE * 2 + LAMP_SIZE,
                                                 fill=OFF_COLOR)
        self.yellow_light = self.canvas.create_oval(CANVAS_SIZE / 2 - LAMP_SIZE / 2,
                                                 PADDING_SIZE * 3 + LAMP_SIZE,
                                                 CANVAS_SIZE / 2 + LAMP_SIZE / 2,
                                                 PADDING_SIZE * 3 + LAMP_SIZE * 2,
                                                 fill=OFF_COLOR)
        self.green_light = self.canvas.create_oval(CANVAS_SIZE / 2 - LAMP_SIZE / 2,
                                                 PADDING_SIZE * 4 + LAMP_SIZE * 2,
                                                 CANVAS_SIZE / 2 + LAMP_SIZE / 2,
                                                 PADDING_SIZE * 4 + LAMP_SIZE * 3,
                                                 fill=OFF_COLOR)

    def set_red(self):
        self.canvas.itemconfig(self.red_light, fill=RED_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill=OFF_COLOR)

    def set_yellow_red(self):
        self.canvas.itemconfig(self.red_light, fill=RED_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=YELLOW_COLOR)
        self.canvas.itemconfig(self.green_light, fill=OFF_COLOR)

    def set_yellow(self):
        self.canvas.itemconfig(self.red_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=YELLOW_COLOR)
        self.canvas.itemconfig(self.green_light, fill=OFF_COLOR)

    def set_green(self):
        self.canvas.itemconfig(self.red_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill=GREEN_COLOR)

    def set_green_blinking(self):
        self.canvas.itemconfig(self.red_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill='cyan')


class PedestrianLight:
    def __init__(self, parent_frame, index):
        self.canvas = tk.Canvas(parent_frame, bg='white', height=150, width=150)
        self.canvas.grid(row=1, column=index)

        self.border = self.canvas.create_rectangle(50, 25, 100, 125, outline='black', fill=BASE_COLOR)
        self.red_light = self.canvas.create_oval(55, 30, 95, 70, fill=OFF_COLOR)
        self.green_light = self.canvas.create_oval(55, 80, 95, 120, fill=OFF_COLOR)

    def set_red(self):
        self.canvas.itemconfig(self.red_light, fill=RED_COLOR)
        self.canvas.itemconfig(self.green_light, fill=OFF_COLOR)

    def set_green(self):
        self.canvas.itemconfig(self.red_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill=GREEN_COLOR)

    def set_green_blinking(self):
        self.canvas.itemconfig(self.red_light, fill=OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill='cyan')


class TimerDisplay:
    def __init__(self, parent_frame, index, timeout_var):
        #self.canvas = tk.Canvas(parent_frame, bg='white', height=150, width=150)
        #self.canvas.grid(row=2, column=index)

        #self.border = self.canvas.create_rectangle(50, 25, 100, 125, outline='black')
        #self.label = self.canvas.create_text(75, 50, fill='black', font='Verdana 15')
        #self.timeout_var = timeout_var
        self.label = tk.Label(parent_frame, font='Verdana 15', textvariable=timeout_var)
        self.label.pack()


class App(tk.Frame):
    queue = Queue()

    def __init__(self, master=None):
        super().__init__(master)

        self.connected = False

        col_count, row_count = self.grid_size()

        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=155)

        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=_placeholder)
        filemenu.add_command(label="Open", command=_placeholder)
        filemenu.add_command(label="Save", command=_placeholder)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=_placeholder)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.master.config(menu=menubar)

        self.timeout_var = IntVar()
        self.title_var = StringVar()
        self.description_var = StringVar()

        self.title_label = tk.Label(self, textvariable=self.title_var)
        self.title_label.grid(row=0, column=0)

        self.title_label = tk.Label(self, textvariable=self.description_var)
        self.title_label.grid(row=0, column=1)

        """ Traffic lights section """
        self.traffic_frame = tk.Frame(self)

        self.traffic_light_1 = TrafficLight(self.traffic_frame, 0)
        self.traffic_light_2 = TrafficLight(self.traffic_frame, 1)
        self.traffic_light_3 = TrafficLight(self.traffic_frame, 2)
        self.traffic_light_4 = TrafficLight(self.traffic_frame, 3)
        self.traffic_light_5 = TrafficLight(self.traffic_frame, 4)
        self.traffic_light_6 = TrafficLight(self.traffic_frame, 5)

        self.traffic_frame.grid(row=1, column=0, columnspan=6, pady=5)
        """ === """

        """ Pedestrian lights section """
        self.pedestrian_frame = tk.Frame(self)

        self.pedestrian_light_1 = PedestrianLight(self.pedestrian_frame, 0)
        self.pedestrian_light_2 = PedestrianLight(self.pedestrian_frame, 1)
        self.pedestrian_light_3 = PedestrianLight(self.pedestrian_frame, 2)
        self.pedestrian_light_4 = PedestrianLight(self.pedestrian_frame, 3)
        self.pedestrian_light_5 = PedestrianLight(self.pedestrian_frame, 4)
        self.pedestrian_light_6 = PedestrianLight(self.pedestrian_frame, 5)

        self.pedestrian_frame.grid(row=2, column=0, columnspan=6, pady=5)
        """ === """

        """ Timer displays section """
        self.timer_display_frame = tk.Frame(self)

        self.timer_display_default = TimerDisplay(self.timer_display_frame, 0, self.timeout_var)
        # self.timer_display_2 = TimerDisplay(self.timer_display_frame, 1)
        # self.timer_display_3 = TimerDisplay(self.timer_display_frame, 2)
        # self.timer_display_4 = TimerDisplay(self.timer_display_frame, 3)
        # self.timer_display_5 = TimerDisplay(self.timer_display_frame, 4)

        self.timer_display_frame.grid(row=3, column=0, columnspan=6, pady=5)
        """ === """

        """ Buttons section """
        self.buttons_frame = tk.Frame(self)
        self.input_btn_1 = tk.Button(self.buttons_frame, text='Btn1', command=lambda: self.send_to_master('button1'),
                                     height=5, width=15)
        self.input_btn_1.grid(row=0, column=0, padx=5)
        self.input_btn_2 = tk.Button(self.buttons_frame, text='Btn2', command=lambda: self.send_to_master('button2'),
                                     height=5, width=15)
        self.input_btn_2.grid(row=0, column=1, padx=5)
        self.input_btn_3 = tk.Button(self.buttons_frame, text='Btn3', command=lambda: self.send_to_master('button3'),
                                     height=5, width=15)
        self.input_btn_3.grid(row=0, column=2, padx=50)
        self.input_btn_4 = tk.Button(self.buttons_frame, text='Btn4', command=lambda: self.send_to_master('button4'),
                                     height=5, width=15)
        self.input_btn_4.grid(row=0, column=3, padx=5)
        self.input_btn_5 = tk.Button(self.buttons_frame, text='Btn5', command=lambda: self.send_to_master('button5'),
                                     height=5, width=15)
        self.input_btn_5.grid(row=0, column=4, padx=5)
        self.input_btn_6 = tk.Button(self.buttons_frame, text='Btn6', command=lambda: self.send_to_master('button6'),
                                     height=5, width=15)
        self.input_btn_6.grid(row=0, column=5, padx=5)
        self.buttons_frame.grid(row=4, column=0, columnspan=6, pady=5)
        """ === """

        self.pack()

        self.instructions_dict = {
            'p1_red': self.pedestrian_light_1.set_red,
            'p1_green': self.pedestrian_light_1.set_green,
            'p1_blinking': self.pedestrian_light_1.set_green_blinking,

            'p2_red': self.pedestrian_light_2.set_red,
            'p2_green': self.pedestrian_light_2.set_green,
            'p2_blinking': self.pedestrian_light_2.set_green_blinking,

            'p3_red': self.pedestrian_light_3.set_red,
            'p3_green': self.pedestrian_light_3.set_green,
            'p3_blinking': self.pedestrian_light_3.set_green_blinking,

            'p4_red': self.pedestrian_light_4.set_red,
            'p4_green': self.pedestrian_light_4.set_green,
            'p4_blinking': self.pedestrian_light_4.set_green_blinking,

            'p5_red': self.pedestrian_light_5.set_red,
            'p5_green': self.pedestrian_light_5.set_green,
            'p5_blinking': self.pedestrian_light_5.set_green_blinking,

            'p6_red': self.pedestrian_light_6.set_red,
            'p6_green': self.pedestrian_light_6.set_green,
            'p6_blinking': self.pedestrian_light_6.set_green_blinking,

            't1_red': self.traffic_light_1.set_red,
            't1_yellow_red': self.traffic_light_1.set_yellow_red,
            't1_yellow': self.traffic_light_1.set_yellow,
            't1_green': self.traffic_light_1.set_green,
            't1_blinking': self.traffic_light_1.set_green_blinking,

            't2_red': self.traffic_light_2.set_red,
            't2_yellow_red': self.traffic_light_2.set_yellow_red,
            't2_yellow': self.traffic_light_2.set_yellow,
            't2_green': self.traffic_light_2.set_green,
            't2_blinking': self.traffic_light_2.set_green_blinking,

            't3_red': self.traffic_light_3.set_red,
            't3_yellow_red': self.traffic_light_3.set_yellow_red,
            't3_yellow': self.traffic_light_3.set_yellow,
            't3_green': self.traffic_light_3.set_green,
            't3_blinking': self.traffic_light_3.set_green_blinking,

            't4_red': self.traffic_light_4.set_red,
            't4_yellow_red': self.traffic_light_4.set_yellow_red,
            't4_yellow': self.traffic_light_4.set_yellow,
            't4_green': self.traffic_light_4.set_green,
            't4_blinking': self.traffic_light_4.set_green_blinking,

            't5_red': self.traffic_light_5.set_red,
            't5_yellow_red': self.traffic_light_5.set_yellow_red,
            't5_yellow': self.traffic_light_5.set_yellow,
            't5_green': self.traffic_light_5.set_green,
            't5_blinking': self.traffic_light_5.set_green_blinking,

            't6_red': self.traffic_light_6.set_red,
            't6_yellow_red': self.traffic_light_6.set_yellow_red,
            't6_yellow': self.traffic_light_6.set_yellow,
            't6_green': self.traffic_light_6.set_green,
            't6_blinking': self.traffic_light_6.set_green_blinking,
        }

    def update_timer(self, timeout_seconds):
        self.timeout_var.set(timeout_seconds)

    def send_to_master(self, event):
        if self.connected:
            self.queue.put(event)

    def button_input1(self):
        self.send_to_master('button1')

    def activate(self, config):
        self.connected = True
        self.title_var.set(config['title'])
        self.description_var.set(config['description'])


class TimerThread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.seconds_remaining = 0
        self.is_active = False
        #self.run()

    def set_timer(self, timeout_seconds):
        self.seconds_remaining = timeout_seconds
        self.is_active = True
        logger.debug(f'Timer is set: {timeout_seconds}s')

    def run(self):
        logger.debug(f'Timer is running')
        while True:
            if self.is_active:
                self.parent.update_timer(self.seconds_remaining)
                time.sleep(1)
                self.seconds_remaining -= 1
                if self.seconds_remaining == 0:
                    self.parent.timeout_event()
                    self.is_active = False
            else:
                time.sleep(0.01)


class GuiThread(Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.timer_thread = TimerThread(self)
        self.timer_thread.daemon = True

    def run(self):
        logger.debug('GUI thread started!')
        self.app = App()
        self.app.master.title('FSM GUI: Traffic Lights')
        self.app.master.minsize(1000, 620)
        self.app.master.maxsize(1000, 620)

        self.timer_thread.start()
        self.app.mainloop()
        logger.debug('GUI thread ended!')

    def execute_instruction(self, instr):
        if instr['instruction'] == 'set_timeout':
            self.timer_thread.set_timer(instr['parameter'])
        elif instr['instruction'] in self.app.instructions_dict:
            self.app.instructions_dict[instr['instruction']]()
            logger.debug(f'instruction executed: {instr}')
        else:
            logger.debug(f'unknown instruction: {instr}')

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
