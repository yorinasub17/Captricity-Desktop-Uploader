# -*- mode: python -*-

root = '/Users/yoriyasuyano/Documents/captricity/Captricity-Desktop-Uploader'

a = Analysis(['capdesk.py'],
             pathex=[root],
             hiddenimports=[],
             hookspath=['pyinstaller-pyside-hooks/'],
             runtime_hooks=None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join(root, 'dist', 'capdesk'),
          debug=False,
          strip=None,
          upx=False,
          console=False )
app = BUNDLE(exe,
             name=os.path.join(root, 'dist', 'capdesk.app'),
             icon='icons/CapIcon.icns')
