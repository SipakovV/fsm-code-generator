
from datetime import datetime, timedelta
import tkinter as tk
from threading import Thread
import event_queue


class TrafficLight:
    def __init__(self, parent_frame, index):
        self.canvas = tk.Canvas(parent_frame, bg='white', height=150, width=150)
        self.canvas.grid(row=0, column=index)


class PedestrianLight:
    def __init__(self, parent_frame, index):
        self.canvas = tk.Canvas(parent_frame, bg='white', height=150, width=150)
        self.canvas.grid(row=1, column=index)

        self.border = self.canvas.create_rectangle(50, 25, 100, 125, outline='black')
        self.red_light = self.canvas.create_oval(55, 30, 95, 70, fill='')
        self.green_light = self.canvas.create_oval(55, 80, 95, 120, fill='')

    def set_red(self):
        self.canvas.itemconfig(self.red_light, fill='red')
        self.canvas.itemconfig(self.green_light, fill='')

    def set_green(self):
        self.canvas.itemconfig(self.red_light, fill='')
        self.canvas.itemconfig(self.green_light, fill='green')

    def set_green_blinking(self):
        self.canvas.itemconfig(self.red_light, fill='')
        self.canvas.itemconfig(self.green_light, fill='yellow')


class TimerDisplay:
    def __init__(self, parent_frame, index):
        self.canvas = tk.Canvas(parent_frame, bg='white', height=150, width=150)
        self.canvas.grid(row=2, column=index)

        self.border = self.canvas.create_rectangle(50, 25, 100, 125, outline='black')
        self.label = self.canvas.create_text(75, 50, text='-', fill='black', font='Verdana 15')

        self.counter = 0

    def set(self, countdown_seconds):
        self.counter = countdown_seconds
        self.canvas.itemconfig(self.label, text=countdown_seconds)


class App(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def button_input1(self):
        event_queue.publish_event('button1')

    def check_outputs(self):
        instr = event_queue.get_instruction()
        if instr:
            #self.label.config(text=instr)
            command, value = instr
            if command == 'set_timeout':
                self.timeout = datetime.now() + timedelta(seconds=value)
                self.root.after(10, self.timer)
            elif command == 'p1_red':
                self.pedestrian_light_1.set_red()
            elif command == 'p1_green':
                self.pedestrian_light_1.set_green()
            elif command == 'p1_blinking':
                self.pedestrian_light_1.set_green_blinking()

        self.root.after(100, self.check_outputs)

    def timer(self):
        if self.timeout > datetime.now():
            time_remaining = (self.timeout - datetime.now()).seconds
            #self.timer_display.config(text=time_remaining)
            self.timer_display_default.set(time_remaining)
            self.root.after(100, self.timer)
        else:
            event_queue.publish_event('timeout')

    def run(self):
        self.timeout = None

        self.root = tk.Tk()
        self.root.resizable(width=True, height=True)
        self.root.title('FSM GUI: Traffic lights')
        self.root.geometry('900x700')
        self.root.protocol('WM_DELETE_WINDOW', self.callback)

        self.main_frame = tk.Frame(self.root)

        self.label = tk.Label(self.root, text='Hello World')
        self.label.pack()

        """ Traffic lights section """
        self.traffic_frame = tk.Frame(self.main_frame)

        self.traffic_light_1 = TrafficLight(self.traffic_frame, 0)
        #self.traffic_light_2 = TrafficLight(self.traffic_frame, 1)
        #self.traffic_light_3 = TrafficLight(self.traffic_frame, 2)
        #self.traffic_light_4 = TrafficLight(self.traffic_frame, 3)
        #self.traffic_light_5 = TrafficLight(self.traffic_frame, 4)

        self.traffic_frame.grid(row=0, column=0)
        """ === """

        """ Pedestrian lights section """
        self.pedestrian_frame = tk.Frame(self.main_frame)

        self.pedestrian_light_1 = PedestrianLight(self.pedestrian_frame, 0)
        #self.pedestrian_light_2 = PedestrianLight(self.pedestrian_frame, 1)
        #self.pedestrian_light_3 = PedestrianLight(self.pedestrian_frame, 2)
        #self.pedestrian_light_4 = PedestrianLight(self.pedestrian_frame, 3)
        #self.pedestrian_light_5 = PedestrianLight(self.pedestrian_frame, 4)

        self.pedestrian_frame.grid(row=1, column=0)
        """ === """

        """ Pedestrian lights section """
        self.timer_display_frame = tk.Frame(self.main_frame)

        self.timer_display_default = TimerDisplay(self.timer_display_frame, 0)
        #self.timer_display_2 = TimerDisplay(self.timer_display_frame, 1)
        #self.timer_display_3 = TimerDisplay(self.timer_display_frame, 2)
        #self.timer_display_4 = TimerDisplay(self.timer_display_frame, 3)
        #self.timer_display_5 = TimerDisplay(self.timer_display_frame, 4)

        self.timer_display_frame.grid(row=2, column=0)
        """ === """

        """ Buttons section """
        self.buttons_frame = tk.Frame(self.main_frame)
        self.input_btn_1 = tk.Button(self.buttons_frame, text='Input button', command=self.button_input1, height=3, width=15)
        self.input_btn_1.grid(row=0, column=0)
        self.buttons_frame.grid(row=3, column=0)
        """ === """

        self.main_frame.pack()

        self.root.after(10, self.check_outputs)
        self.root.mainloop()


'''
if __name__ == '__main__':
    app = App()
    #main()
'''
