import os
import sys

pyinstaller_path = os.sep.join(sys.executable.split(os.sep)[:-1] + ['Scripts', 'pyinstaller'])

parametro_list = [pyinstaller_path, '--noconfirm', '--clean', '--windowed', os.path.join('devel', 'main.spec')]

os.spawnve(os.P_WAIT, pyinstaller_path, parametro_list, os.environ)
