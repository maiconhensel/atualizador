#import requests
import os
import pythoncom
import shlex
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
import win32com.client

from core.key import APP_EXE_NAME_MAP

class Updater:
	def __init__(self, ws, parent=None):
		self.ws = ws
		self.parent = parent
		self.main_dir = parent and parent.main_dir
		self.install_db = parent and parent.install_db
		self.buckup_file_name = None

	def show_message(self, msg):
		self.parent.set_status_txt(msg)
		self.ws.log.info(msg)
	
	def update(self):
		"""
			Objetivo: Método responsável por realizar toda a operação de atualização dos arquivos baixados.
			Parametros: Nenhum
			Retorno: True em caso de sucesso, Exception em caso de falha.
		"""

		self.parent.set_statusbar_percent(0)
		self.show_message('Inicializando o processo de atualização dos arquivos.')
		time.sleep(1)

		self.__execute_system_security()

		self.__compactar_arquivos_backup()

		self.__move_files()

		self.ws.log.debug('flag install_db %r' % self.install_db)
		if self.install_db:
			self.parent.set_statusbar_percent(0)
			self.__instal_postgres()

		else:
			self.parent.set_statusbar_percent(0)
			self.__execute_manut()

		self.ws.log.debug('flag is_install %r' % self.parent.is_install)
		self.ws.log.debug('flag create_shortcut %r' % self.parent.create_shortcut)

		if self.parent.is_install and self.parent.create_shortcut:
			self.__create_shortcuts()

		self.parent.set_statusbar_percent(100)
		self.show_message("Finalizado!")
		return True

	def __execute_system_security(self):
		"""
			Objetivo: Executar o system_security.exe responsável pra conseder permissões de alteração nos arquivos a serem atualizados.
			Parametro: Nenhum
			Retorno: True em caso de sucesso, False em caso de falha.
		"""

		try:
			sys_security_exe = os.sep.join([self.main_dir, 'system_security.exe'])
			if os.path.exists(sys_security_exe):
				self.show_message('Executando scripts de segurança da aplicação.')
				self.__execute_exe([sys_security_exe])

			else:
				self.ws.log.critical("system_security.exe não existe na diretório de instalação/atualização: %s" % self.main_dir)
				return False

		except Exception as e:
			self.ws.log.error(traceback.format_exc())
			return False

		return True

	def __compactar_arquivos_backup(self):
		"""
			Objetivo: Criar o backup da pasta raiz, incluindo apenas os arquivos do sistema que serão atualizados.
						Todos os outros arquivos presentes na pasta raiz não serão adicionados
			Parâmetro: Nenhum
			Retorno: True em caso de sucesso, False em caso de não existir a pasta update, Exception em caso de falha.
		"""

		if not os.path.exists(os.path.join(self.main_dir, 'update')) or not os.listdir(self.main_dir):
			return False

		self.parent.set_statusbar_percent(0)

		backup_dir = os.path.join(self.main_dir, 'backup')

		if not os.path.exists(backup_dir):
			os.makedirs(backup_dir)

		try:
			# Valida: Se o arquivo não começa com old_ e não possui outro arquivo com o mesmo nome que começa com old_, apenas renomeia.
			# Se o arquivo não começa com old_ e possui outro arquivo com o mesmo nome que começa com old_, remove a versão com _
			# Depois renomeia o arquivo atual.
			arquivos_backup = [x for x in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, x))]

			for arquivo in arquivos_backup:
				if not arquivo.startswith('old_') and not os.path.exists(os.path.join(self.main_dir, 'backup', 'old_{}'.format(arquivo))):
					os.rename(os.path.join(self.main_dir, 'backup', arquivo), os.path.join(self.main_dir, 'backup', 'old_{}'.format(arquivo)))

				elif not arquivo.startswith('old_') and os.path.exists(os.path.join(self.main_dir, 'backup', 'old_{}'.format(arquivo))):
					os.remove(os.path.join(self.main_dir, 'backup', 'old_{}'.format(arquivo)))
					os.rename(os.path.join(self.main_dir, 'backup', arquivo), os.path.join(self.main_dir, 'backup', 'old_{}'.format(arquivo)))

		except Exception as e:
			self.ws.log.error(traceback.format_exc())
			raise Exception('Falhar ao validar o diretório de backup de versão')

		self.show_message("Criando backup da versão atual!")
		self.parent.set_statusbar_percent(0)
		time.sleep(1)

		lista_arquivos_descartados = ["log", "backup", "update", "paf_ecf"]

		nome_arquivo = "{0}V{1}.zip".format(self.main_dir.split(os.path.sep)[-1], self.ws.versao)
		diretorio_backup = os.path.join(self.main_dir, 'backup')

		try:
			if not os.path.exists(diretorio_backup):
				self.ws.log.info("Criando diretório de backup %s" % diretorio_backup)
				os.mkdir(diretorio_backup)
		except Exception as e:
			self.ws.log.error(traceback.format_exc())
			raise Exception("Ocorreu um erro ao criar o diretório de backup.")

		self.buckup_file_name = os.sep.join([diretorio_backup, nome_arquivo])
		self.ws.log.info("Criando backup do diretório %s no arquivo %s" % (self.main_dir, self.buckup_file_name))

		try:
			arquivo_zip = zipfile.ZipFile(self.buckup_file_name, 'w')

			self.__compactar_arquivos(self.main_dir, os.path.join(self.main_dir, 'update'), lista_arquivos_descartados, arquivo_zip)

			arquivo_zip.close()
		except Exception as e:
			self.ws.log.error(traceback.format_exc())
			raise Exception("Ocorreu um erro ao compactar os arquivos no backup.")

		self.parent.set_statusbar_percent(100)
		self.show_message("Backup concluído!")
		time.sleep(1)
		return True

	def __compactar_arquivos(self, diretorio_origem, diretorio_destino, lista_arquivos_descartados=None, arquivo_zip=None, diretorio_zip=''):
		'''
		Objetivo..: Compactar arquivos de um determinado diretorio
		Parâmetros: nome_arquivo: nome do arquivo compactado
					diretorio_origem: diretório a ser compactado.
					diretorio_destino: diretorio onde será criado o arquivo compactado.
					lista_arquivos_descartados: lista de diretódios a serem desconsiderados na compactação
		Retorno...: Não se aplica
		'''

		lista_arquivos_descartados = lista_arquivos_descartados or []

		self.ws.log.info("Diretorios descartados: {}".format(", ".join(lista_arquivos_descartados)))
		file_list = self.__get_file_list(diretorio_origem, diretorio_destino, lista_arquivos_descartados)

		file_list_length = len(file_list)

		for index, file_name in enumerate(file_list):

			try:
				self.show_message('Compactando arquivo {}'.format(file_name.split(os.sep)[-1]))
				self.parent.set_statusbar_percent(100 * (index+1) / file_list_length)
				arquivo_zip.write(file_name)
			except Exception as e:
				self.ws.log.error(traceback.format_exc())
				raise Exception("Falha ao compactar o arquivo %s: Erro: %s" % (file_name, str(e)))

	def __get_file_list(self, diretorio_origem, diretorio_destino=None, lista_arquivos_descartados=None):
		"""
			Objetivo: Metódo recursivo para buscar no diretório de origem todos os arquivos que estão no diretório de destivo, 
						ignorando arquivos/diretórios a serem descartados.
			Parâmetros: diretorio_origem - caminho do diretório a ser buscado os arquivos. Ex: C:\\LinxPostos
						diretorio_destino - caminho do diretório a ser comparado os arquivos. Ex: C:\\LinxPostos\\update
						lista_arquivos_descartados - lista com os arquivos/diretórios que deveão ser descartados
			Retorno: lista com os caminho completo dos arquivos encontrados no diretório de origem.
		"""

		return_list = []
		lista_arquivos_descartados = lista_arquivos_descartados or []

		file_list = [x for x in os.listdir(diretorio_origem) if x not in lista_arquivos_descartados]

		for file_name in file_list:
			real_file = os.path.join(diretorio_origem, file_name)

			if os.path.isdir(real_file):
				new_dir = os.path.join(diretorio_destino, file_name) if diretorio_destino else None
				return_list.extend(self.__get_file_list(real_file, new_dir, lista_arquivos_descartados))
			else:
				if not diretorio_destino or os.path.exists(os.path.join(diretorio_destino, file_name)):
					return_list.append(real_file)

		return return_list

	def __move_files(self):
		"""
			Objetivo: Mover os arquivos da pasta update para a pasta raiz.
			Parâmetro: lista_arquivos_descartados - lista contendo arquivos/diretórios que não devem ser movidos.
			Retorno: True em caso de sucesso, Exception em caso de falha.
		"""

		lista_arquivos_descartados = ["log", "backup", "update", "paf_ecf"]

		self.parent.set_statusbar_percent(0)

		try:
			self.kill_process_runing()
			self.show_message("Movendo pastas e arquivos.")
			diretorio_origem = os.path.join(self.main_dir, 'update')

			file_list = self.__get_file_list(diretorio_origem, lista_arquivos_descartados=lista_arquivos_descartados)
			
			file_list_length = len(file_list)

			for index, real_file_name in enumerate(file_list):

				self.parent.set_statusbar_percent(100 * (index+1) / file_list_length)

				file_name_list = real_file_name.split(os.sep) 
				dir_name = os.sep.join(file_name_list[:-1])
				file_name = file_name_list[-1]
				dest_dir_name = dir_name.replace(diretorio_origem, self.main_dir)

				if os.path.isdir(dir_name) and dest_dir_name != self.main_dir \
						and dest_dir_name.split(os.sep)[-1] not in lista_arquivos_descartados \
						and not os.path.exists(dest_dir_name):

					self.ws.log.info('Criando diretório %s' % dest_dir_name)
					os.makedirs(dest_dir_name)

				self.show_message("Movendo o arquivo: {}".format(file_name))
				shutil.move(real_file_name, os.sep.join([dest_dir_name, file_name]))

			arquivos_backup = [x for x in os.listdir(os.path.join(self.main_dir, 'backup')) if os.path.isfile(os.path.join(os.path.join(self.main_dir, 'backup'), x))]
			for arquivo in arquivos_backup:
				if arquivo.startswith('old_'):
					os.remove(os.path.join(self.main_dir, 'backup', arquivo))

		except Exception as e:
			self.ws.log.critical(traceback.format_exc())
			self.parent.show_message_error("Ocorreu um erro durante a atualização dos arquivos.\nO backup da versão anterior será restaurado.")
			self.__rollback_backup()
			raise Exception("Backup restaurado com sucesso.")

		if self.ws.dbs.get('public'):
			try:
				self.ws.dbs['public'].execute("update config_local set valor = false where chave = 'atualizacao_versao_baixada'")
			except Exception as e:
				self.ws.log.error("Ocorreu um erro ao atualizar a chave 'atualizacao_versao_baixada' da tabela config_local")
				self.ws.log.error(traceback.format_exc())

		self.parent.set_statusbar_percent(100)
		self.show_message("Arquivos movidos com sucesso!")

		return True

	def __rollback_backup(self):
		"""
			Objetivo: Restaurar o backup criado anteriormente em caso de falha ao mover os arquivos da pasta update.
			Parâmetro: Nenhum
			Retorno: True em caso de sucesso, False em caso de falha.
		"""

		try:
			self.kill_process_runing()

			self.ws.log.info('Houve um problema na aplicação da atualização. Restaurando o arquivo %s de backup do sistema.' % self.buckup_file_name)
			self.__unzip_file(self.buckup_file_name)

			return True
		except Exception as e:
			self.ws.log.critical(traceback.format_exc())
			return False

	def __unzip_file(self, zip_file_name):

		arquivo_zip = zipfile.ZipFile(zip_file_name, "r")

		file_list_length = len(arquivo_zip.infolist())

		self.parent.set_statusbar_percent(0)

		for index, arquivo in enumerate(arquivo_zip.infolist()):
			dir_list = arquivo.filename.split('/')
			self.parent.set_statusbar_percent(100 * (index+1) / file_list_length)
			self.show_message('Descompactando arquivo: ' + dir_list[-1])
			arquivo_zip.extract(arquivo)

	def kill_process_runing(self):
		"""
			Objetivo: Listar todos os executáveis da pasta raiz e finalizar a execução dos mesmos.
			Parâmetro: Nenhum
			Retorno: Nenhum
		"""

		exe_list = [x for x in os.listdir(self.main_dir) if x.endswith('.exe') and not x.startswith('atualizador')]

		self.ws.log.info('Apps a serem finalizados: %s' % ", ".join(exe_list))

		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		for index, app in enumerate(exe_list):
			self.show_message('Finalizando o processo: %s' % app)
			self.parent.set_statusbar_percent(100 * (index+1) / len(exe_list))
			subprocess.call('taskkill /f /im {}'.format(app), startupinfo=startupinfo)
			time.sleep(.5)
			
	def __execute_manut(self):
		"""
			Objetivo: Realizar a manutenção de banco de dados, através do executável do produto LinxPostosPos
			Parametro: Nenhum
			Retorno: Nenhum
		"""
		self.show_message("Realizando manutenção no banco de dados.")
		manut_exe = os.sep.join([self.main_dir, 'pdvserver.exe'])
		self.ws.log.info([manut_exe, '--checkdb'])

		base_dir = os.getcwd()
		os.chdir(self.main_dir)

		try:
			self.__execute_exe(shlex.split("\"%s\" --checkdb" % manut_exe))
		except:
			self.ws.log.critical(traceback.format_exc())
		finally:
			os.chdir(base_dir)

	def __instal_postgres(self):
		"""
			Objetivo: Realizar a manutenção de banco de dados, através do executável do produto LinxPostosPos
			Parametro: Nenhum
			Retorno: Nenhum
		"""
		base_dir = os.getcwd()
		os.chdir(self.main_dir)

		try:
			psql_file_zip = os.sep.join([self.main_dir, 'pgsql.zip'])
			self.ws.log.info("Arquvio pgsql.zip: %s" % psql_file_zip)
			self.__unzip_file(psql_file_zip)
			
		except Exception as e:
			self.ws.log.error(traceback.format_exc())

		self.show_message("Realizando instalação do banco de dados.")
		pgsql_install_exe = os.sep.join([self.main_dir, 'pgsql_install.exe'])
		self.ws.log.info([pgsql_install_exe])

		try:
			self.__execute_exe(pgsql_install_exe)
			os.remove(psql_file_zip)
		except Exception as e:
			self.ws.log.critical(traceback.format_exc())
			raise Exception("Ocorreu um erro ao realizar a instalação do banco de dados\nErro: %s" % str(e))
		finally:
			os.chdir(base_dir)

	def __execute_exe(self, exe):
		"""
			Objetivo: Executar alguns executáveis necessários na instalação/atualização do sistema
			Parametro: exe - nome do arquivo executável
			Retorno: Nenhum
		"""

		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		count = 0.0
		proc = subprocess.Popen(exe, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT)
		for line in iter(proc.stdout.readline,''):
			if not line:
				break
			try:
				text = line.rstrip().decode()
				if text:
					self.show_message(text)
			except:
				pass
			self.parent.set_statusbar_percent(count)
			count = count + 0.2 if count < 100 else 0

		self.parent.set_statusbar_percent(100)

	def __create_shortcuts(self):
		"""
			Objetivo: Criar os atalhosdos executáveis do sistema instalado
			Parametro: Nenhum
			Retorno: Nenhum
		"""

		self.parent.set_statusbar_percent(0)

		def __create(exe, lnk_name=''):
			self.ws.log.info('Criando atalho do %s' % exe)

			try:
				target = os.path.join(self.main_dir, exe)
				self.ws.log.info("Diretório do exe: %s" % target)
				
				pythoncom.CoInitialize()
				desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
				self.ws.log.info("Diretório desktop: %s" % desktop)
				
				path = os.path.join(desktop, self.ws.key.get('appname') + lnk_name + '.lnk')

				shell = win32com.client.Dispatch("WScript.Shell")
				shortcut = shell.CreateShortCut(path)
				shortcut.Targetpath = target
				shortcut.IconLocation = target
				shortcut.WorkingDirectory = self.main_dir
				shortcut.WindowStyle = 7 # 7 - Minimized, 3 - Maximized, 1 - Normal

				self.ws.log.info("Criando atalho %s" % path)
				shortcut.save()
			except Exception as e:
				self.ws.log.critical("Falha ao criar o atalho do exe: %s" % exe)
				self.ws.log.error(traceback.format_exc())

		principal_exe_name = APP_EXE_NAME_MAP.get(self.ws.key.get('appid')) or 'pdv.exe'

		__create(principal_exe_name)
		self.parent.set_statusbar_percent(33)

		__create('sync.exe', ' - Sincronia')
		self.parent.set_statusbar_percent(66)

		__create('atualizador.exe', ' - Atualizador')
		self.parent.set_statusbar_percent(100)
