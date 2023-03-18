import sys
import tkinter as tk


class FSMCompileApp(tk.Frame):
    def __init__(self, master=None, parent_frame=None):
        super().__init__(master)

        self.parent_frame = parent_frame

        self.title = tk.Label(self, text='hello world')
        self.title.pack()

        self.run_button = tk.Button(self, text='Compile & Run', command=self.switch_app)
        self.run_button.pack()

    def switch_app(self):
        config = {
            'title': 'hello',
            'description': 'world',
        }
        self.parent_frame.activate_runtime(config)
