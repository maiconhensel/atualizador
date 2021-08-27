import logging
import os
import sys

if __name__ == '__main__':
	
	from core.workspace import ws

	print('Args: %s' % sys.argv)

	cur_dir = os.getcwd().split(os.sep)
	print('CurDir: %s ' % cur_dir)

	cur_dir = os.sep.join([x for x in cur_dir if x != 'atualizador'])
	print('CurDir: %s ' % cur_dir)

	if os.environ.get('DEVEL'):
		cur_dir = os.sep.join([cur_dir, 'teste_atualizador'])
		print('CurDir Devel: %s ' % cur_dir)

	ws.load(cur_dir)

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
	

