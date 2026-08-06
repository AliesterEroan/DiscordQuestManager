# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\user\\OneDrive\\Desktop\\DiscordQuestManager\\version 1.1.0\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\user\\OneDrive\\Desktop\\DiscordQuestManager\\version 1.1.0\\discord.png', '.'), ('C:\\Users\\user\\OneDrive\\Desktop\\DiscordQuestManager\\version 1.1.0\\assets', 'assets'), ('C:\\Users\\user\\OneDrive\\Desktop\\DiscordQuestManager\\version 1.1.0\\core\\themes\\*.json', 'core/themes'), ('C:\\Users\\user\\OneDrive\\Desktop\\DiscordQuestManager\\version 1.1.0\\help.html', '.')],
    hiddenimports=[],
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
    name='DiscordQuestManager',
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
    icon=['C:\\Users\\user\\OneDrive\\Desktop\\DiscordQuestManager\\version 1.1.0\\app_icon.ico'],
)
