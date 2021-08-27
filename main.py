import logging
import os
import sys

if __name__ == '__main__':
	
	from core.workspace import ws

	ws.log.info('Args: %s' % sys.argv)

	cur_dir = os.getcwd().split(os.sep)
	ws.log.debug('CurDir: %s ' % cur_dir)

	cur_dir = os.sep.join([x for x in cur_dir if x != 'atualizador'])
	ws.log.info('CurDir: %s ' % cur_dir)

	if ws.info['env'].get('devel'):
		cur_dir = os.sep.join([cur_dir, 'teste_atualizador'])
		ws.log.info('CurDir Devel: %s ' % cur_dir)

	if ws.key:
		hidden = False
		if '--hidden' in sys.argv:
			sys.argv.remove('--hidden')
			hidden = True

		if not '--download' in sys.argv and not '--update' in sys.argv:
			sys.argv.extend([
				'--download',
				'--update',
			])

		from view.progress import ProgressApp

		ProgressApp(ws, cur_dir, hidden).run(*sys.argv)

	else:
		from view.cadastro import CadastroApp
		CadastroApp(ws, cur_dir).run()
	

