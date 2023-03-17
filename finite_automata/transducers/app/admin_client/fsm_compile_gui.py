import sys
import tkinter as tk


class FSMCompileApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.title = tk.Label(self, text='hello world')
        self.title.pack()

        self.run_button = tk.Button(self, text='Compile & Run', command=self.switch)
        self.run_button.pack()

    def switch(self):
        pass
