import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image


class Indicator:
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
        self.init_thumbnail()

    def disable(self):
        self.canvas.itemconfig(self.lamp, fill=self.OFF_DISABLED_COLOR)

    def enable(self):
        self.canvas.itemconfig(self.lamp, fill=self.OFF_COLOR)

    def turn_on(self):
        self.canvas.itemconfig(self.lamp, fill=self.ON_COLOR)

    def turn_off(self):
        self.canvas.itemconfig(self.lamp, fill=self.OFF_COLOR)

    def init_thumbnail(self):
        pass


class PowerIndicator(Indicator):
    def init_thumbnail(self):
        img_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'runtime_admin_app', 'resources',
                                'mw_magnetron.png')
        img = Image.open(img_path)
        width, height = img.size
        img_resized = img.resize((round(0.11 * width), round(0.11 * height)), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(img_resized)
        self.thumbnail = self.canvas.create_image(27, 26, anchor=tk.NW, image=self.img)


class LampIndicator(Indicator):
    def init_thumbnail(self):
        img_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'runtime_admin_app', 'resources',
                                'mw_lamp.png')
        img = Image.open(img_path)
        width, height = img.size
        img_resized = img.resize((round(0.08 * width), round(0.08 * height)), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(img_resized)
        self.thumbnail = self.canvas.create_image(23, 22, anchor=tk.NW, image=self.img)


class BeepIndicator(Indicator):
    def init_thumbnail(self):
        img_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'runtime_admin_app', 'resources',
                                'mw_beep.png')
        img = Image.open(img_path)
        width, height = img.size
        img_resized = img.resize((round(0.09 * width), round(0.09 * height)), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(img_resized)
        self.thumbnail = self.canvas.create_image(27, 30, anchor=tk.NW, image=self.img)
