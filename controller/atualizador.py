import os
import time
import threading
from tkinter import messagebox

class Atualizador:
	def __init__(self, ws, parent, *args, **kwargs):
		self.ws = ws
		self.parent = parent
		self.current_dir = parent.current_dir

	def download(self):
		self.ws.log.info('Iniciando Download')

		if not os.path.exists(os.sep.join([self.current_dir, 'update'])):
			os.mkdir(os.sep.join([self.current_dir, 'update']))

		f = open(os.sep.join([self.current_dir, 'update', 'md5.json']), 'w')
		for i in range(30):
			self.ws.log.info(i)
			f.write(str(i) + '\n')
			time.sleep(.1)
			self.parent.set_statusbar_percent(i)
			self.parent.set_status_txt(i)

		f.close()
		
	def update(self):
		self.ws.log.info('Iniciando Update')

		if not os.path.exists(os.sep.join([self.current_dir, 'update'])):
			self.ws.log.error('Diretório update não existe')
			return

		f = open(os.sep.join([self.current_dir, 'update', 'md5.json']), 'r')

		for i in f.readlines():
			self.ws.log.info(i)
			time.sleep(.1)
			self.parent.set_statusbar_percent(i)
			self.parent.set_status_txt(float(i.strip()))
	

