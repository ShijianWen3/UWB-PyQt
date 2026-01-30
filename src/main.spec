# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_test.py'],
    pathex=[],
    binaries=[],
    datas=[
#        ('icons', 'icons'),  # 打包图标文件夹
#        ('resources', 'resources'),  # 打包资源文件
#        ('config.ini', '.'),  # 打包配置文件到根目录
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'numpy',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='UWB_Application',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 关闭控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../install/icon/UWB_256x256.ico',  # 应用程序图标
    version_file=None,  # 可以添加版本信息文件
)
