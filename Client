from Tkinter import *
from ScrolledText import*
import select
import socket

class GUIClient:
    def __init__(self):
        self.master = Tk()

        frame = Frame(self.master)
        frame.pack()

        bottom_frame = Frame(self.master)
        bottom_frame.pack(side=BOTTOM)

        right_frame = Frame(self.master)
        right_frame.pack(side=RIGHT)

        self.send_entry = Entry(bottom_frame)
        self.send_entry.pack()

        self.name_entry = Entry(right_frame)
        self.name_entry.pack()

        self.gettext = ScrolledText(frame, height=10, width=100)
        self.gettext.pack()
        self.gettext.insert(END, 'Welcome to the Chat Server')

        b = Button(bottom_frame, text="Send", width=8, command=self.callback)
        b.pack()

        qb = Button(right_frame, text="Quit", width=8, command=self.quit)
        qb.pack()

        self.cb = Button(right_frame, text="Connect", width=8, command=self.connect)
        self.cb.pack()


    def connect(self):
        if(self.name_entry.get()!= ''):
            self.client_socket = socket.socket()
            self.client_socket.connect(('127.0.0.1', 8820))
            self.client_socket.send("ClientName:" + self.name_entry.get())
            self.name_entry.delete(0, 'end')
            self.cb.destroy()
            self.name_entry.destroy()
            self.text_to_send = None

            self.master.after(10, self.iteration)

    def MainLoop(self):
        mainloop()

    def iteration(self):
        if self.text_to_send != None and self.text_to_send != "":
            self.client_socket.send(self.text_to_send)
            self.text_to_send = None

        rlist, wlist, xlist = select.select([self.client_socket], [self.client_socket], [], 0.1)

        for current_socket in rlist:
            message = self.client_socket.recv(1024)
            self.gettext.insert(END, '\n' + message)
        self.master.after(10, self.iteration)

    def callback(self):
        self.text_to_send = self.send_entry.get()
        if(self.text_to_send!=''):
            self.gettext.insert(END, '\nYou:' + self.text_to_send)
        self.send_entry.delete(0, 'end')

    def quit(self):
        self.client_socket.send("Quit:Quit")
        self.text_to_send = None
        self.master.destroy()

def main():
    gui_obj = GUIClient()
    gui_obj.MainLoop()

if __name__ == '__main__':
    main()
