# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# mister_skinnylegs discovers its plugins at runtime via a filesystem glob
# (PLUGIN_PATH.glob("*_plugin.py")), so PyInstaller's import-graph analysis
# never sees them. 

msl_plugin_datas = collect_data_files('mister_skinnylegs.plugins', include_py_files=True)

a = Analysis(
    ['../../aleapp.py'],
    pathex=['../scripts/artifacts'],
    binaries=[],
    datas=[
        ('../', 'scripts'),
        ('../../leapp_functions', 'leapp_functions'),
        ('../../assets', 'assets'),
        *msl_plugin_datas],
    hiddenimports=[
        # Artifacts are bundled as data files and imported from disk at runtime,
        # so PyInstaller's import-graph analysis never sees what they import.
        # Collect the packages
        # artifacts import wholesale; a missing submodule here is a startup
        # crash in the frozen build only.
        *collect_submodules('Crypto'),
        *collect_submodules('google.protobuf'),
        *collect_submodules('leapp_functions'),
        *collect_submodules('PIL'),
        'bcrypt',
        'bencoding',
        'bs4',
        'Crypto.Cipher.AES',
        'Crypto.Util.Padding',
        'fitdecode',
        'html.parser',
        'mister_skinnylegs',
        'polyline',
        'uuid',
        'xmltodict',
        'zoneinfo'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='aleapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
