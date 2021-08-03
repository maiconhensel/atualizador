import os
import time

class Atualizador:
	def __init__(self, ws, current_dir, *args, **kwargs):
		self.ws = ws
		self.current_dir = current_dir

	def download(self):
		self.ws.log.info('Iniciando Download')
		import pdb; pdb.set_trace()
		if not os.path.exists(os.sep.join([self.current_dir, 'update'])):
			os.mkdir(os.sep.join([self.current_dir, 'update']))

		f = open(os.sep.join([self.current_dir, 'update', 'md5.json']), 'w')
		for i in range(100):
			self.ws.log.info(i)
			f.write(str(i) + '\n')
			time.sleep(.1)
			
		f.close()
		
	def update(self):
		self.ws.log.info('Iniciando Update')

		if not os.path.exists(os.sep.join([self.current_dir, 'update'])):
			self.ws.log.error('Diretório update não existe')
			return

		f = open(os.sep.join([self.current_dir, 'update', 'md5.json']), 'r')

		for i in f.readlines():
			self.ws.log.info(i)
			time.sleep(.1)
	

