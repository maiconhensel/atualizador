import os
import socket

from .lxcrypto import LxCrypto
from .lxlog import get_logger
from .lxkey import LinxPostosInfoKey, LinxPostosKeyRequest

__version__ = (1, 0, 0, 0)
__version_str__  = '.'.join([str(x) for x in __version__])

class WS:
	def __init__(self, *args, **kwargs):
		self.log = get_logger(level=10)
		self.key = {}

		self.version = __version_str__
		self.sys_key = LxCrypto().get_sys_key()
		self.hostname = socket.gethostname().upper()
		self.log.info('Versão = %s' % self.version)
		self.log.info('Estação: %s' % self.hostname)
		self.log.info('Serial: %s' % self.sys_key)

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
