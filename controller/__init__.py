import os
import time
import threading
import traceback

from .downloader import Downloader
from .updater import Updater

class Atualizador:
	def __init__(self, ws, parent, *args, **kwargs):
		self.ws = ws
		self.parent = parent
		self.show_message_error = parent.show_message_error
		self.main_dir = parent.main_dir

		self.set_status_txt = self.parent.set_status_txt
		self.set_statusbar_percent = self.parent.set_statusbar_percent

	def __create_dir(self, dir_name):
		if not os.path.exists(dir_name):
			try:
				self.ws.log.info('Criando o diretório %s' % dir_name)
				os.mkdir(dir_name)
			except:
				self.ws.log.error(traceback.format_exc())
				raise Exception('Falha ao criar o diretório %s' % dir_name)

	def download(self):
		self.ws.log.info('Iniciando Download')

		self.__create_dir(self.main_dir)

		dir_name = os.sep.join([self.main_dir, 'update'])
		self.__create_dir(dir_name)

		D = Downloader(self.ws, self)
		D.download_version()
		return True
		
	def update(self):

		if not os.path.exists(os.sep.join([self.main_dir, 'update'])):
			raise Exception('Diretório update não existe')

		U = Updater(self.ws, self)
		U.update()
		return True
