# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../../aleappGUI.py'],
    pathex=['../scripts/artifacts'],
    binaries=[],
    datas=[('../', 'scripts'), ('../../assets', 'assets')],
    hiddenimports=[
        'bcrypt',
        'bencoding',
        'blackboxprotobuf',
        'bs4',
        'Crypto.Cipher.AES',
        'Crypto.Util.Padding',
        'fitdecode',
        'folium',
        'html.parser',
        'PIL.Image',
        'polyline',
        'xmltodict',
        'xlsxwriter',
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
    version='3.4.0',
)
