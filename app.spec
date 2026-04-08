# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect ALL files, binaries, and hidden imports for these packages
np_datas, np_binaries, np_hiddenimports = collect_all('numpy')
pd_datas, pd_binaries, pd_hiddenimports = collect_all('pandas')
sk_datas, sk_binaries, sk_hiddenimports = collect_all('sklearn')
wv_datas, wv_binaries, wv_hiddenimports = collect_all('webview')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[] + np_binaries + pd_binaries + sk_binaries + wv_binaries,
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('ml_data', 'ml_data'),
        ('database/schema.sql', 'database'),
    ] + np_datas + pd_datas + sk_datas + wv_datas,
    hiddenimports=[
        'numpy', 'numpy._core', 'numpy._core._multiarray_umath',
        'numpy._core.multiarray', 'numpy._core.numeric', 'numpy._core.umath',
        'numpy.core', 'numpy.core._methods', 'numpy.lib', 'numpy.linalg', 'numpy.random',
        'pandas', 'pandas._libs', 'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.np_datetime', 'pandas._libs.tslibs.nattype',
        'pandas._libs.missing',
        'sklearn', 'sklearn.ensemble', 'sklearn.ensemble._forest',
        'sklearn.tree', 'sklearn.tree._utils', 'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs', 'sklearn.neighbors._partition_nodes',
        'flask', 'flask_login', 'flask_sqlalchemy', 'werkzeug', 'werkzeug.security',
        'webview', 'webview.platforms.winforms', 'clr',
        'pickle', 'sqlite3',
    ] + np_hiddenimports + pd_hiddenimports + sk_hiddenimports + wv_hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StudentResultSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    onefile=True,
    icon=['TEMITOPE.ico'],   
)