import os
import time
import threading
from tkinter import messagebox
from view.progress import ProgressApp

class Atualizador:
	def __init__(self, ws, current_dir, *args, **kwargs):
		self.ws = ws
		self.current_dir = current_dir
		self.statusView = ProgressApp()

	def download(self):
		threading.Thread(target=self.download_aux).start()
		self.statusView.run()

	def download_aux(self):
		self.ws.log.info('Iniciando Download')

		if not os.path.exists(os.sep.join([self.current_dir, 'update'])):
			os.mkdir(os.sep.join([self.current_dir, 'update']))

		f = open(os.sep.join([self.current_dir, 'update', 'md5.json']), 'w')
		for i in range(100):
			self.ws.log.info(i)
			f.write(str(i) + '\n')
			time.sleep(.1)
			self.statusView.set_statusbar_percent(i)
			self.statusView.set_status_txt(i)

		f.close()
		self.statusView.stop()
		
	def update(self):
		threading.Thread(target=self.update_aux).start()
		self.statusView.run()

	def update_aux(self):
		self.ws.log.info('Iniciando Update')

		if not os.path.exists(os.sep.join([self.current_dir, 'update'])):
			self.ws.log.error('Diretório update não existe')
			return

		f = open(os.sep.join([self.current_dir, 'update', 'md5.json']), 'r')

		for i in f.readlines():
			self.ws.log.info(i)
			time.sleep(.1)
			self.statusView.set_statusbar_percent(i)
			self.statusView.set_status_txt(float(i.strip()))

		messagebox.showinfo(message='Atualização concluída!')
		self.statusView.stop()
	

