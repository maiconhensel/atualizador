import os
import sys

pyinstaller_path = os.sep.join(sys.executable.split(os.sep)[:-1] + ['Scripts', 'pyinstaller'])

os.spawnve(os.P_WAIT, pyinstaller_path, [pyinstaller_path, '-w', os.path.join('devel', 'main.spec')], os.environ)
