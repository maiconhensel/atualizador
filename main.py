import logging
import os
import sys

if __name__ == '__main__':
	from utils.ws import WS

	ws = WS()
	ws.log.info('Args: %s' % sys.argv)
	cur_dir = os.path.realpath(os.curdir).split(os.sep)
	ws.log.debug('CurDir: %s ' % cur_dir)

	cur_dir = os.sep.join([x for x in cur_dir if x != 'atualizador'])
	ws.log.info('CurDir: %s ' % cur_dir)

	ws.load_key(cur_dir)

	ws.log.info(os.listdir(cur_dir))

	if ws.key:
		hidden = False
		if '--hidden' in sys.argv:
			sys.argv.remove('--hidden')
			hidden = True

		if len(sys.argv) <= 1:
			sys.argv.extend([
				'--download',
				'--update',
			])

		from view.progress import ProgressApp

		ProgressApp(ws, cur_dir, hidden).run(*sys.argv)

	else:
		from view.cadastro import CadastroApp
		CadastroApp(ws).run()
	

