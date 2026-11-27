# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['secrets_manager', 'pyodbc', 'requests', 'cryptography', 'cert_manager', 'db_service', 'logger_service', 'reboot_service', 'totvs_chef_web', 'totvs_tec']

tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

playwright_data, playwright_binaries, playwright_imports = collect_all('playwright')
datas += [entry for entry in playwright_data if '.local-browsers' not in Path(entry[0]).parts]
binaries += [entry for entry in playwright_binaries if '.local-browsers' not in Path(entry[0]).parts]
hiddenimports += playwright_imports

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TOTVS-Cert-Uploader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
