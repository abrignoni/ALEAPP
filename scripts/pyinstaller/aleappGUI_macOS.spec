# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# mister_skinnylegs discovers its plugins at runtime via a filesystem glob
# (PLUGIN_PATH.glob("*_plugin.py")), so PyInstaller's import-graph analysis
# never sees them. 

msl_plugin_datas = collect_data_files('mister_skinnylegs.plugins', include_py_files=True)

a = Analysis(
    ['../../aleappGUI.py'],
    pathex=['../scripts/artifacts'],
    binaries=[],
    datas=[
        ('../', 'scripts'),
        ('../../assets', 'assets'),
        ('../../leapp_functions', 'leapp_functions'),
        *msl_plugin_datas
    ],
    hiddenimports=[
        # Artifacts are bundled as data files and imported from disk at runtime,
        # so PyInstaller's import-graph analysis never sees what they import.
        # hook-plugin_loader.py was meant to cover this but targets a bare
        # 'plugin_loader' module that no longer exists (it moved to
        # scripts.plugin_loader), so it never fires. Collect the packages
        # artifacts import wholesale; a missing submodule here is a startup
        # crash in the frozen build only.
        *collect_submodules('Crypto'),
        *collect_submodules('google.protobuf'),
        *collect_submodules('leapp_functions'),
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
    [],
    exclude_binaries=True,
    name='aleappGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='aleappGUI',
)
app = BUNDLE(
    coll,
    name='aleappGUI.app',
    icon='../../assets/icon.icns',
    bundle_identifier='4n6.brigs.ALEAPP',
    version='2026.2.0',
)
