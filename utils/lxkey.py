import os, re
import sys
import json
import platform
import traceback

from datetime import datetime, timedelta

now = datetime.now
oneDay = timedelta(days=1)
oneHour = timedelta(hours=1)

from .lxcrypto import LxCrypto

from .exceptions import LinxPostosKeyException, LinxPostosKeyExpiredException, LinxPostosKeyOutdatedException, \
		LinxPostosKeyDemoException, LinxPostosKeyRequestException, LinxPostosKeySaveException

KEY_FILENAME = 'linxpostospos.key'

# Caminho de onde salvar a chave do sistema
WIN_KEY_PATH_LIST = ["./"]
UNIX_KEY_PATH_LIST = ['/etc/', os.path.expanduser('~') + '/.sellerpdv/', '']

# Padrão dos backoffice de integração...
AUTOSYSTEM_BACKOFFICE = 1
SELLER_BACKOFFICE = 4
POSTOPOP_BACKOFFICE = 6
EMPORIOPOP_BACKOFFICE = 8
EMPORIOPRO_BACKOFFICE = 9

BACKOFFICE_NAME_MAP = {
	AUTOSYSTEM_BACKOFFICE: "Autosystem",
	SELLER_BACKOFFICE: "Seller Web",
	POSTOPOP_BACKOFFICE: "Posto Pop",
	EMPORIOPOP_BACKOFFICE: "Empório Pop",
	EMPORIOPRO_BACKOFFICE: "Empório Pro",
}

BACKOFFICE_CONTATO_SUPORTE_MAP = {
	AUTOSYSTEM_BACKOFFICE: "3003-1551",
	SELLER_BACKOFFICE: "(51) 3003-1401",
	EMPORIOPOP_BACKOFFICE: "(51) 3003-1401",
	POSTOPOP_BACKOFFICE: "(51) 2101-9950",	
}

# Aplicativos
LXPOS_APP = 1
PDVSELLER_APP = 2
JETOIL_APP = 3
KDS_APP = 5
AUTOATENDIMENTO_APP = 6
TERMINAL_COMANDA_APP = 7

APPS_ID = (LXPOS_APP, PDVSELLER_APP, JETOIL_APP, KDS_APP, AUTOATENDIMENTO_APP, TERMINAL_COMANDA_APP)

PRODUTO_INTRANET_MAP = {
	LXPOS_APP: 8,
	PDVSELLER_APP: 13,
	JETOIL_APP: 12,
	KDS_APP: 16,
	AUTOATENDIMENTO_APP: 36,
	TERMINAL_COMANDA_APP: 37,
}

# Bandeiras
BANDEIRA_BRANCA = 1
BANDEIRA_IPIRANGA = 2
BANDEIRA_RAIZEN = 3
BANDEIRA_ALE = 4
BANDEIRA_PETROBRAS = 5

BANDEIRA_NAME_MAP = {
	BANDEIRA_BRANCA: "BRANCA",
	BANDEIRA_IPIRANGA: "IPIRANGA",
	BANDEIRA_RAIZEN: "RAIZEN",
	BANDEIRA_ALE: "ALE",
	BANDEIRA_PETROBRAS: "PETROBRAS",
}

class LinxPostosInfoKey(dict):
	def __init__(self, log):
		dict.__init__(self)
		self.fname = None
		self.log = log
		self.backoffice = None

	def read(self):
		self.fname = self.get_key_file()
		text = open(self.fname, encoding='latin1').read()
		lcrypt = LxCrypto()
		text = lcrypt.decrypt_key(text)
		d = json.loads(text)
		self.update(d)
		self['ativo'] = True

		# Flag para teste de chave Linx
		self['linx'] = self['empresa_cnpj'] == "54.517.628/0014-02"

		self['ts_create'] = datetime.strptime(self['ts_create'], '%Y-%m-%d %H:%M')
		self['ts_valid'] = datetime.strptime(self['ts_valid'], '%Y-%m-%d %H:%M')

		if self.get('ts_renew'):
			self['ts_renew'] = datetime.strptime(self['ts_renew'], '%Y-%m-%d %H:%M')
		else:
			self['ts_renew'] = self['ts_create'] + (7 * oneDay)

		if self.get('config') and self['config'].get('horario_verao_entrada') and self['config'].get('horario_verao_saida'):
			self['config']['horario_verao_saida'] = str(datetime.strptime(self['config'].get('horario_verao_saida'), '%Y-%m-%d %H:%M'))
			self['config']['horario_verao_entrada'] = str(datetime.strptime(self['config'].get('horario_verao_entrada'), '%Y-%m-%d %H:%M'))

		if 'paf' in self and 'config' in self['paf']:

			config = {}
			for key, value in self['paf']['config'].items():
				k,v = self.parse_type_key(key,value)
				config[k] = v

			self['paf']['config'] = config

		self.backoffice = self.get('backoffice')
		self.bandeira = self.get('cliente_bandeira_id')
		self.validate_config()
		self.log.debug("Modulos: %s" % self.get('modules'))
		self.log.debug("Configs: %s" % self.get('config'))
		self.log.debug("Releases: %s" % self.get('releases'))
		self.log.debug("Paf: %s" % self.get('paf'))

	def load(self, renew=True):
		self.read()

		# Atualização automática da chave.
		if self.validate_renew() and renew:
			self.log.info("Atualização automática de licença.")
			if self.renew():
				self.read()

		try:
			self.validate()

		except LinxPostosKeyException as e:

			if renew:
				if self.renew():
					return self.load(renew=False)

			raise e

	def validate(self):
		""" Valida os dados da chave """

		# Licença de demonstração?
		if self.get('demo'):
			raise LinxPostosKeyDemoException("Licença de uso de demonstração.")

		# Licença de uso provisório?
		elif self.get('cliente_status') == 1:
			raise LinxPostosKeyDemoException("Licença de uso provisório.")

		# Licença está vencida?
		if self.get('ts_valid') and self['ts_valid'] < now():
			raise LinxPostosKeyExpiredException("Chave de ativação vencida. Validade: %s." % self['ts_valid'].strftime("%d/%m/%Y %H:%M"))

		# Data de criação maior que a data atual?
		if self.get('ts_create') and self['ts_create'] > now() + (6 * oneHour):
			raise LinxPostosKeyOutdatedException("Chave de ativação desatualizada.")

	def validate_config(self):
		types = {'int': int, 'str': str}
		chave_list = list(self['config'].keys())
		for chave in chave_list:
			schave = chave.split(':')
			if len(schave) > 1:
				self['config'][schave[0]] = types[schave[1]](self['config'][chave]) if types.get(schave[1]) else self['config'][chave]

	def validate_renew(self):
		"""Valida se é necessário atualizar a chave"""
		return self['ts_renew'] <= now()

	def get_key_file(self):
		"""Tenta abrir a chave de ativacao nos locais possiveis, de
		acordo com as variavel '*_KEY_PREFIX_LIST'"""

		for key_file in get_key_filepath_list():
			if not os.path.exists(key_file):
				continue

			return key_file
		raise FileNotFoundError('Chave de ativação do sistema não encontrada.')

	def renew(self):

		# Tenta realizar o download da chave de ativação
		try:
			self.log.info("Atualizando chave de ativação.")

			key_dict = LinxPostosKeyRequest(self.log).get_key(self)

			self.update(key_dict)
			return key_dict

		except Exception as e:
			self.log.error("Erro ao atualizar chave de ativação. %s" % str(e))

	#CHAVE_VERSAO2
	def parse_type_key(self, key, value):
		k, v = key.strip(), value.strip()

		if k.find(':') != -1:
			k, t = k.split(':')

			t = {'bool': int, 'str': str, 'int': int, 'long': int,
				'float': float, 'date': datetime}.get(t.strip(), v)

			v = t(value)

		return k, v

class LinxPostosKeyRequest:
	def __init__(self, log):
		self.log = log

	def get_key(self, info):

		params = {}
		if hasattr(info, 'fname'):
			params['host_key'] = info['host_key']
			params['key'] = open(info.fname, 'rb').read()

		else:
			for k, v in [('empresa_cnpj', 'CNPJ do posto'), ('senha', 'Senha'), ('host_name', 'Nome da Estação')]:
				if not info.get(k):
					raise LinxPostosKeyRequestException("Campo %s não informado! Informe o campo para realizar a solicitação." % v)

			# Parao PDV, a intranet irá devolver o produto que será utilizado.
			if 'appid' in info.keys():
				info['appid'] = int(info.get('appid'))				
				if info['appid'] not in APPS_ID:
					info['appid'] = LXPOS_APP

			params = info.copy()

			params['empresa_cnpj'] = ''.join([x for x in info['empresa_cnpj'] if x.isdigit()])

			params['versao'] = 2
			params['platform'] = sys.platform
			params['produtosellerpdv'] = 1
			params['osversion'] = platform.release()
			#params['exeversion'] = __appversion_str__

			# Se não tem senha, pega os 8 primeiros digitos do CNPJ (senha padrão)
			if not params.get('senha'):
				params['senha'] = params['empresa_cnpj'][:8]

				# Se é a Linx usa a senha da intranet
				if info['empresa_cnpj'] == '54.517.628/0014-02':
					params['senha'] = '96857412'

		host     = 'auth.lzt.com.br'
		endereco = '/estacao/lxpos_key/'

		import http.client, urllib
		conn = http.client.HTTPConnection(host)

		params = urllib.parse.urlencode(params)

		headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "application/x-zip"}

		try:
			self.log.debug("Conectando ao servidor de autenticação")
			conn.request("POST", endereco, params, headers)
			response = conn.getresponse()
		except:
			msg = "Erro ao conectar ao servidor de autenticação."
			self.log.error(traceback.format_exc())
			self.log.error(msg)
			raise LinxPostosKeyRequestException(msg)

		if response.status != 200:
			msg = "Erro ao efetuar a solicitação.\n%d %s" % (response.status, response.reason)
			self.log.error(msg)
			raise LinxPostosKeyRequestException(msg)

		self.log.debug("Conexão estabelecida. Recebendo resposta...")

		msg = "Servidor respondeu: %d %s" % (response.status, response.reason)
		self.log.debug(msg)

		data = response.read()
		conn.close()

		if not data:
			msg = "Não houve retorno de informação do servidor de ativação."
			raise LinxPostosKeyRequestException(msg)

		if data.startswith(b"-ERR") or data.startswith(b"+OK"):
			p = data.decode('latin1').split()
			msg = " ".join(p[1:])
			self.log.error(msg)
			raise LinxPostosKeyRequestException("O servidor de ativação retornou: " + msg)
		else:
			self.log.debug("Gravando arquivo...")
			key = self.write_key(data)

			if not key:
				msg = "Impossível gravar o arquivo da chave de ativação."
				raise LinxPostosKeySaveException(msg)

			self.log.debug("Validando chave %s" % key)
			key_info = LinxPostosInfoKey(self.log)
			key_info.load(False)

			if not key_info['ativo']:
				msg = 'Chave corrompida ou inválida.'
				self.log.debug(msg)
				raise LinxPostosKeySaveException(msg)

			if key.startswith(os.path.expanduser('~')):
				msg = "Chave instalada na pasta 'home' do usuário atual (<b>'%s'</b>)\n"\
						"Mova a chave para a pasta <b>'/etc/'</b> para que todos os usuários "\
						"tenham acesso ao sistema!" % os.path.expanduser('~')
			else:
				msg = "Chave instalada em %s" % os.path.realpath(key)

			self.log.debug(msg)
			return key_info

	def write_key(self, data):
		"""Tenta gravar a chave de ativacao nos locais possiveis,
		de acordo com as variavel '*_KEY_PREFIX_LIST'."""

		for key in get_key_filepath_list():
			try:
				file = open(key, 'wb')
			except IOError as e:
				self.log.error("Impossível gravar arquivo %s! Erro: %s" % (key, str(e)))
				continue

			file.write(data)
			file.close()
			return key

		return

def get_key_filepath_list(name=KEY_FILENAME):
	"""Retorna uma lista de caminhos possiveis para a chave de ativacao ou de ecf"""

	if sys.platform == "win32":
		path_list = WIN_KEY_PATH_LIST
	else:
		path_list = UNIX_KEY_PATH_LIST

	ret = []

	for path in path_list:
		ret.append('%s%s' % (path, name))

	for path in path_list:
		ret.append('%s%s' % (path, 'sellerpdv.key'))

	return ret


if __name__ == '__main__':
	from core.workspace import ws
	ws.load()
	ws.on_login()

	ecfkey = ECFKey(ws)
	ecfkey.load()

	from pprint import pprint
	pprint(ecfkey)
