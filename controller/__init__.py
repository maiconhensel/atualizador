import os
import time
import threading
import traceback

from .downloader import Downloader

class Atualizador:
	def __init__(self, ws, parent, *args, **kwargs):
		self.ws = ws
		self.parent = parent
		self.main_dir = parent.main_dir

		self.set_status_txt = self.parent.set_status_txt
		self.set_statusbar_percent = self.parent.set_statusbar_percent

	def download(self):
		self.ws.log.info('Iniciando Download')

		dir_name = os.sep.join([self.main_dir, 'update'])
		if not os.path.exists(dir_name):
			try:
				self.ws.log.info('Criando o diretório %s' % dir_name)
				os.mkdir(dir_name)
			except:
				self.ws.log.error(traceback.format_exc())
				raise Exception('Falha ao criar o diretório %s' % dir_name)

		D = Downloader(self.ws, self)
		D.download_version()
		
	def update(self):
		self.ws.log.info('Iniciando Update')
		return

		if not os.path.exists(os.sep.join([self.main_dir, 'update'])):
			self.ws.log.error('Diretório update não existe')
			return

		f = open(os.sep.join([self.main_dir, 'update', 'md5.json']), 'r')

		for i in f.readlines():
			self.ws.log.info(i)
			time.sleep(.1)
			self.parent.set_statusbar_percent(i)
			self.parent.set_status_txt(float(i.strip()))
	

