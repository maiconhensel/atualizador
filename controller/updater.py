#import requests
import shutil
import os
import subprocess
import sys
#import json
import traceback
import zipfile

#from hashlib import md5
#from requests.auth import HTTPBasicAuth
#from requests.adapters import HTTPAdapter

#from datetime import datetime

class Updater:
	def __init__(self, ws, parent=None):
		self.ws = ws
		self.parent = parent
		self.main_dir = parent.main_dir

	def show_message(self, msg):
		self.parent.set_status_txt(msg)
		self.ws.log.info(msg)
	
	def update(self):

		self.parent.set_statusbar_percent(0)
		self.show_message('Inicializando o processo de atualização dos arquivos.')

		try:
			sys_security_exe = os.sep.join([self.main_dir, 'system_security.exe'])
			if os.path.exists(sys_security_exe):
				self.show_message('Executando scripts de segurança da aplicação.')
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW	
				subprocess.call([sys_security_exe], startupinfo=startupinfo)	
				#os.startfile('system_security.exe')
		except Exception as e:
			self.ws.log.error(traceback.format_exc())

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

		self.show_message("Criando backup da versão atual!")
		self.__compactar_arquivos_backup()
		self.parent.set_statusbar_percent(100)
		self.show_message("Backup concluído!")

		lista_diretorios_descartados = ['log']

		self.parent.set_statusbar_percent(0)

		self.__move_files(lista_diretorios_descartados)

		self.parent.set_statusbar_percent(100)
		self.show_message("Atualização concluída!")

		self.show_message("#Verificando estrutura do banco de dados...")
		manut_exe = os.sep.join([self.main_dir, 'pdvserver.exe'])
		self.ws.log.info([manut_exe, '--checkdb'])
		
		try:
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW				
			#retorno = subprocess.call('C:\\LinxPostos\\pdvserver.exe --checkdb', stdout=sys.stdout, stderr=sys.stderr, startupinfo=startupinfo)
			subprocess.call([manut_exe, '--checkdb'], startupinfo=startupinfo)
		except:
			self.ws.log.critical(traceback.format_exc())

		self.show_message("#Salvando nova versão no banco de dados...")
		#self.write_sysversion()

		self.show_message("#Finalizando...")

	def __compactar_arquivos_backup(self):
		''' Irá criar o backup da pasta raiz, incluindo apenas os arquivos do sistema
			Todos os outros arquivos presentes na pasta raiz não serão adicionados '''

		if not os.path.exists('update'):
			return

		diretorios_descartados_list = []
		pasta_raiz_list = os.listdir(self.main_dir)
		pasta_update_list = os.listdir(os.sep.join([self.main_dir, 'update']))

		self.show_message("Atualização concluída!")

		for file in pasta_raiz_list:
			exists = False

			for file_update in pasta_update_list:
				if file_update == file:
					exists = True

			if not exists:
				diretorios_descartados_list.append(file)

		diretorios_descartados_list.append('log')

		nome_arquivo = "{0}V{1}.zip".format(os.path.realpath('.').split(os.path.sep)[-1], self.ws.version)
		self.__compactar_arquivos(nome_arquivo, os.getcwd(), os.path.join(os.getcwd(), 'backup'), diretorios_descartados_list)

	def __compactar_arquivos(self, nome_arquivo, diretorio_origem, diretorio_destino, lista_diretorios_descartados=None, arquivo_zip=None, diretorio_zip=''):
		'''
		Objetivo..: Compactar arquivos de um determinado diretorio
		Parâmetros: nome_arquivo: nome do arquivo compactado
					diretorio_origem: diretório a ser compactado.
					diretorio_destino: diretorio onde será criado o arquivo compactado.
					lista_diretorios_descartados: lista de diretódios a serem desconsiderados na compactação
		Retorno...: Não se aplica
		'''

		lista_diretorios_descartados = lista_diretorios_descartados or []

		if not arquivo_zip:
			if not os.path.exists(diretorio_destino):
				os.mkdir(diretorio_destino)

			arquivo_zip = zipfile.ZipFile(diretorio_destino+'/'+nome_arquivo, 'w')

			self.__compactar_arquivos(nome_arquivo, diretorio_origem, diretorio_destino, lista_diretorios_descartados, arquivo_zip)

			arquivo_zip.close()
			return

		lista_diretorios_descartados.append(nome_arquivo)

		self.ws.log.info("Diretorios descartados: {}".format(", ".join(lista_diretorios_descartados)))
		file_list = self.__get_file_list(diretorio_origem, diretorio_destino, lista_diretorios_descartados)

		#file_list = [x for x in os.listdir(diretorio_origem) if x not in lista_diretorios_descartados]
		file_list_length = len(file_list)

		for index, file_name in enumerate(file_list):

			try:
				self.show_message('Compactando arquivo {}'.format(file_name))
				self.parent.set_statusbar_percent(100 * index / file_list_length)
				arquivo_zip.write(file_name)
			except Exception as e:
				import traceback
				self.ws.log.error(traceback.format_exc())
				raise Exception("Falha ao compactar %s: Erro: %s" % (file_name, str(e)))

	def __get_file_list(self, diretorio_origem, diretorio_destino, lista_diretorios_descartados):

		return_list = []
		lista_diretorios_descartados = lista_diretorios_descartados or []

		file_list = [x for x in os.listdir(diretorio_origem) if x not in lista_diretorios_descartados]

		for file_name in file_list:
			real_file = os.path.join(diretorio_origem, file_name)

			if os.path.isdir(real_file):
				return_list.extend(self.__get_file_list(real_file, os.path.join(diretorio_destino, file_name), lista_diretorios_descartados))
			else:
				return_list.append(real_file)

		return return_list

	def __move_files(self, lista_diretorios_descartados=[]):
		try:
			#self.kill_process_runing(force=True)
			self.show_message("Movendo pastas e arquivos.")
			diretorio_origem = os.path.join(self.main_dir, 'update')

			file_list = self.__get_file_list(diretorio_origem, self.main_dir, lista_diretorios_descartados)
			
			file_list_length = len(file_list)

			for index, real_file_name in enumerate(file_list):

				self.parent.set_statusbar_percent(100 * index / file_list_length)

				file_name_list = real_file_name.split(os.sep) 
				dir_name = os.sep.join(file_name_list[:-1])
				file_name = file_name_list[-1]
				dest_dir_name = dir_name.replace(diretorio_origem, self.main_dir)

				if os.path.isdir(dir_name) and dest_dir_name != self.main_dir \
						and dest_dir_name.split(os.sep)[-1] not in lista_diretorios_descartados \
						and not os.path.exists(dest_dir_name):

					self.ws.log.info('Criando diretório %s' % dest_dir_name)
					os.makedirs(dest_dir_name)

				self.show_message("Movendo o arquivo: {}".format(file_name))
				shutil.move(real_file_name, os.sep.join([dest_dir_name, file_name]))

			#if self.ws.has_mide() and os.path.exists(os.path.join(self.main_dir, ws.services['mide.atualizador'].setup_file_name)):
			#	ws.log.info("Executando instalador do MID-e Client")
			#	os.popen("%s /s /F /CNPJ=%s" % (ws.services['mide.atualizador'].setup_file_name, ''.join([x for x in ws.info['empresa']['cnpj'] if x.isdigit()])))

			arquivos_backup = [x for x in os.listdir(os.path.join(self.main_dir, 'backup')) if os.path.isfile(os.path.join(os.path.join(self.main_dir, 'backup'), x))]
			for arquivo in arquivos_backup:
				if arquivo.startswith('old_'):
					os.remove(os.path.join(self.main_dir, 'backup', arquivo))

		except Exception as e:
			self.ws.log.critical(traceback.format_exc())
			raise e
			#self.rollback_backup()

		# Desmarca a flag de versão baixada
		#ws.services['config'].save_config({'atualizacao_versao_baixada': False})