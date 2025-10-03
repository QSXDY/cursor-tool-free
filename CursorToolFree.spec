# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icons/*.png', 'resources/icons'),
        ('resources/icons/*.svg', 'resources/icons'),
        ('resources/fonts/*.ttf', 'resources/fonts'),
        ('resources/fonts/*.md', 'resources/fonts'),
        ('icon.png', '.'),
        ('icon.ico', '.'),
        ('icon.icns', '.'),
    ],
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
    name='CursorToolFree',
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
    version='version_info.txt' if sys.platform == 'win32' else None,
    icon='icon.icns' if sys.platform == 'darwin' else 'icon.ico'
)

# macOS .app bundle configuration
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='CursorToolFree.app',
        icon='icon.icns',
        bundle_identifier='com.cursortool.free',
        info_plist={
            'CFBundleName': 'Cursor Tool Free',
            'CFBundleDisplayName': 'Cursor Tool Free',
            'CFBundleVersion': '1.0.3',
            'CFBundleShortVersionString': '1.0.3',
            'CFBundleExecutable': 'CursorToolFree',
            'CFBundleIdentifier': 'com.cursortool.free',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
            'NSPrincipalClass': 'NSApplication',
            'NSRequiresAquaSystemAppearance': False,
        },
    )
