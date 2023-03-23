import tkinter as tk


class PowerLamp:
    def __init__(self, parent_frame, row, col, dimensions, colors):

        self.CANVAS_SIZE = dimensions['canvas_size']
        self.LAMP_SIZE = dimensions['lamp_size']
        self.PADDING_SIZE = dimensions['padding']
        self.OFF_COLOR = colors['off_active']
        self.OFF_DISABLED_COLOR = colors['off_disabled']
        self.ON_COLOR = colors['on_active']

        self.canvas = tk.Canvas(parent_frame, bg='white', highlightthickness=0, height=self.CANVAS_SIZE, width=self.CANVAS_SIZE)
        self.canvas.grid(row=row, column=col)

        self.lamp = self.canvas.create_oval(self.PADDING_SIZE, self.PADDING_SIZE, self.LAMP_SIZE + self.PADDING_SIZE, self.LAMP_SIZE + self.PADDING_SIZE, outline='black', fill=self.OFF_COLOR)
        self.disable()

    def disable(self):
        self.canvas.itemconfig(self.lamp, fill=self.OFF_DISABLED_COLOR)

    def activate(self):
        self.canvas.itemconfig(self.lamp, fill=self.OFF_COLOR)

    def turn_on(self):
        self.canvas.itemconfig(self.lamp, fill=self.ON_COLOR)

    def turn_off(self):
        self.canvas.itemconfig(self.lamp, fill=self.OFF_COLOR)
