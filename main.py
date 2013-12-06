import sys
import keyring
import getpass
from captools.api import Client

from PyQt4 import QtGui, QtCore

from new_upload import NewUploadWindow, UploadTracker

APP_NAME = "capdesk"

username = getpass.getuser()

# Obtain the API token from the keyring if it exists. Otherwise, have the user enter it.
api_token = keyring.get_password(APP_NAME, username)
if not api_token:
    #TODO open dialog box to obtain api_token from user and store it
    api_token = raw_input('Enter your API token: ')
    keyring.set_password(APP_NAME, username, api_token.strip())

cap_client = Client(api_token)

# Now initialize the main app
class MainWindow(QtGui.QMainWindow):
    def __init__(self, cap_client, parent=None):
        self.cap_client = cap_client
        super(MainWindow, self).__init__(parent)

        self.resize(350, 250)
        self.setWindowTitle(APP_NAME)

        new_upload = QtGui.QAction(QtGui.QIcon('icons/Gnome-mail-message-new.png'), 'New Upload', self)
        new_upload.setShortcut('Ctrl+N')
        new_upload.setStatusTip('Initiate a new upload to Captricity')
        self.connect(new_upload, QtCore.SIGNAL('triggered()'), self.initiate_new_upload)

        exit = QtGui.QAction(QtGui.QIcon('icons/Gnome-application-exit.png'), 'Exit', self)
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

        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)

    def initiate_new_upload(self):
        self.new_upload_window = NewUploadWindow(cap_client, self)
        self.new_upload_window.resize(350, 250)
        self.new_upload_window.show()

    def close_new_upload(self):
        self.new_upload_window = None

    def add_upload_tracker(self, upload_manager):
        self.main_widget.add_upload_tracker(upload_manager)

class MainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        self.progress_bars = []
        super(MainWidget, self).__init__(parent)

        self.layout_ = QtGui.QVBoxLayout()
        self.setLayout(self.layout_)

    def add_upload_tracker(self, upload_manager):
        pbar = UploadTracker(upload_manager)
        self.progress_bars.append(pbar)
        self.layout_.addWidget(pbar)

app = QtGui.QApplication(sys.argv)
main = MainWindow(cap_client)
main.show()
sys.exit(app.exec_())
