import sys
import keyring
import getpass

from PyQt4 import QtGui, QtCore

from new_upload import NewUploadWindow

APP_NAME = "capdesk"

username = getpass.getuser()

# Obtain the API token from the keyring if it exists. Otherwise, have the user enter it.
api_token = keyring.get_password(APP_NAME, username)
if api_token is None:
    #TODO open dialog box to obtain api_token from user and store it
    api_token = raw_input('Enter your API token: ')
    keyring.set_password(APP_NAME, username, api_token.strip())

# Now initialize the main app
class MainWindow(QtGui.QtMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(350, 250)
        self.setWindowTitle(APP_NAME)

        new_upload = QtGui.QAction(QtGui.QIcon('icons/document-send.png'), 'New Upload', self)
        new_upload.setShortcut('Ctrl+N')
        new_upload.setStatusTip('Initiate a new upload to Captricity')
        self.connect(new_upload, QtCore.SIGNAL('triggered()'), self.initiate_new_upload)

        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.statusBar()

        menu = self.menuBar()
        file_menu = menu.addMenu('File')
        file_menu.addAction(new_upload)
        file_menu.addAction(exit)

        toolbar = self.addToolBar('Main')
        toolbar.addAction(new_upload)
        toolbar.addAction(exit)

        self.new_upload_window = NewUploadWindow(self)

    def initiate_new_upload(self):
        self.new_upload_window.exec_()
 
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())