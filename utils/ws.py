import os

from .lxlog import get_logger
from .lxkey import LinxPostosInfoKey, LinxPostosKeyRequest

class WS:
	def __init__(self, *args, **kwargs):
		self.log = get_logger(level=10)
		self.key = {}

	def load_key(self, dir_name):
		if os.path.exists(os.sep.join([dir_name, 'linxpostospos.key'])):
			self.log.info('Carregando chave de ativação')
			self.key = LinxPostosInfoKey(self.log)
			self.key.load(True)
		else:
			self.log.error('Chave de ativação linxpostospos.key não existe!')

	def download_key(self, key_info):
		self.log.info('Baixando chave de ativação')
		self.key = LinxPostosKeyRequest(self.log).get_key(key_info)
