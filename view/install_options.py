import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Frame, BooleanVar, Checkbutton, Label, Entry, StringVar, Button, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk

class InstallOptions(simpledialog.Dialog):
	def __init__(self, ws, parent, title, default_dict=None):
		self.ws = ws
		self.my_username = None
		self.my_password = None
		self.ret_dict = default_dict or {}
		super().__init__(parent, title)

	def body(self, toplevel2):

		self.frame1 = Frame(toplevel2)

		self.install_db = BooleanVar(value=self.ret_dict.get('install_db', True))
		self.checkbutton1 = Checkbutton(self.frame1)
		self.checkbutton1.configure(text='Instalar banco de dados', variable=self.install_db)
		self.checkbutton1.configure(activebackground='#5B2E90', activeforeground='#ffffff', background='#5B2E90')
		self.checkbutton1.configure(foreground='#ffffff', selectcolor='#5B2E90')
		self.checkbutton1.grid(column='0', columnspan='2', pady='5', row='0', sticky='w')
		self.checkbutton1.rowconfigure('0', pad='5')
		self.checkbutton1.columnconfigure('0', pad='0')

		self.create_shortcuts = BooleanVar(value=self.ret_dict.get('create_shortcuts', True))
		self.checkbutton2 = Checkbutton(self.frame1)
		self.checkbutton2.configure(text='Criar atalho na área de trabalho', variable=self.create_shortcuts)
		self.checkbutton2.configure(activebackground='#5B2E90', activeforeground='#ffffff', background='#5B2E90')
		self.checkbutton2.configure(foreground='#ffffff', selectcolor='#5B2E90')
		self.checkbutton2.grid(column='0', columnspan='2', row='1', sticky='w')
		self.checkbutton2.rowconfigure('1', pad='0')
		self.checkbutton2.columnconfigure('0', pad='0')

		self.label1 = Label(self.frame1)
		self.label1.configure(text='Diretório:', foreground='#ffffff', background='#5B2E90')
		self.label1.grid(column='0', pady='5', row='2', sticky='w')
		self.label1.columnconfigure('0', pad='0')

		self.entry2 = Entry(self.frame1)
		self.install_dir = StringVar(value=self.ret_dict.get('install_dir', ''))
		self.entry2.configure(textvariable=self.install_dir, width='25')
		self.entry2.grid(column='1', padx='1', pady='5', row='2', columnspan='2', ipady='3')

		image = Image.open(os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'bt-icone-input-busca.png']))

		self.bticoneinputbusca_png = ImageTk.PhotoImage(image)
		self.button3 = Button(self.frame1, command=self.find_directory)
		self.button3.configure(image=self.bticoneinputbusca_png)
		self.button3.grid(column='3', row='2')

		self.frame1.configure(borderwidth='2', height='150', width='400', background='#5B2E90')
		self.frame1.grid(column='0', padx='10', pady='10', row='0')

		toplevel2.configure(background='#5B2E90', height='150', width='400')

		return toplevel2

	def find_directory(self):
		selected_dir = filedialog.Directory(self, title="teste").show()
		self.ws.log.info("Diretório selecionado '%r'" % selected_dir)
		if selected_dir:
			self.install_dir.set(selected_dir.replace('/', os.sep))

	def ok_pressed(self):
		self.ws.log.info('InstallOptions: Confirmar pressionado')

		self.ret_dict = {
			'install_dir': self.install_dir.get(),
			'install_db': self.install_db.get(),
			'create_shortcuts': self.create_shortcuts.get(),
		}
		self.ws.log.info('Opções selecionadas %r' % self.ret_dict)
		self.destroy()

	def cancel_pressed(self):
		self.ws.log.info('InstallOptions: Cancelar pressionado')
		self.ret_dict = {}
		self.destroy()

	def buttonbox(self):
		self.configure(background='#5B2E90')

		image = Image.open(os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'bt-icone-check.png']))
		self.bticoneok_button = ImageTk.PhotoImage(image)

		self.ok_button = Button(self, text='Confirmar', command=self.ok_pressed)
		self.ok_button.pack(side="right", padx='15', pady='5')
		self.ok_button.configure(activebackground='#5B2E90', activeforeground='#ffffff', anchor='s', background='#5B2E90')
		self.ok_button.configure(compound='left', foreground='#ffffff')
		self.ok_button.configure(image=self.bticoneok_button, width='100')


		image = Image.open(os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'bt-icone-close.png']))
		self.bticonecancel_button = ImageTk.PhotoImage(image)

		cancel_button = Button(self, text='Cancelar', command=self.cancel_pressed)
		cancel_button.pack(side="left", padx='15', pady='5')
		cancel_button.configure(activebackground='#5B2E90', activeforeground='#ffffff', anchor='s', background='#5B2E90')
		cancel_button.configure(compound='left', foreground='#ffffff')
		cancel_button.configure(image=self.bticonecancel_button, width='100')

		self.bind("<Return>", lambda event: self.ok_pressed())
		self.bind("<Escape>", lambda event: self.cancel_pressed())
