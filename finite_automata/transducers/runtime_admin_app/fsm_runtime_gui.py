import json
from json.decoder import JSONDecodeError
import logging
import os
import sys
import time
import traceback
import socket
import subprocess
from threading import Thread
from _thread import interrupt_main
import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font
import tkinter.ttk as ttk
from PIL import ImageTk, Image
from queue import Queue

from utility import timings
from runtime_admin_app import timer
from runtime_admin_app.traffic_lights_gui_preset import TrafficLight, PedestrianLight, TimerDisplay
#from python_server import fsm_server


SERVER_ADDRESS = ("127.0.0.1", 12345)
MAX_BUFFER_SIZE = 4096

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: client %(levelname)-7s] %(message)s'))
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
    'off_active': 'black',
    'off_disabled': 'gray',
    'base_active': 'gray',
    'base_disabled': 'light gray',
}


def load_image(path):
    try:
        img = Image.open(path)
        img_resized = img.resize((700, 700), Image.ANTIALIAS)
        photoimg = ImageTk.PhotoImage(img_resized)
        #photoimg = tk.PhotoImage(path)
    except Exception as exc:
        print(exc)
    else:
        return photoimg


def get_instruction_from_server(sock):
    instruction_json = sock.recv(MAX_BUFFER_SIZE)
    # TODO: split multiple jsons received (or handle otherwise)

    #dict_list = [d.strip() for d in instruction_json.splitlines()]
    #for d in dict_list:
    instruction = json.loads(instruction_json)
    logger.debug(instruction)
    return instruction


def instruction_listening_thread(sock, gui):
    while True:
        try:
            instruction = get_instruction_from_server(sock)
        except (ConnectionResetError, ConnectionAbortedError) as exc:
            logger.info('Server closed')
            #gui.reset()
            gui.event_generate('<<AppReset>>')
            break
        except JSONDecodeError as exc:
            traceback.print_exc()
            continue
        except:
            logger.error('Error while getting data from server')
            traceback.print_exc()
            break
        else:
            if type(instruction) is dict:
                #gui.set_fsm_info(instruction)
                gui.save_config(instruction)
            else:
                try:
                    #gui.execute_instruction(instruction)
                    gui.instruction_queue.put(instruction)
                    gui.event_generate('<<instruction>>')
                except:
                    logger.error('Error while executing instruction')
                    traceback.print_exc()
                    break


def connecting_thread(sock, gui):
    for _ in range(10):
        try:
            sock.connect(SERVER_ADDRESS)
        except ConnectionRefusedError:
            logger.info('Connecting...')
            time.sleep(0.1)
        else:
            #gui.activate()
            gui.event_generate('<<activate>>')
            break
    else:
        logger.error('Couldn\'t connect to server')
        gui.reset()


def _placeholder():
    pass


class FSMRuntimeApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master.title('FSM GUI: Traffic Lights')
        self.master.minsize(700, 450)
        self.master.maxsize(1600, 900)
        self.master.protocol("WM_DELETE_WINDOW", self.exit)
        self.configure(bg='white')

        self.bind('<<app_reset>>', self.reset)
        self.bind('<<set_config>>', self.set_fsm_info)
        self.bind('<<activate>>', self.activate)
        self.bind('<<instruction>>', self.execute_instruction)

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
        self.style.configure('Timer.TLabel', foreground='black', background=app_colors['bg'], justify=tk.RIGHT, width=2, height=1, padding=10, font=self.FONTS['oldstyle'])
        self.style.configure('TFrame', background=app_colors['bg'])
        self.style.configure('Thick.TFrame', background=app_colors['warning'], borderwidth=2)
        self.style.configure('TButton', background=app_colors['primary'], foreground='black', padding=10, font=self.FONTS['normal'])
        self.style.configure('TNotebook.Tab', background='light blue', focuscolor=self.style.configure('.')['background'])
        self.style.configure('TNotebook', background='white')
        self.style.map('TNotebook.Tab',
                       background=[('selected', 'white'), ],
                       focuscolor=[('selected', 'white'), ])

        menu_bar = tk.Menu(self.master)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='Open', command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label='Settings', command=_placeholder)  # TODO: add settings popup window
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.exit)
        menu_bar.add_cascade(label='File', menu=file_menu)

        helpmenu = tk.Menu(menu_bar, tearoff=0)
        helpmenu.add_command(label='About...', command=_placeholder)  # TODO: add About popup window
        menu_bar.add_cascade(label='Help', menu=helpmenu)

        self.master.config(menu=menu_bar)

        self.instruction_queue = Queue()
        self.sock = None
        self.fsm_filename = None
        self.active = False
        self.dynamic_visualization = False
        self.graph_images = dict()
        self.timer_thread = timer.TimerThread(self)
        self.timer_thread.daemon = True
        self.server_process = None
        self.config_is_set = False
        self.fsm_config = None

        col_count, row_count = self.grid_size()

        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        for row in range(row_count):
            self.grid_rowconfigure(row, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        self.timeout_var = tk.IntVar()
        self.title_var = tk.StringVar()
        self.description_var = tk.StringVar()

        self.title_frame = tk.Frame(self, borderwidth=2, relief=tk.RIDGE, width=500, height=500, bg='blue')
        self.title_label = ttk.Label(self.title_frame, textvariable=self.title_var, style='Header.TLabel')
        #self.title_label.grid(row=0, column=0)
        self.title_label.pack()
        self.title_frame.grid(row=0, column=0)

        self.description_frame = tk.Frame(self, borderwidth=2, relief=tk.RIDGE, width=500, height=500, bg='green')
        self.description_label = ttk.Label(self.description_frame, textvariable=self.description_var)
        #self.description_label.grid(row=0, column=1, columnspan=3)
        self.description_label.pack()
        self.description_frame.grid(row=0, column=1, columnspan=3)

        #self.timer_display_default = TimerDisplay(self, 0, self.timeout_var)
        #self.timer_display_default = ttk.Label(self, font='Courier 18 bold',  textvariable=self.timeout_var)
        #self.timer_display_frame = ttk.Frame(self, borderwidth=2, width=300, height=300, style='Thick.TFrame')
        self.timer_display_frame = tk.Frame(self, borderwidth=2, relief=tk.RIDGE, width=500, height=500, bg='yellow')
        self.timer_display_default = ttk.Label(self.timer_display_frame, textvariable=self.timeout_var, style='Timer.TLabel')
        self.timer_display_default.pack(pady=20, padx=20)
        self.timer_display_frame.grid(row=0, column=5)
        #self.timer_display_frame.configure(height=self.timer_display_frame["height"], width=self.timer_display_frame["width"])
        self.timer_display_frame.grid_propagate(0)

        self.graph_image_frame = ttk.Frame(self, width=700, height=700, style='TFrame')
        self.graph_image_lbl = ttk.Label(self.graph_image_frame, style='TLabel')
        #self.graph_image_lbl.grid(row=0, column=6, rowspan=6, columnspan=6)
        self.graph_image_lbl.pack()
        self.graph_image_frame.grid(row=0, column=6, rowspan=6, columnspan=6)

        #self.timer_progressbar = ttk.Progressbar()

        #self.switch_app_button = tk.Button(self, text='Edit', command=self.switch_app)
        #self.switch_app_button.grid(row=0, column=2)

        self.tab_control = ttk.Notebook(self, style='TNotebook')
        self.init_tab_traffic(self.tab_control)
        self.init_tab_elevator(self.tab_control)
        self.tab_control.grid(row=1, column=0, rowspan=4, columnspan=6, padx=0, pady=0)

        self.output_console_frame = ttk.Frame(self, style='TFrame')
        self.output_console_frame.grid(row=5, column=0, rowspan=2, columnspan=6, padx=0, pady=0)

        self.pack()

        self.buttons_dict = {
            'button1': self.input_btn_1,
            'button2': self.input_btn_2,
            'button3': self.input_btn_3,
            'button4': self.input_btn_4,
            'button5': self.input_btn_5,
            'button6': self.input_btn_6,
        }

        self.widgets_dict = {
            'p1': self.pedestrian_lights_list[0],
            'p2': self.pedestrian_lights_list[1],
            'p3': self.pedestrian_lights_list[2],
            'p4': self.pedestrian_lights_list[3],
            'p5': self.pedestrian_lights_list[4],
            'p6': self.pedestrian_lights_list[5],

            't1': self.traffic_lights_list[0],
            't2': self.traffic_lights_list[1],
            't3': self.traffic_lights_list[2],
            't4': self.traffic_lights_list[3],
            't5': self.traffic_lights_list[4],
            't6': self.traffic_lights_list[5],
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

    def init_tab_traffic(self, tab_control):
        self.tab_traffic = ttk.Frame(tab_control, style='TFrame', width=700, height=500)

        col_count, row_count = self.tab_traffic.grid_size()
        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        for row in range(row_count):
            self.grid_rowconfigure(row, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        self.tab_control.add(self.tab_traffic, text='Traffic lights')

        self.traffic_lights_list = [TrafficLight(self.tab_traffic, 0, i, tl_dimensions, tl_colors) for i in range(6)]
        self.pedestrian_lights_list = [PedestrianLight(self.tab_traffic, 1, i, tl_dimensions, tl_colors) for i in range(6)]

        """ Buttons section """
        #self.buttons_frame = tk.Frame(self.tab_traffic)
        self.input_btn_1 = ttk.Button(self.tab_traffic, state=tk.DISABLED, text='button1', command=lambda: self.send_event('button1'), style='TButton')
        self.input_btn_1.grid(row=2, column=0, padx=5, pady=5)
        self.input_btn_2 = ttk.Button(self.tab_traffic, state=tk.DISABLED, text='button2', command=lambda: self.send_event('button2'), style='TButton')
        self.input_btn_2.grid(row=2, column=1, padx=5, pady=5)
        self.input_btn_3 = ttk.Button(self.tab_traffic, state=tk.DISABLED, text='button3', command=lambda: self.send_event('button3'), style='TButton')
        self.input_btn_3.grid(row=2, column=2, padx=5, pady=5)
        self.input_btn_4 = ttk.Button(self.tab_traffic, state=tk.DISABLED, text='button4', command=lambda: self.send_event('button4'), style='TButton')
        self.input_btn_4.grid(row=2, column=3, padx=5, pady=5)
        self.input_btn_5 = ttk.Button(self.tab_traffic, state=tk.DISABLED, text='button5', command=lambda: self.send_event('button5'), style='TButton')
        self.input_btn_5.grid(row=2, column=4, padx=5, pady=5)
        self.input_btn_6 = ttk.Button(self.tab_traffic, state=tk.DISABLED, text='button6', command=lambda: self.send_event('button6'), style='TButton')
        self.input_btn_6.grid(row=2, column=5, padx=5, pady=5)
        #self.buttons_frame.grid(row=3, column=0, columnspan=6, pady=5)
        """ === """

    def init_tab_elevator(self, tab_control):
        self.tab_elevator = ttk.Frame(tab_control, style='TFrame', width=700, height=500)

        col_count, row_count = self.tab_elevator.grid_size()
        for col in range(col_count):
            self.grid_columnconfigure(col, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        for row in range(row_count):
            self.grid_rowconfigure(row, minsize=tl_dimensions['canvas_size'] + tl_dimensions['padding'])

        self.tab_control.add(self.tab_elevator, text='Elevator')

    def update_timer(self, timeout_seconds):
        self.timeout_var.set(timeout_seconds)

    def send_event(self, event):
        if self.active:
            event_dict = {
                'event': event,
            }
            event_json = json.dumps(event_dict)
            self.sock.send(bytes(event_json, encoding='utf-8'))
            #self.queue.put(event)

    def timeout_event(self):
        self.update_timer(0)
        self.send_event('timeout')

    def execute_instruction(self, event):
        instr = self.instruction_queue.get()
        if not self.config_is_set:
            self.switch_all_widgets(True)
            self.switch_all_buttons(True)
            self.config_is_set = True
        if instr[0] == 'state':
            logger.debug(f'GUI: state changed to {instr[1]}')
            self.switch_graph_image(instr[1])
        elif instr[0] == 'set_timeout':
            self.timer_thread.set_timer(instr[1])
        elif instr[0] in self.instructions_dict:
            self.instructions_dict[instr[0]]()
        else:
            logger.debug(f'GUI: unknown instruction: {instr[0]}')

    def reset(self):
        logger.debug('Reset called')
        if self.active:
            self.fsm_filename = None
            self.active = False
            self.server_process.kill()
            for widget in (self.traffic_lights_list + self.pedestrian_lights_list):
                widget.reset()
            if self.sock:
                self.sock.close()
                self.sock = None
            self.timer_thread.reset_timer()
            self.timeout_var.set(0)
            self.title_var.set('')
            self.description_var.set('')
            self.graph_image_lbl.configure(image='')
            self.graph_images = dict()
            self.dynamic_visualization = False
            self.switch_all_widgets(False)
            self.switch_all_buttons(False)
            self.fsm_config = None
            self.config_is_set = False
            logger.info(f'App is reset')

    def open_file(self):
        init_dir = os.path.abspath(os.path.dirname(sys.argv[0])).replace('\\', '/') + '/python_fsm_generated'
        filename = filedialog.askopenfilename(
            initialdir=init_dir,
            filetypes=(('Python source files', '*.py'),)
        )
        if filename:
            if filename[-3:] != '.py':
                logger.error(f'File provided is not a Python source file: {filename}')
                # TODO: add error popup
            else:
                logger.info(f'Opening file: {filename}')
                self.load_file(filename)

    def load_file(self, filename):
        fsm_name = os.path.basename(filename)
        # logger.debug(fsm_name)

        if fsm_name:
            self.reset()
            self.fsm_filename = fsm_name
            self.start_server(filename)
            self.load_images(self.fsm_filename)
            if self.graph_images:
                self.switch_graph_image('_base')
            self.after(10, self.connect)

    def load_images(self, fsm_name):
        images_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'generated_graph_images', fsm_name[:-3])

        base_graph_found = False

        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                ext = os.path.splitext(filename)[-1].lower()
                if ext in {'.png', '.jpg', '.svg'}:
                    image_path = os.path.join(images_dir, filename)
                    if filename[:-4] == '_base':
                        #self.graph_images['_base'] = self.load_image(filename)
                        base_graph_found = True
                        logger.debug(f'Base graph image found')
                    try:
                        self.graph_images[filename[:-4]] = load_image(image_path)

                        #self.graph_images[filename[:-4]] = tk.PhotoImage(file=image_path)
                    except Exception as exc:
                        logger.warning(f'Couldn\'t open graph image {filename[:-4]}')
                        #print(exc)
                    else:
                        logger.debug(f'Graph image for state {filename[:-4]} added')
            if not base_graph_found:
                logger.warning(f'Base graph image for {fsm_name} found')
        else:
            logger.warning(f'Graph images directory for {fsm_name[:-3]} not found')
            logger.warning(f'Tried: {images_dir}')
        logger.debug('Available images loaded')

    def switch_graph_image(self, state_name):
        if self.active:
            if state_name in self.graph_images:
                img = self.graph_images[state_name]
                logger.debug(f'GUI: graph image switched to {state_name}')
            else:
                img = self.graph_images['_base']
                logger.debug(f'GUI: graph defaulted to base')

            self.graph_image_lbl.configure(image=img)

    def start_server(self, filename):
        # test_process = subprocess.Popen(['ls', '--help'])
        # logger.debug(f"Command: {['python', 'fsm_server_python.py', '--visual', filename]}")

        try:
            self.server_process = subprocess.Popen(['python', 'fsm_server_python.py', '--visual', filename])
        except FileNotFoundError:
            self.server_process = subprocess.Popen(['python3', 'fsm_server_python.py', '--visual', filename])

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            Thread(target=connecting_thread, args=(self.sock, self), daemon=True).start()
        except:
            logger.error("Error while starting connecting thread")
            traceback.print_exc()

    def switch_all_widgets(self, active: bool):
        if active:
            for instruction in self.widgets_dict:
                self.widgets_dict[instruction].activate()
        else:
            for instruction in self.widgets_dict:
                self.widgets_dict[instruction].disable()

    def switch_all_buttons(self, active: bool):
        if active:
            for event in self.buttons_dict:
                button = self.buttons_dict[event]
                button.configure(state=tk.NORMAL)
        else:
            for event in self.buttons_dict:
                button = self.buttons_dict[event]
                button.configure(state=tk.DISABLED)

    def save_config(self, config):
        self.fsm_config = config
        self.event_generate('<<set_config>>')

    def set_fsm_info(self, event):
        self.config_is_set = True
        if 'title' in self.fsm_config:
            self.title_var.set(self.fsm_config['title'])
        if 'description' in self.fsm_config:
            self.description_var.set(self.fsm_config['description'])
        if 'instructions_set' in self.fsm_config:
            logger.debug(f'GUI got instructions set:')
            for instruction in self.fsm_config['instructions_set']:
                logger.debug(f'instruction: {instruction}')
                if instruction[:2] in self.widgets_dict:
                    self.widgets_dict[instruction[:2]].activate()
                    logger.debug(f'{instruction[:2]} - canvas hidden')
        else:
            logger.debug(f'No instructions set provided:')
            self.switch_all_widgets(True)
        if 'events_set' in self.fsm_config:
            logger.debug(f'GUI got events set:')
            for event in self.fsm_config['events_set']:
                logger.debug(f'event: {event}')
                if event == 'timeout':
                    continue
                elif event.startswith('button'):
                    if event in self.buttons_dict:
                        button = self.buttons_dict[event]
                        button.configure(state=tk.NORMAL)
        else:
            logger.debug(f'No events set provided:')
            self.switch_all_buttons(True)

    def activate(self, event):
        #logger.debug('App activated')
        if self.server_process:
            if not self.timer_thread.is_alive():
                self.timer_thread.start()
            self.title_var.set(self.fsm_filename)
            try:
                Thread(target=instruction_listening_thread, args=(self.sock, self), daemon=True).start()
            except:
                logger.error("Error while starting listening thread")
                traceback.print_exc()
            logger.info('Connected to server')
            self.active = True

    def exit(self):
        if self.server_process:
            if type(self.server_process) is not subprocess.CompletedProcess:
                self.server_process.kill()
        self.master.quit()


def start_admin():
    app = FSMRuntimeApp()
    app.mainloop()
