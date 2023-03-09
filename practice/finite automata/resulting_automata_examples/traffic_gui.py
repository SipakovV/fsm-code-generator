
from datetime import datetime, timedelta
import tkinter as tk
from threading import Thread
import event_queue


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
            self.label.config(text=instr)
            command, value = instr
            if command == 'set_timeout':
                self.timeout = datetime.now() + timedelta(seconds=value)
                self.root.after(10, self.timer)

        self.root.after(100, self.check_outputs)

    def timer(self):
        if self.timeout > datetime.now():
            time_remaining = (self.timeout - datetime.now()).seconds
            self.timer_display.config(text=time_remaining)
            self.root.after(1000, self.timer)
        else:
            event_queue.publish_event('timeout')
            self.timer_display.config(text='-')

    def run(self):
        self.timeout = None

        self.root = tk.Tk()
        self.root.resizable(width=True, height=True)
        self.root.title('FSM GUI: Traffic lights')
        self.root.geometry('810x600')
        self.root.protocol('WM_DELETE_WINDOW', self.callback)

        self.frame = tk.Frame(self.root)

        self.label = tk.Label(self.frame, text='Hello World')
        self.label.pack()

        self.timer_display = tk.Label(self.frame, text='-')
        self.timer_display.pack()

        input_btn = tk.Button(self.frame, text='Input button', command=self.button_input1, height=3, width=15)
        input_btn.pack()

        self.frame.pack()

        self.root.after(10, self.check_outputs)
        self.root.mainloop()


'''
if __name__ == '__main__':
    app = App()
    #main()
'''
