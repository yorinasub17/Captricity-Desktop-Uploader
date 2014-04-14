# -*- mode: python -*-

root = '/Users/yoriyasuyano/Documents/captricity/Captricity-Desktop-Uploader'

hiddenimports = ['keyring.credentials',
                 'keyring.backends.file',
                 'keyring.backends.Gnome',
                 'keyring.backends.Google',
                 'keyring.backends.keyczar',
                 'keyring.backends.kwallet',
                 'keyring.backends.multi',
                 'keyring.backends.OS_X',
                 'keyring.backends.pyfs',
                 'keyring.backends.SecretService',
                 'keyring.backends.Windows',
                 'keyring.util',
                 'keyring.util.escape',
                 'keyring.util.XDG',
                 'keyring.util.platform_',
                 'keyring.util.properties']

a = Analysis(['capdesk.py'],
             pathex=[root],
             hiddenimports=hiddenimports,
             hookspath=None,
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
