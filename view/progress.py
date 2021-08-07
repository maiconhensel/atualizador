import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import pygubu
import threading
import time
from PIL import Image
from PIL import ImageTk
from tkinter import messagebox

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_UI = os.path.join(PROJECT_PATH, "progress.ui")

class ProgressApp:
    def __init__(self, master=None):
        # build ui
        self.toplevel1 = tk.Tk() if master is None else tk.Toplevel(master)
        self.frame2 = tk.Frame(self.toplevel1)
        self.label1 = tk.Label(self.frame2)
        
        self.toplevel1.resizable(1,  1)
        self.toplevel1.overrideredirect(1)

        img = Image.open(os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'logo-linx.png']))
        self.logolinx_png =  ImageTk.PhotoImage(img)
        self.label1.configure(background='#5B2E90', image=self.logolinx_png, text='')
        self.label1.grid(column='0', row='0', rowspan='4', sticky='w')
        self.label1.rowconfigure('0', pad='0')
        self.label1.columnconfigure('1', pad='0')
        self.progressbar1 = ttk.Progressbar(self.frame2)
        self.status_progress = tk.IntVar(value=50)
        self.progressbar1.configure(length='552', orient='horizontal', value='50', variable=self.status_progress)
        self.progressbar1.grid(column='0', columnspan='2', ipady='8', row='6', sticky='w')
        self.progressbar1.rowconfigure('6', pad='0')
        self.progressbar1.columnconfigure('1', pad='0')
        self.label5 = tk.Label(self.frame2)
        self.produto_txt = tk.StringVar(value='Linx Postos POS')
        self.label5.configure(anchor='e', background='#5B2E90', font='{Segoe UI} 20 {bold}', foreground='#ffffff')
        self.label5.configure(justify='right', text='Linx Postos POS', textvariable=self.produto_txt)
        self.label5.grid(column='1', row='0', sticky='e')
        self.label5.grid_propagate(0)
        self.label5.columnconfigure('1', pad='0')
        self.label6 = tk.Label(self.frame2)
        self.versao_txt = tk.StringVar(value='1.1.1.1')
        self.label6.configure(anchor='e', background='#5B2E90', font='{Segoe UI} 12 {}', foreground='#FF7100')
        self.label6.configure(text='1.1.1.1', textvariable=self.versao_txt)
        self.label6.grid(column='1', row='1', sticky='e')
        self.label6.columnconfigure('1', pad='0')
        self.label7 = tk.Label(self.frame2)
        self.status_txt = tk.StringVar(value='Iniciando atualizacao...')
        self.label7.configure(anchor='e', background='#5B2E90', font='{Segoe UI} 12 {}', foreground='#ffffff')
        self.label7.configure(text='Iniciando atualizacao...', textvariable=self.status_txt)
        self.label7.grid(column='0', columnspan='2', ipady='0', pady='3', row='5', sticky='e')
        self.label7.rowconfigure('4', pad='0')
        self.label7.rowconfigure('5', minsize='0', pad='0', weight='0')
        self.label7.columnconfigure('1', pad='0')
        self.label8 = tk.Label(self.frame2)
        self.label8.configure(background='#5B2E90', height='3')
        self.label8.grid(column='1', row='3')
        self.label8.grid_propagate(0)
        self.label8.rowconfigure('3', pad='0')
        self.label8.columnconfigure('1', pad='0')
        self.frame2.configure(background='#5B2E90', height='225', padx='20', pady='2')
        self.frame2.configure(width='600')
        self.frame2.grid(column='0', row='0')
        self.frame2.grid_propagate(0)
        self.toplevel1.configure(height='225', relief='flat', width='600')
        windowWidth = 600
        windowHeight = 225
        
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.toplevel1.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.toplevel1.winfo_screenheight()/2 - windowHeight/2)
        
        # Positions the window in the center of the page.
        self.toplevel1.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))
        
        #self.toplevel1.geometry('600x225+522+385')
        self.toplevel1.title('Atualizador')

        # Main widget
        self.mainwindow = self.toplevel1

    def run(self):
        #threading.Thread(target=self.mainwindow.mainloop).start()
        self.mainwindow.mainloop()
    
    def stop(self):
        #threading.Thread(target=self.mainwindow.mainloop).start()
        self.mainwindow.quit()
    
    def set_statusbar_percent(self, value):
        self.status_progress.set(value)

    def set_status_txt(self, text):
        self.status_txt.set('Total %.2f%%' % text)

if __name__ == '__main__':
    app = ProgressApp()
    app.run()

