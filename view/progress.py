import os
import sys
import pygubu
import threading
import time

from PIL import Image
from PIL.ImageTk import PhotoImage
from tkinter import Tk, Frame, Label, IntVar, StringVar, messagebox
from tkinter.ttk import Progressbar

from controller import Atualizador

class ProgressApp:
	def __init__(self, ws, main_dir, hidden=False):
		self.ws = ws
		self.main_dir = main_dir

		self.visible = not hidden

		self.configure()

	def configure(self):

		# Main widget
		self.mainwindow = Tk()

		if not self.visible:
			self.hide()

		self.frame2 = Frame(self.mainwindow)
		self.label1 = Label(self.frame2)

		self.mainwindow.resizable(1,  1)
		self.mainwindow.overrideredirect(1)

		img = Image.open(os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'logo-linx.png']))
		self.logolinx_png = PhotoImage(img)
		self.label1.configure(background='#5B2E90', image=self.logolinx_png, text='')
		self.label1.grid(column='0', row='0', rowspan='4', sticky='w')
		self.label1.rowconfigure('0', pad='0')
		self.label1.columnconfigure('1', pad='0')

		self.progressbar1 = Progressbar(self.frame2)
		self.status_progress = IntVar(value=0)
		self.progressbar1.configure(length='552', orient='horizontal', variable=self.status_progress)
		self.progressbar1.grid(column='0', columnspan='2', ipady='8', row='6', sticky='w')
		self.progressbar1.rowconfigure('6', pad='0')
		self.progressbar1.columnconfigure('1', pad='0')
		
		self.label5 = Label(self.frame2)
		self.produto_txt = StringVar(value='Linx Postos POS')
		self.label5.configure(anchor='e', background='#5B2E90', font='{Segoe UI} 20 {bold}', foreground='#ffffff')
		self.label5.configure(justify='right', text='Linx Postos POS', textvariable=self.produto_txt)
		self.label5.grid(column='1', row='0', sticky='e')
		self.label5.grid_propagate(0)
		self.label5.columnconfigure('1', pad='0')
		
		self.label6 = Label(self.frame2)
		self.versao_txt = StringVar(value='1.1.1.1')
		self.label6.configure(anchor='e', background='#5B2E90', font='{Segoe UI} 12 {}', foreground='#FF7100')
		self.label6.configure(text='1.1.1.1', textvariable=self.versao_txt)
		self.label6.grid(column='1', row='1', sticky='e')
		self.label6.columnconfigure('1', pad='0')
		
		self.label7 = Label(self.frame2)
		self.status_txt = StringVar(value='Iniciando atualizacao...')
		self.label7.configure(anchor='e', background='#5B2E90', font='{Segoe UI} 8 {}', foreground='#ffffff')
		self.label7.configure(text='Iniciando atualizacao...', textvariable=self.status_txt)
		self.label7.grid(column='0', columnspan='2', ipady='0', pady='3', row='5', sticky='e')
		self.label7.rowconfigure('4', pad='0')
		self.label7.rowconfigure('5', minsize='0', pad='0', weight='0')
		self.label7.columnconfigure('1', pad='0')
		
		self.label8 = Label(self.frame2)
		self.label8.configure(background='#5B2E90', height='3')
		self.label8.grid(column='1', row='3')
		self.label8.grid_propagate(0)
		self.label8.rowconfigure('3', pad='0')
		self.label8.columnconfigure('1', pad='0')
		
		self.frame2.configure(background='#5B2E90', height='225', padx='20', pady='2')
		self.frame2.configure(width='600')
		self.frame2.grid(column='0', row='0')
		self.frame2.grid_propagate(0)
		
		self.mainwindow.configure(relief='flat')
		
		# Positions the window in the center of the page.
		windowWidth = 600
		windowHeight = 225
		positionRight = int(self.mainwindow.winfo_screenwidth()/2 - windowWidth/2)
		positionDown = int(self.mainwindow.winfo_screenheight()/2 - windowHeight/2)
		
		self.mainwindow.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))
		
		self.mainwindow.title('Atualizador')
		self.mainwindow.protocol("WM_DELETE_WINDOW", self.exit)

		self.logo_icon = os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'logo.ico'])
		self.ws.log.info(self.logo_icon)
		self.mainwindow.iconbitmap(self.logo_icon)

	def run(self, *args, **kwargs):
		if not self.visible:
			return self.__execute(*args, **kwargs)

		threading.Thread(target=self.__execute, args=args, kwargs=kwargs, daemon=True).start()
		self.show()
		self.mainwindow.mainloop()

	def show(self):
		self.visible = True
		self.mainwindow.deiconify()

	def hide(self):
		self.visible = False
		self.mainwindow.withdraw()
	
	def exit(self):
		self.mainwindow.destroy()

	def set_statusbar_percent(self, value):
		self.status_progress.set(value)

	def set_status_txt(self, text):
		self.status_txt.set(text)
	
	def set_produto_txt(self, text):
		self.produto_txt.set(text)
	
	def set_versao_txt(self, text):
		self.versao_txt.set(text)
	
	def __execute(self, *args, **kwargs):
		self.ws.log.info('args: %r' % str(args))
		self.ws.log.info('kwargs: %r' % str(kwargs))

		self.set_produto_txt(self.ws.key['appname'])
		self.set_versao_txt('')

		A = Atualizador(self.ws, self)
		msg = ''

		if '--download' in args:
			self.ws.log.info('Parâmetro --download')
			try:
				if not A.download():
					self.exit()
				msg = 'Download concluído!'
			except Exception as e:
				messagebox.showerror(parent=self.mainwindow, title='Ocorreu um erro', message=str(e), icon='error')
				self.exit()

		if '--update' in args:
			self.ws.log.info('Parâmetro --update')
			try:
				if not A.update():
					self.exit()
				msg = 'Atualização concluída!'
			except Exception as e:
				messagebox.showerror(parent=self.mainwindow, title='Ocorreu um erro', message=str(e), icon='error')
				self.exit()

		if msg and self.visible:
			messagebox.showinfo(parent=self.mainwindow, title='Atenção', message=msg, icon='info')

		self.exit()

if __name__ == '__main__':
	app = ProgressApp()
	app.run()

