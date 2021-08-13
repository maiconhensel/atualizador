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
		self.__set_is_paf()
		self.log.info('PAF: %s' % self.is_paf)

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

	def __set_is_paf(self):

		def check_module_config():
			if self.key.get('modules') and (self.key['modules'].get('midemfe') or self.key['modules'].get('midecfe') or self.key['modules'].get('midenfce')):
				return False

			return True

		self.is_paf = self.key.get('paf') and self.key['paf'].get('ativo') and check_module_config(self) or False

		if self.key.get('empresa_cnpj') =='54.517.628/0014-02' and os.environ.get('LXNOTPAF'):
			self.is_paf = False

	def has_mide(self):
		"""
		Verifica se possui algum módulo do MID-e.
		"""
		modules_list = [
			'midenfce',
			'midenfe',
			'midemfe',
			'midecfe',
		]

		for module in modules_list:
			if self.key['modules'].get(module):
				return True

		return False

