#!/usr/bin/python
# vi: fileencoding=utf-8

__title__ = 'WorkSpace - Area de Trabalho'
__author__ = 'Thiago Piccinini'
__doc__ = '''A area de trabalho é uma classe que possui todos os objetos
necessarios para execução do sistema, tais como o banco de
dados, sistema de log, informações sobre o banco de dados, etc.'''

import os
import sys
import logging
import importlib
import traceback
import psycopg2
import subprocess
import time

from datetime import datetime

from lx import lxdb
from lx.lxdatetime import now
from lx.lxtypes import TString, TLong, TInteger, TTime
from lx.lxcrypto import LxCrypto

from core import version
from core.key import LinxPostosInfoKey, LinxPostosKeyRequest
from core.exceptions import WorkSpaceValidateException, DatabaseVersionException

class WorkSpace:
	"""
		Classe responsável por armazenar diversas informações e provê-las em qualquer lugar da aplicação
	"""

	def __init__(self, loadconfig=True, logname=None):
		self.logname = logname
		if loadconfig:
			self.load()

	def load(self):

		self.versao = version.__version_str__
		self.appversion = version.__appversion_str__
		self.versao_ts = datetime(*version.__ts__)
		self.versao_ts_update = datetime(*version.__ts__)

		self.info = {}
		self.info['env'] = {k[2:].lower(): v for k, v in os.environ.items() if k.startswith('LX')}

		# PID do processo em execução
		self.pid = os.getpid()

		# Cria objeto de log para o sistema
		#logging.basicConfig(format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")
		if not hasattr(self, 'log'):

			self.log = self.get_logger(self.logname)
			self.log_level = self.log.level

		self.sys_key = LxCrypto().get_sys_key()
		self.log.info("Versão = %s" % self.versao)
		self.log.info("Versão APP = %s" % self.appversion)
		self.log.info("Serial = %s" % self.sys_key)
		self.log.info("Gerado = %s" % self.versao_ts.strftime('%d/%m/%Y %H:%M:%S'))

		try:
			self.set_hostname()
		except Exception as e:
			self.log.error("Não foi possível conectar ao banco de dados")
			self.log.error(traceback.format_exc())
			sys.exit(0)

		self.log.info("Estação: %s" % self.hostname)
		# ----------------------------------------------------------------------
		# Chave de ativação

		self.key = {}
		try:
			self.load_key(True)

		except Exception as e:
			self.log.critical("Não foi possível carregar/validar a chave de ativação.")
			self.log.error(str(e))

			self.log_level = logging.DEBUG
			self.log.setLevel(self.log_level)

		# ----------------------------------------------------------------------
		# PAF
		self.set_is_paf()

		# ----------------------------------------------------------------------
		# Banco de Dados

		# Dicionário, uma conexão para cada schema
		if not hasattr(self, 'dbs'):
			self.dbs = {}

		# Cria as conexões
		self.db = None

		try:
			self.connect_db()
			# Schema 'public' será o DB padrão.
			self.db = self.dbs['public']

		except Exception as e:
			self.log.error("Não foi possível conectar ao banco de dados")
			self.log.error(traceback.format_exc())

	def get_logger(self, name=None):

		log = logging.getLogger(name or "linxpos")

		loglevel = int(self.info['env'].get("loglevel", logging.INFO))

		if self.info['env'].get('app', '').startswith('sincronia') and not self.info['env'].get("loglevel"):
			loglevel = logging.INFO

		log.setLevel(loglevel)

		# log do flask/werkzeug...
		werkzeug_log = logging.getLogger('werkzeug')
		werkzeug_log.setLevel(logging.ERROR)

		if self.info['env'].get('logfile') or getattr(sys, 'frozen', False):
			# quando eh versao producao, seta variavel onde esta a cadeia de certificados para o requests
			# e configura logs em arquivo
			os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.executable), 'cacert.pem')

			from lx.lxlog import TimedCompressedRotatingFileHandler, parse_rotate_interval

			## Quando for versao de producao, configura o log para gerar arquivo com rotacao e compactacao...
			if not os.path.exists('log'):
				os.mkdir('log')

			rotate_interval, rotate_when = 1, 'MIDNIGHT'
			if self.info['env'].get('app', '').startswith('sincronia') and self.info['env'].get('logrotate'):
				interval_when = parse_rotate_interval(self.info['env']['logrotate'])
				if interval_when:
					rotate_interval, rotate_when = interval_when

			filename = name or self.info['env'].get('app') or "linx"

			handler = TimedCompressedRotatingFileHandler(filename="log/{}.log".format(filename), when=rotate_when, interval=rotate_interval, encoding='utf-8')
			#handler = TimedCompressedRotatingFileHandler(filename="log/{}.log".format(os.environ.get('LXAPP') or "linx"), when='M', interval=1)
			formatter = logging.Formatter("%(asctime)s: %(name)s: %(levelname)s: %(message)s")
			handler.setFormatter(formatter)
			log.addHandler(handler)
			

		else:
			logging.basicConfig(format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")

		return log

	def load_key(self, renew=False):
		'''Recarregar Configuracoes da Key para Aplicativo PDV'''

		self.key = LinxPostosInfoKey(self.log)
		self.key.load(renew)

		self.log.info("BackOffice = '%s'" % self.key.get('backoffice_nome'))
		self.log.info("Aplicativo = '%s'" % self.key.get('appname'))
		self.log.info("Bandeira   = '%s'" % self.key.get('cliente_bandeira_nome'))

	def download_key(self, key_info):
		self.log.info('Baixando chave de ativação')
		self.key = LinxPostosKeyRequest(self.log).get_key(key_info)

	def connect_db(self, schema='public'):
		'''
			Conecta ao banco de dados de acordo com os dados passados por parâmetro
			force: Se já existir conexão com o banco de dados, esse parametro dirá se deve reconectar ou não
		'''

		db_dict = {
			'host': 'localhost',
			'port': 5470,
			'database': 'linxpostospos',
			'schema': schema,
			'user': 'postgres',
			'password': 'postgres'			
		}

		self.log.info("Conectando banco de dados '{database}' em '{host}':'{port}' user '{user}' schema '{schema}'".format(**db_dict))

		try:
			if hasattr(self, 'log') and hasattr(self, 'serial'):
				db_dict['log'] = self.log
			self.dbs[schema] = lxdb.DB(**db_dict)
		except psycopg2.OperationalError as e:

			self.log.info("Não foi possível conectar no banco de dados linxpostospos...")
			raise e

		self.dbs[schema].log_level = self.log_level

	def set_hostname(self):
		'''Seta o atributo self.hostname de acordo com o sistema operacional'''

		import socket
		self.hostname = socket.gethostname().upper()

	def set_is_paf(self):

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

global ws
ws = WorkSpace()
