import json
import logging
import os
import sys
import time
import traceback
import socket
from subprocess import Popen, PIPE
from threading import Thread
from _thread import interrupt_main
import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font
import tkinter.ttk as ttk
from PIL import ImageTk, Image
#from queue import Queue

from utility import timings
from runtime_admin_app import timer
from runtime_admin_app.traffic_lights_gui_preset import TrafficLight, PedestrianLight, TimerDisplay
from python_server import fsm_server


SERVER_ADDRESS = ("127.0.0.1", 12345)
MAX_BUFFER_SIZE = 4096


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)-6s] %(message)s'))
logger.addHandler(handler)

app_colors = {
    'bg': 'white',
    'primary': 'light blue',
    'secondary': 'light gray',
    'error': 'red',
    'warning': 'yellow',
}

tl_dimensions = {
    'lamp_size': 30,
    'padding': 3,
    'canvas_size': 110,
}

tl_colors = {
    'red': 'red',
    'yellow': 'yellow',
    'green': '#30ff30',
    'off': 'black',
    'base': 'gray',
}


def get_instruction_from_server(soc):  # принятие пакета от сервера
    instruction_json = soc.recv(MAX_BUFFER_SIZE)
    #logger.debug(instruction_json)
    instruction_dict = json.loads(instruction_json)
    return instruction_dict


def instruction_listening_thread(sock, gui):  # поток, обрабатывающий пакеты с сервера
    while True:
        try:
            instruction_dict = get_instruction_from_server(sock)
        except ConnectionResetError:
            logger.info('Server closed')
            gui.reset()
            break
        except:
            logger.error('Error while getting data from server')
            traceback.print_exc()
            break
        else:
            logger.debug(f'Instruction received: {instruction_dict}')

            try:
                gui.execute_instruction(instruction_dict)
            except:
                logger.error('Error while data output to gui')
                traceback.print_exc()
                break


def connecting_thread(sock, gui):
    while True:
        try:
            sock.connect(SERVER_ADDRESS)
        except ConnectionRefusedError:
            logger.info('Connecting...')
            time.sleep(0.1)
        else:
            gui.activate()
            break


def _placeholder():
    pass


class FSMRuntimeApp(tk.Frame):
    #queue = Queue()

    def __init__(self, master=None):
        super().__init__(master)

        self.master.title('FSM GUI: Traffic Lights')
        self.master.minsize(800, 450)
        self.master.maxsize(1600, 900)
        self.master.protocol("WM_DELETE_WINDOW", self.exit)
        self.configure(bg='white')

        self.FONTS = {
            'oldstyle': Font(family='Adobe Caslon Oldstyle Figures', size=30),
            'monospace': Font(family='Courier New', size=10),
            'normal': Font(family='Helvetica', size=12),
            'heading': Font(family='Helvetica', size=16),
        }

        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TLabel', foreground='black', background=app_colors['bg'], padding=10, font=self.FONTS['normal'])
        self.style.configure('Header.TLabel', foreground='black', background=app_colors['bg'], padding=10,
                                     font=self.FONTS['heading'])
        self.style.configure('Timer.TLabel', foreground='black', background=app_colors['bg'], padding=10, font=self.FONTS['oldstyle'])
        self.style.configure('TFrame', background=app_colors['bg'])
        self.style.configure('TButton', background=app_colors['primary'], foreground='black', padding=10, font=self.FONTS['normal'])
        self.style.configure('TNotebook.Tab', background='light blue', focuscolor=self.style.configure('.')['background'])
        self.style.configure('TNotebook', background='white')
        self.style.map('TNotebook.Tab',
                       background=[('selected', 'white'), ],
                       focuscolor=[('selected', 'white'), ])

        #NOTEBOOK_STYLE.configure('My.TNotebook.Tab', background='green3')
        #NOTEBOOK_STYLE.map('My.TNotebook', background=[('selected', 'green3')])

        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=_placeholder)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=_placeholder)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=_placeholder)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.master.config(menu=menubar)

        #self.parent_frame = parent_frame
        self.sock = None
        self.connected = False
        self.timer_thread = timer.TimerThread(self)
        self.timer_thread.daemon = True

        self.server_process = None

        col_count, row_count = self.grid_size()

        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        for row in range(row_count):
            self.grid_rowconfigure(row, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        self.timeout_var = tk.IntVar()
        self.title_var = tk.StringVar()
        self.description_var = tk.StringVar()

        self.title_label = ttk.Label(self, textvariable=self.title_var, style='Header.TLabel')
        self.title_label.grid(row=0, column=0)

        self.description_label = ttk.Label(self, textvariable=self.description_var)
        self.description_label.grid(row=0, column=1, columnspan=3)

        #self.timer_display_default = TimerDisplay(self, 0, self.timeout_var)
        #self.timer_display_default = ttk.Label(self, font='Courier 18 bold',  textvariable=self.timeout_var)
        self.timer_display_frame = tk.Frame(self, bg='#bbddff')
        self.timer_display_default = ttk.Label(self.timer_display_frame, textvariable=self.timeout_var, style='Timer.TLabel')
        self.timer_display_default.pack(pady=10, padx=10)
        self.timer_display_frame.grid(row=0, column=5)

        self.graph_image = Image.open('generated_graph_images/fsm_TL_4way_1button.png')
        self.graph_image = self.graph_image.resize((700, 700), Image.ANTIALIAS)
        self.graph_photoimage = ImageTk.PhotoImage(self.graph_image)
        self.graph_image_lbl = ttk.Label(self, image=self.graph_photoimage, style='TLabel')
        self.graph_image_lbl.grid(row=0, column=6, rowspan=6, columnspan=6)
        #self.timer_progressbar = ttk.Progressbar()

        #self.switch_app_button = tk.Button(self, text='Edit', command=self.switch_app)
        #self.switch_app_button.grid(row=0, column=2)

        self.tab_control = ttk.Notebook(self, style='TNotebook')
        self.init_tab_traffic(self.tab_control)
        self.init_tab_elevator(self.tab_control)
        self.tab_control.grid(row=1, column=0, rowspan=5, columnspan=6, padx=10, pady=10)

        self.pack()

        self.widgets_dict = {
            'p1': self.pedestrian_lights_list[0],
            'p2': self.pedestrian_lights_list[1],
            'p3': self.pedestrian_lights_list[2],
            'p4': self.pedestrian_lights_list[3],
            'p5': self.pedestrian_lights_list[4],
            'p6': self.pedestrian_lights_list[5],
        }

        self.instructions_dict = {
            'p1_red': self.pedestrian_lights_list[0].set_red,
            'p1_green': self.pedestrian_lights_list[0].set_green,
            'p1_blinking': self.pedestrian_lights_list[0].set_green_blinking,

            'p2_red': self.pedestrian_lights_list[1].set_red,
            'p2_green': self.pedestrian_lights_list[1].set_green,
            'p2_blinking': self.pedestrian_lights_list[1].set_green_blinking,

            'p3_red': self.pedestrian_lights_list[2].set_red,
            'p3_green': self.pedestrian_lights_list[2].set_green,
            'p3_blinking': self.pedestrian_lights_list[2].set_green_blinking,

            'p4_red': self.pedestrian_lights_list[3].set_red,
            'p4_green': self.pedestrian_lights_list[3].set_green,
            'p4_blinking': self.pedestrian_lights_list[3].set_green_blinking,

            'p5_red': self.pedestrian_lights_list[4].set_red,
            'p5_green': self.pedestrian_lights_list[4].set_green,
            'p5_blinking': self.pedestrian_lights_list[4].set_green_blinking,

            'p6_red': self.pedestrian_lights_list[5].set_red,
            'p6_green': self.pedestrian_lights_list[5].set_green,
            'p6_blinking': self.pedestrian_lights_list[5].set_green_blinking,

            't1_red': self.traffic_lights_list[0].set_red,
            't1_yellow_red': self.traffic_lights_list[0].set_yellow_red,
            't1_yellow': self.traffic_lights_list[0].set_yellow,
            't1_green': self.traffic_lights_list[0].set_green,
            't1_blinking': self.traffic_lights_list[0].set_green_blinking,

            't2_red': self.traffic_lights_list[1].set_red,
            't2_yellow_red': self.traffic_lights_list[1].set_yellow_red,
            't2_yellow': self.traffic_lights_list[1].set_yellow,
            't2_green': self.traffic_lights_list[1].set_green,
            't2_blinking': self.traffic_lights_list[1].set_green_blinking,

            't3_red': self.traffic_lights_list[2].set_red,
            't3_yellow_red': self.traffic_lights_list[2].set_yellow_red,
            't3_yellow': self.traffic_lights_list[2].set_yellow,
            't3_green': self.traffic_lights_list[2].set_green,
            't3_blinking': self.traffic_lights_list[2].set_green_blinking,

            't4_red': self.traffic_lights_list[3].set_red,
            't4_yellow_red': self.traffic_lights_list[3].set_yellow_red,
            't4_yellow': self.traffic_lights_list[3].set_yellow,
            't4_green': self.traffic_lights_list[3].set_green,
            't4_blinking': self.traffic_lights_list[3].set_green_blinking,

            't5_red': self.traffic_lights_list[4].set_red,
            't5_yellow_red': self.traffic_lights_list[4].set_yellow_red,
            't5_yellow': self.traffic_lights_list[4].set_yellow,
            't5_green': self.traffic_lights_list[4].set_green,
            't5_blinking': self.traffic_lights_list[4].set_green_blinking,

            't6_red': self.traffic_lights_list[5].set_red,
            't6_yellow_red': self.traffic_lights_list[5].set_yellow_red,
            't6_yellow': self.traffic_lights_list[5].set_yellow,
            't6_green': self.traffic_lights_list[5].set_green,
            't6_blinking': self.traffic_lights_list[5].set_green_blinking,
        }

        #self.after(100, self.load_file)

    def init_tab_traffic(self, tab_control):
        self.tab_traffic = ttk.Frame(tab_control, style='TFrame', width=700, height=700)

        col_count, row_count = self.tab_traffic.grid_size()
        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        for row in range(row_count):
            self.grid_rowconfigure(row, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        self.tab_control.add(self.tab_traffic, text='Traffic lights')

        """ Traffic lights section """
        #self.traffic_frame = tk.Frame(self.tab_traffic)

        self.traffic_lights_list = [TrafficLight(self.tab_traffic, 0, i, tl_dimensions, tl_colors) for i in range(6)]

        #self.traffic_light_1 = TrafficLight(self.tab_traffic, 0, 0, tl_dimensions, tl_colors)
        #self.traffic_light_2 = TrafficLight(self.tab_traffic, 0, 1, tl_dimensions, tl_colors)
        #self.traffic_light_3 = TrafficLight(self.tab_traffic, 0, 2, tl_dimensions, tl_colors)
        #self.traffic_light_4 = TrafficLight(self.tab_traffic, 0, 3, tl_dimensions, tl_colors)
        #self.traffic_light_5 = TrafficLight(self.tab_traffic, 0, 4, tl_dimensions, tl_colors)
        #self.traffic_light_6 = TrafficLight(self.tab_traffic, 0, 5, tl_dimensions, tl_colors)

        #self.traffic_frame.grid(row=1, column=0, columnspan=6, pady=5)
        """ === """

        """ Pedestrian lights section """
        #self.pedestrian_frame = tk.Frame(self.tab_traffic)

        self.pedestrian_lights_list = [PedestrianLight(self.tab_traffic, 1, i, tl_dimensions, tl_colors) for i in range(6)]
        #self.pedestrian_light_1 = PedestrianLight(self.tab_traffic, 1, 0, tl_dimensions, tl_colors)
        #self.pedestrian_light_2 = PedestrianLight(self.tab_traffic, 1, 1, tl_dimensions, tl_colors)
        #self.pedestrian_light_3 = PedestrianLight(self.tab_traffic, 1, 2, tl_dimensions, tl_colors)
        #self.pedestrian_light_4 = PedestrianLight(self.tab_traffic, 1, 3, tl_dimensions, tl_colors)
        #self.pedestrian_light_5 = PedestrianLight(self.tab_traffic, 1, 4, tl_dimensions, tl_colors)
        #self.pedestrian_light_6 = PedestrianLight(self.tab_traffic, 1, 5, tl_dimensions, tl_colors)

        #self.pedestrian_frame.grid(row=2, column=0, columnspan=6, pady=5)
        """ === """

        """ Buttons section """
        #self.buttons_frame = tk.Frame(self.tab_traffic)
        self.input_btn_1 = ttk.Button(self.tab_traffic, text='Btn1', command=lambda: self.send_event('button1'), style='TButton')
        self.input_btn_1.grid(row=2, column=0, padx=5, pady=5)
        self.input_btn_2 = ttk.Button(self.tab_traffic, text='Btn2', command=lambda: self.send_event('button2'), style='TButton')
        self.input_btn_2.grid(row=2, column=1, padx=5, pady=5)
        self.input_btn_3 = ttk.Button(self.tab_traffic, text='Btn3', command=lambda: self.send_event('button3'), style='TButton')
        self.input_btn_3.grid(row=2, column=2, padx=5, pady=5)
        self.input_btn_4 = ttk.Button(self.tab_traffic, text='Btn4', command=lambda: self.send_event('button4'), style='TButton')
        self.input_btn_4.grid(row=2, column=3, padx=5, pady=5)
        self.input_btn_5 = ttk.Button(self.tab_traffic, text='Btn5', command=lambda: self.send_event('button5'), style='TButton')
        self.input_btn_5.grid(row=2, column=4, padx=5, pady=5)
        self.input_btn_6 = ttk.Button(self.tab_traffic, text='Btn6', command=lambda: self.send_event('button6'), style='TButton')
        self.input_btn_6.grid(row=2, column=5, padx=5, pady=5)
        #self.buttons_frame.grid(row=3, column=0, columnspan=6, pady=5)
        """ === """

    def init_tab_elevator(self, tab_control):
        self.tab_elevator = ttk.Frame(tab_control, style='TFrame', width=700, height=700)

        col_count, row_count = self.tab_elevator.grid_size()
        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        for row in range(row_count):
            self.grid_rowconfigure(row, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        self.tab_control.add(self.tab_elevator, text='Elevator')

    def update_timer(self, timeout_seconds):
        self.timeout_var.set(timeout_seconds)

    def send_event(self, event):
        if self.connected:
            event_dict = {
                'event': event,
            }
            event_json = json.dumps(event_dict)
            self.sock.send(bytes(event_json, encoding='utf-8'))
            #self.queue.put(event)

    def timeout_event(self):
        self.update_timer(0)
        self.send_event('timeout')

    def execute_instruction(self, instr):
        if instr['instruction'] == 'set_timeout':
            self.timer_thread.set_timer(instr['parameter'])
        elif instr['instruction'] in self.instructions_dict:
            self.instructions_dict[instr['instruction']]()
            #logger.debug(f'instruction executed: {instr}')
        else:
            pass

    def reset(self):
        self.server_process.kill()
        self.sock.close()
        self.sock = None
        self.timer_thread.reset_timer()
        self.timeout_var.set(0)
        logger.info(f'App is reset')

    def open_file(self):
        init_dir = os.path.abspath(os.path.dirname(sys.argv[0])).replace('\\', '/') + '/python_fsm_generated'
        filename = filedialog.askopenfilename(
            initialdir=init_dir)
        logger.info(f'Opening file: {filename}')
        self.load_file(filename)

    def load_file(self, filename):
        if self.connected:
            self.reset()
        self.start_server(filename)
        self.after(1000, self.connect)

    def start_server(self, filename):
        try:
            self.server_process = Popen(['python', 'fsm_server_python.py', filename])
            #fsm_server.run(filename)
        except FileNotFoundError:
            self.server_process = Popen(['python3', 'fsm_server_python.py', filename])

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            Thread(target=connecting_thread, args=(self.sock, self), daemon=True).start()
        except:
            logger.error("Error while starting connecting thread")
            traceback.print_exc()

    def activate(self):
        if not self.timer_thread.is_alive():
            self.timer_thread.start()
        self.connected = True
        config = {
            'title': 'test',
            'description': 'bla bla bla FSM bla bla\nbla bla'
        }
        self.title_var.set(config['title'])
        self.description_var.set(config['description'])
        logger.info('Connected to server')
        try:
            Thread(target=instruction_listening_thread, args=(self.sock, self), daemon=True).start()
        except:
            logger.error("Error while starting listening thread")
            traceback.print_exc()

    def exit(self):
        if self.server_process:
            self.server_process.kill()
        self.master.quit()


def start_admin():
    app = FSMRuntimeApp()
    app.mainloop()
