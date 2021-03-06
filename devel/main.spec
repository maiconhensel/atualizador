# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['..\\main.py'],
	pathex=['C:\\sistemas\\updater'],
	binaries=[],
	datas=[],
	hiddenimports=[],
	hookspath=[],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False
)

pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=block_cipher
)
a.datas += [
    ('resources\\logo.ico','.\\resources\\logo.ico', 'Data'),
    ('resources\\logo_linx.png','.\\resources\\logo_linx.png', 'Data'),
    ('resources\\logo-linx.png','.\\resources\\logo-linx.png', 'Data'),
    ('resources\\bt-icone-check.png','.\\resources\\bt-icone-check.png', 'Data'),
    ('resources\\bt-icone-close.png','.\\resources\\bt-icone-close.png', 'Data'),
    ('resources\\bt-icone-input-busca.png','.\\resources\\bt-icone-input-busca.png', 'Data'),
]

exe = EXE(pyz,
	a.scripts,
	a.binaries,
	a.zipfiles,
	a.datas,  
	[],
	name='atualizador',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	upx_exclude=[],
	runtime_tmpdir=None,
	console=False,
	disable_windowed_traceback=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None,
	uac_admin=True, 
	icon='..\\resources\\logo.ico'
)
