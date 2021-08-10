import os
import sys
import traceback
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.ttk import Separator
import pygubu
from PIL import Image, ImageTk
from tkinter import Tk, Toplevel, LabelFrame, Label, Entry, Button, StringVar, messagebox

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_UI = os.path.join(PROJECT_PATH, "cadastro.ui")

class CadastroApp:
	def __init__(self, ws, master=None):

		self.ws = ws
		# build ui
		self.configure()

	def configure(self):
		# Main widget
		self.mainwindow = Tk()

		self.labelframe3 = LabelFrame(self.mainwindow)

		self.label2 = Label(self.labelframe3)
		self.label2.configure(anchor='w', background='#5B2E90', foreground='#ffffff', justify='right')
		self.label2.configure(padx='2', pady='2', text='CNPJ:')
		self.label2.configure(font="-family {Segoe UI} -size 9")
		self.label2.grid(column='0', row='0')

		self.label3 = Label(self.labelframe3)
		self.label3.configure(anchor='w', background='#5B2E90', foreground='#ffffff', justify='right')
		self.label3.configure(padx='2', pady='2', text='Senha:')
		self.label3.configure(font="-family {Segoe UI} -size 9")
		self.label3.grid(column='0', row='1')

		self.ed_senha = Entry(self.labelframe3)
		self.ed_senha.configure(show='•')
		self.ed_senha.grid(column='1', row='1')

		self.separator1 = Separator(self.labelframe3)
		self.separator1.configure(orient='vertical')
		self.separator1.grid(column='3', padx='4', pady='0', row='0', rowspan='4', sticky='ns')

		self.bt_consultar = Button(self.labelframe3)
		self.bt_consultar.configure(justify='center', padx='0', text='Consultar', width='17')
		self.bt_consultar.grid(column='1', row='2')
		self.bt_consultar.grid_propagate(0)
		self.bt_consultar.rowconfigure('2', pad='0')
		self.bt_consultar.bind('<1>', self.bt_consultar_clicked, add='')

		self.ed_cnpj = Entry(self.labelframe3)
		self.ed_cnpj.grid(column='1', row='0')

		self.label4 = Label(self.labelframe3)
		self.label4.configure(anchor='w', background='#5B2E90', foreground='#ffffff', justify='left')
		self.label4.configure(text='Razão Social:', width='47')
		self.label4.configure(font="-family {Segoe UI} -size 9")
		self.label4.grid(column='4', columnspan='2', padx='2', row='0')

		self.lb_razao_social = Label(self.labelframe3)
		self.razao_social = StringVar(value='')
		self.lb_razao_social.configure(anchor='w', background='#5B2E90', font='TkDefaultFont', foreground='#ffffff')
		self.lb_razao_social.configure(relief='flat', textvariable=self.razao_social, width='47')
		self.lb_razao_social.configure(font="-family {Segoe UI} -size 9 -weight bold")
		self.lb_razao_social.grid(column='4', columnspan='2', padx='2', row='1')

		self.label6 = Label(self.labelframe3)
		self.label6.configure(anchor='w', background='#5B2E90', font='TkDefaultFont', foreground='#ffffff')
		self.label6.configure(text='CNPJ:', width='23')
		self.label6.configure(font="-family {Segoe UI} -size 9")
		self.label6.grid(column='4', padx='1', row='2')

		self.lb_cnpj = Label(self.labelframe3)
		self.cnpj = StringVar(value='')
		self.lb_cnpj.configure(anchor='w', background='#5B2E90', compound='top', foreground='#ffffff')
		self.lb_cnpj.configure(textvariable=self.cnpj, width='23')
		self.lb_cnpj.configure(font="-family {Segoe UI} -size 9 -weight bold")
		self.lb_cnpj.grid(column='4', padx='1', row='3')

		self.label8 = Label(self.labelframe3)
		self.label8.configure(anchor='w', background='#5B2E90', foreground='#ffffff', text='Situação:')
		self.label8.configure(width='22')
		self.label8.configure(font="-family {Segoe UI} -size 9")
		self.label8.grid(column='5', row='2')

		self.lb_situacao = Label(self.labelframe3)
		self.situacao = StringVar(value='')
		self.lb_situacao.configure(anchor='w', background='#5B2E90', foreground='#ffffff')
		self.lb_situacao.configure(textvariable=self.situacao, width='22')
		self.lb_situacao.configure(font="-family {Segoe UI} -size 9 -weight bold")
		self.lb_situacao.grid(column='5', row='3')

		self.labelframe3.configure(background='#5B2E90', foreground='#ffffff', height='120', text='Cadastro')
		self.labelframe3.configure(width='526')
		self.labelframe3.grid(column='0', row='1')
		self.labelframe3.grid_propagate(0)

		self.labelframe4 = LabelFrame(self.mainwindow)
		self.labelframe4.configure(background='#5B2E90', foreground='#ffffff', height='327', padx='2')
		self.labelframe4.configure(text='Produtos', width='526')
		self.labelframe4.grid(column='0', row='2')
		self.labelframe4.grid_propagate(0)

		self.mainwindow.configure(background='#5B2E90', height='200', padx='5', pady='3')
		#self.mainwindow.configure(width='200')
		
		# Centraliza a aplicação na tela.
		windowWidth = 536
		windowHeight = 455
		positionRight = int(self.mainwindow.winfo_screenwidth()/2 - windowWidth/2)
		positionDown = int(self.mainwindow.winfo_screenheight()/2 - windowHeight/2)
		self.mainwindow.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))

		self.mainwindow.maxsize(windowWidth, windowHeight)
		self.mainwindow.minsize(windowWidth, windowHeight)
		self.mainwindow.resizable(False, False)
		self.mainwindow.title('Linx Postos Installer')

		logo_icon = os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'logo.ico'])
		self.ws.log.info(logo_icon)
		self.mainwindow.iconbitmap(logo_icon)

		self.bt_produto_map = {}

	def make_bt_produto(self, bt_name, produto, row, column):
		bt_name = 'bt_%s' % bt_name
		bt_name = 'bt_%s' % bt_name
		img_name = 'bt_img_%s' % bt_name

		button = Button(self.labelframe4)

		width = height = 60
		img = Image.open(os.sep.join([getattr(sys, '_MEIPASS', '.'), 'resources', 'logo_linx.png']))

		self.ws.log.info(img)
		img = img.resize((width,height), Image.ANTIALIAS)

		photoImg =  ImageTk.PhotoImage(img)

		button.configure(anchor='center', compound='top', height='90', width='90', image=photoImg, text=produto, wraplength='85')
		button.grid(row=row, column=column, padx='3', pady='3')

		self.bt_produto_map[bt_name] = (button, photoImg)

	def bt_consultar_clicked(self, event=None):
		cnpj = self.ed_cnpj.get()
		senha = self.ed_senha.get()

		try:
			self.ws.download_key({'empresa_cnpj': cnpj, 'senha': senha, 'host_name': self.ws.hostname, 'host_key': self.ws.sys_key})
		except Exception as e:
			self.ws.log.error(traceback.format_exc())
			messagebox.showerror(parent=self.mainwindow, title='Ocorreu um erro', message=str(e), icon='error')
			return

		self.cnpj.set(self.ws.key['empresa_cnpj'])
		self.razao_social.set(self.ws.key['empresa_nome'])
		self.situacao.set('Ativo' if self.ws.key['ativo'] else 'Inativo')

		for k in list(self.bt_produto_map.keys()):
			self.bt_produto_map.pop(k)[0].destroy()

		import random
		for i in range(random.randrange(0, 15)):
			self.ws.log.info(i)
			self.make_bt_produto(str(i), 'Teste', int(i/5), i%5)

	def run(self):
		self.mainwindow.mainloop()


if __name__ == '__main__':
	from utils.ws import WS
	ws = WS()
	app = CadastroApp(ws)
	app.run()

