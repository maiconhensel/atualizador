import logging
import os
import sys

from controller.atualizador import Atualizador

if __name__ == '__main__':
	from utils.ws import WS

	ws = WS()
	ws.log.info('Args: %s' % sys.argv)
	cur_dir = os.path.realpath(os.curdir).split(os.sep)
	ws.log.debug('CurDir: %s ' % cur_dir)

	cur_dir = os.sep.join([x for x in cur_dir if x != 'atualizador'])
	ws.log.info('CurDir: %s ' % cur_dir)

	ws.load_key(cur_dir)

	A = Atualizador(ws, cur_dir)

	ws.log.info(os.listdir(cur_dir))

	if len(sys.argv) > 1 and ws.key:
		if '--download' in sys.argv:
			ws.log.info('Parâmetro --download')
			A.download()

		if '--update' in sys.argv:
			ws.log.info('Parâmetro --update')
			A.update()

	else:
		ws.download_key({'empresa_cnpj':'54517628001402', 'senha': '77462691', 'host_name': 'desktop-maicon', 'host_key': 'RPJJ-LLBL-MIIN-IKEP'})
		ws.log.info('instalador')
	

