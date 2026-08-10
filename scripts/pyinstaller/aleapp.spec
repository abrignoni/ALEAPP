# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files

# mister_skinnylegs discovers its plugins at runtime via a filesystem glob
# (PLUGIN_PATH.glob("*_plugin.py")), so PyInstaller's import-graph analysis
# never sees them. 

msl_plugin_datas = collect_data_files('mister_skinnylegs.plugins', include_py_files=True)

a = Analysis(
   ['..\\..\\aleapp.py'],
   pathex=['..\\scripts\\artifacts'],
   binaries=[],
   datas=[('..\\', '.\\scripts'), *msl_plugin_datas],
   hiddenimports=[
      'bcrypt',
      'bencoding',
      'bs4',
      'Crypto.Cipher.AES',
      'Crypto.Util.Padding',
      'fitdecode',
      'html.parser',
      'mister_skinnylegs',
      'PIL.Image',
      'polyline',
      'uuid',
      'xmltodict',
      'zoneinfo'
   ],
   hookspath=['.\\'],
   runtime_hooks=[],
   excludes=[],
   win_no_prefer_redirects=False,
   win_private_assemblies=False,
   cipher=block_cipher,
   noarchive=False)

pyz = PYZ(
   a.pure, a.zipped_data,
   cipher=block_cipher)

exe = EXE(
   pyz,
   a.scripts,
   a.binaries,
   a.zipfiles,
   a.datas,
   [],
   name='aleapp',
   debug=False,
   bootloader_ignore_signals=False,
   strip=False,
   upx=True,
   upx_exclude=[],
   runtime_tmpdir=None,
   version='aleapp-file_version_info.txt',
   console=True )
