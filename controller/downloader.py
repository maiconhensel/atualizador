import requests
import shutil
import os
import sys
import json
import traceback

from hashlib import md5
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter

from datetime import datetime
#from lx.lxtypes import TString, TInteger


class Downloader:
	def __init__(self, ws, parent=None):
		self.ws = ws
		self.parent = parent
		self.main_dir = parent and parent.main_dir
		self.install_db = parent and parent.install_db
		self.md5s = {}
		self.pgsql_md5s = {}

		self.__load_info_server()

	def __load_info_server(self):
		self.base_url = None
		self.username = None
		self.password = None

		for server_dict in self.ws.key['updatesrv']:
			if server_dict['type'] != 'HTTP':
				continue

			self.base_url = server_dict['host']
			self.username = server_dict['user']
			self.password = server_dict['password']

		self.auth = HTTPBasicAuth(self.username, self.password)

	'''
	def verifica_atualizacao_mide(self, versao, versao_pdv):
		"""
			Verifica a necessidade de atualização do mideclient.exe
		"""
		try:
			self.base_url = "%s%s" % (self.base_url, 'extra/mide/V%s/' % versao_pdv)

			self.__download_file("versao.txt", target_path=os.path.join(self.main_dir))

			if os.path.exists(os.path.join(self.main_dir, 'update')):
				versao_mide_versao = TString.parse(open(self.main_dir + '\\versao.txt', 'r').readline().strip())
				versao_mide_versao = [TInteger.parse(x) for x in (versao_mide_versao or '0').split('.')]
			
			from util.lxutil import compara_versao

			self.ws.log.info('Versão Atual: %s' % '.'.join([str(x) for x in versao]))
			self.ws.log.info('Versão FTP: %s' % '.'.join([str(x) for x in versao_mide_versao]))

			return compara_versao(versao, versao_mide_versao)

		except Exception as e:			
			self.ws.log.critical("Erro ao buscar a versão do mide para a versão: %s" % str(e))
			self.ws.log.critical(traceback.format_exc())
			# Pula atualização
			return True

	def download_mide(self):
		"""
			Download mideclient.exe
		"""
		return self.__download_file("MideClient.exe", target_path=os.path.join(self.main_dir))

	'''

	def download(self):
		"""
		Faz o download da versão através do servidor HTTP.
		Parâmetro:
			main_folder: Se for True os arquivos serão baixados dentro da subpasta 'update' no diretório do sistema,
			para posteriomente mover para a pasta principal, quando a atualização for aceita pelo usuário.
		"""
		#self.ws.services['config'].save_config({'atualizacao_versao_baixada': False})
		#subprocess.call('"%s" psql -p 5470 -U postgres -c "%s" postgres' % (abspath('./pgsql/bin/'), sql), stdout=sys.stdout, stderr=sys.stdout)

		self.ws.log.info("Baixando arquivos do servidor no diretório %s" % self.main_dir)
		self.ws.log.info("---------------------------------")

		if self.install_db:
			self.ws.log.info("Baixando arquivos do banco de dados.")
			self.base_url = "%s%s" % (self.base_url, 'extra/postgres/')

			self.__download_file('pgsql.zip', target_path=os.path.join(self.main_dir, 'update'))
			self.ws.log.info("---------------------------------")
			self.__load_info_server()

		self.__resolve_version_path()

		self.ws.log.info("Baixando arquivos do sistema.")
		self.__walk_http(self.md5s)

		self.ws.log.info("---------------------------------")
		self.ws.log.info("Todos os arquivos foram baixados.")

		#self.ws.services['config'].save_config({'atualizacao_versao_baixada': True})

		self.ws.log.info("Verificando necessidade de download do MID-e")
		if self.ws.has_mide():
			self.__download_mide()

		self.ws.log.info('Download dos arquivos da nova versão foram concluídos.')
		return True

	def __download_mide(self):
		return
		ws.services['mide.atualizador'].update(print, is_electron)

	def __download_file(self, source_path, target_path=None):
		"""
		Realiza o download do arquivo e salva o mesmo no caminho (source_path) dentro da pasta do sistema (target_path).
		"""
		if target_path is None:
			target_path = os.path.join(self.main_dir, 'update')

		local_filename = os.path.join(target_path, source_path)
		self.__make_dir(local_filename, target_path)

		req = self.__get_request(self.base_url + source_path.replace('\\', '/'))

		self.ws.log.info('Baixando {}'.format(source_path))
		self.parent.set_status_txt('Baixando {}'.format(source_path.split('\\')[-1]))

		with open(local_filename, 'wb') as f:
			shutil.copyfileobj(req.raw, f)

		return local_filename

	def __get_request(self, url):
		S = requests.Session()
		S.mount(url, HTTPAdapter(max_retries=5))
		return S.get(url, stream=True, auth=self.auth, timeout=30)

	def __path_request(self, url):
		try:
			S = requests.Session()
			S.mount(url, HTTPAdapter(max_retries=5))
			self.ws.log.info(url)
			return S.get(url, auth=self.auth, timeout=30) and True
		except Exception as e:
			self.ws.log.error("Caminho não existe %s! Erro: %s" % (url, str(e)))
			return False

	def __make_dir(self, file_path, target_path):
		"""
		Cria dinâmicamente a hierarquia de pastas de destino do arquivo, partindo do diretório base (target_path).
		"""
		dirname = os.path.dirname(file_path)

		def mkdir(dirname):
			if not os.path.exists(dirname):
				os.mkdir(dirname)

		if dirname == target_path:
			mkdir(dirname)
			return

		self.__make_dir(dirname, target_path)

		mkdir(dirname)

	def __resolve_version_path(self):
		"""
		Resolve qual a URL acessar para baixar a versão.
		"""
		# Se for versão stable, current, esse é o caminho padrão:
		dirname = 'current'

		# Se for PAF, vamos caçar a versão:
		if self.ws.is_paf:
			dirname = 'paf'

			if sys.platform in ("win32", "darwin"):
				dirname += "/windows"

			else:
				dirname += "/linux"

			dirname += "/" + self.ws.key['empresa_uf']

		version_path = self.__get_version_path(dirname)

		self.base_url += version_path + "/"
		self.ws.log.debug("Buscando MD5 em %s" % self.base_url)
		self.md5s = self.__get_md5_sum()
		return True

	def __get_version_path(self, dirname):
		"""
		Retorna o path da versão que deve ser baixada.
		"""

		cnpj = "".join([x for x in self.ws.key['empresa_cnpj'] if x.isdigit()])

		# Se for Linx valida a variável de ambiente LXNOTCURRENT para testes de QA.
		if not (self.ws.key['linx'] and not os.environ.get('LXNOTCURRENT')) and self.__path_request(self.base_url+cnpj):
			self.ws.log.info('Versao definida (especifica): %s' % cnpj)
			return cnpj

		elif dirname == 'current':
			self.ws.log.info('Versao definida: %s' % dirname)
			return dirname

		else:
			self.ws.log.info('Versão definida: PAF')

		# Se não for current nem Linx então é PAF:
		self.__update_key()

		if not self.ws.key['versions'].get('paf_autentic'):
			raise Exception("Nao existe versao liberada na chave para a UF %r (%s)" % (self.ws.key['empresa_uf'], sys.platform))

		version_list = list(self.ws.key['versions']['paf_autentic']['eq'].keys())

		if not version_list:
			raise Exception("Nao existe versao liberada na chave para a UF %r (%s)" % (self.ws.key['empresa_uf'], sys.platform))

		self.ws.log.debug("Versoes liberadas na chave: %s" % version_list)

		version_list_sort = [[int(x) for x in v.split(".")] for v in version_list]
		version_list_sort.sort()
		version = ""

		while len(version_list_sort) > 0:
			version = ".".join([str(x) for x in version_list_sort.pop()])
			req = self.__get_request("%s/%s/%s" % (self.base_url, dirname, version))

			if req.status_code == 200:
				break

			elif req.status_code == 404:
				continue

			else:
				self.ws.log.error('Retorno do servidor %s' % req.status_code)
				raise Exception("Erro ao validar validar versao no servidor, verifique sua conexao com a internet.")

		self.ws.log.info('Versao definida: %s' % version)

		return "%s/%s" % (dirname, version)

	def __update_key(self):
		"""
		Atualiza a chave de licença caso a atual possua data de geração menor que hoje
		para garantir que as versões PAF liberadas na chave sejam as mais atuais.
		"""
		if self.ws.key['ts_create'].date() < datetime.now().date():
			self.ws.key.renew()

	def __get_md5_sum(self):
		"""
		Baixa o arquivo que contém todos os arquivos e os respectivos MD-5 que compõem a versão.
		"""
		fname = self.__download_file("md5.json")

		with open(fname, 'r') as f:
			text = f.read()
			return json.loads(text)

	def __walk_http(self, md5s):
		"""
		Percorre a lista de arquivos versus MD-5 do servidor baixando os arquivos do sistema que não existem
		ou estão desatualizados.
		"""
		main_folder_path = self.main_dir
		update_folder_path = os.path.join(main_folder_path, 'update')
		md5_length = len(md5s)

		for index, iter in enumerate(md5s.items()):
			fname = iter[0].replace('.\\', '')
			fmd5 = iter[1]
			full_dir = os.path.join(update_folder_path, fname)
			full_dir_main = os.path.join(main_folder_path, fname)

			self.parent.set_statusbar_percent(100 * index / md5_length)
			self.parent.set_status_txt('Verificando {}'.format(fname))

			# Valida o MD5 dos arquivos da pasta upload do sitema.
			if os.path.exists(full_dir):
				self.ws.log.debug("MD5 LOCAL: %s // MD5 REMOTO: %s" % (self.__md5_sum(full_dir), fmd5))

				if self.__md5_sum(full_dir) == fmd5:
					self.parent.set_status_txt('Arquivo {} OK.'.format(fname.split('\\')[-1]))

					self.ws.log.info("Arquivo {} OK".format(fname))
					continue

			# Valida o MD5 dos arquivos da pasta principal do sistema
			elif os.path.exists(full_dir_main):
				self.ws.log.debug("MD5 LOCAL: %s // MD5 REMOTO: %s" % (self.__md5_sum(full_dir_main), fmd5))

				if self.__md5_sum(full_dir_main) == fmd5:
					self.parent.set_status_txt('Arquivo {} OK.'.format(fname.split('\\')[-1]))

					self.ws.log.info("Arquivo {} OK".format(fname))
					continue

			self.__download_file(fname, update_folder_path)

	def __md5_sum(self, fname):
		"""
		Gera o MD-5 do arquivo recebido como parâmetro.
		"""
		h = md5()

		with open(fname, 'rb') as f:
			for chunk in iter(lambda: f.read(4096), b''):
				h.update(chunk)

		return h.hexdigest()
