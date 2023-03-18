import tkinter as tk


class TrafficLight:
    def __init__(self, parent_frame, index, dimensions, colors):

        self.CANVAS_SIZE = dimensions['canvas_size']
        self.LAMP_SIZE = dimensions['lamp_size']
        self.PADDING_SIZE = dimensions['padding']
        self.BASE_COLOR = colors['base']
        self.OFF_COLOR = colors['off']
        self.RED_COLOR = colors['red']
        self.YELLOW_COLOR = colors['yellow']
        self.GREEN_COLOR = colors['green']

        self.canvas = tk.Canvas(parent_frame, bg='white', height=self.CANVAS_SIZE, width=self.CANVAS_SIZE)
        self.canvas.grid(row=0, column=index)

        self.base = self.canvas.create_rectangle(self.CANVAS_SIZE / 2 - self.LAMP_SIZE / 2 - self.PADDING_SIZE,
                                                 self.PADDING_SIZE,
                                                 self.CANVAS_SIZE / 2 + self.LAMP_SIZE / 2 + self.PADDING_SIZE,
                                                 self.CANVAS_SIZE - self.PADDING_SIZE,
                                                 outline='black', fill=self.BASE_COLOR)
        self.red_light = self.canvas.create_oval(self.CANVAS_SIZE / 2 - self.LAMP_SIZE / 2,
                                                 self.PADDING_SIZE * 2,
                                                 self.CANVAS_SIZE / 2 + self.LAMP_SIZE / 2,
                                                 self.PADDING_SIZE * 2 + self.LAMP_SIZE,
                                                 fill=self.OFF_COLOR)
        self.yellow_light = self.canvas.create_oval(self.CANVAS_SIZE / 2 - self.LAMP_SIZE / 2,
                                                    self.PADDING_SIZE * 3 + self.LAMP_SIZE,
                                                    self.CANVAS_SIZE / 2 + self.LAMP_SIZE / 2,
                                                    self.PADDING_SIZE * 3 + self.LAMP_SIZE * 2,
                                                    fill=self.OFF_COLOR)
        self.green_light = self.canvas.create_oval(self.CANVAS_SIZE / 2 - self.LAMP_SIZE / 2,
                                                   self.PADDING_SIZE * 4 + self.LAMP_SIZE * 2,
                                                   self.CANVAS_SIZE / 2 + self.LAMP_SIZE / 2,
                                                   self.PADDING_SIZE * 4 + self.LAMP_SIZE * 3,
                                                   fill=self.OFF_COLOR)

    def set_red(self):
        self.canvas.itemconfig(self.red_light, fill=self.RED_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=self.OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill=self.OFF_COLOR)

    def set_yellow_red(self):
        self.canvas.itemconfig(self.red_light, fill=self.RED_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=self.YELLOW_COLOR)
        self.canvas.itemconfig(self.green_light, fill=self.OFF_COLOR)

    def set_yellow(self):
        self.canvas.itemconfig(self.red_light, fill=self.OFF_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=self.YELLOW_COLOR)
        self.canvas.itemconfig(self.green_light, fill=self.OFF_COLOR)

    def set_green(self):
        self.canvas.itemconfig(self.red_light, fill=self.OFF_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=self.OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill=self.GREEN_COLOR)

    def set_green_blinking(self):
        self.canvas.itemconfig(self.red_light, fill=self.OFF_COLOR)
        self.canvas.itemconfig(self.yellow_light, fill=self.OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill='cyan')


class PedestrianLight:
    def __init__(self, parent_frame, index, dimensions, colors):
        self.CANVAS_SIZE = dimensions['canvas_size']
        self.LAMP_SIZE = dimensions['lamp_size']
        self.PADDING_SIZE = dimensions['padding']
        self.BASE_COLOR = colors['base']
        self.OFF_COLOR = colors['off']
        self.RED_COLOR = colors['red']
        self.YELLOW_COLOR = colors['yellow']
        self.GREEN_COLOR = colors['green']

        self.canvas = tk.Canvas(parent_frame, bg='white', height=150, width=150)
        self.canvas.grid(row=1, column=index)

        self.border = self.canvas.create_rectangle(50, 25, 100, 125, outline='black', fill=self.BASE_COLOR)
        self.red_light = self.canvas.create_oval(55, 30, 95, 70, fill=self.OFF_COLOR)
        self.green_light = self.canvas.create_oval(55, 80, 95, 120, fill=self.OFF_COLOR)

    def set_red(self):
        self.canvas.itemconfig(self.red_light, fill=self.RED_COLOR)
        self.canvas.itemconfig(self.green_light, fill=self.OFF_COLOR)

    def set_green(self):
        self.canvas.itemconfig(self.red_light, fill=self.OFF_COLOR)
        self.canvas.itemconfig(self.green_light, fill=self.GREEN_COLOR)

    def set_green_blinking(self):
        self.canvas.itemconfig(self.red_light, fill=self.OFF_COLOR)
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