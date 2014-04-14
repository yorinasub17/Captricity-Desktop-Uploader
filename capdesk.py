import sys
import keyring
import getpass
import multiprocessing
import PySide
from captools.api import Client

from new_upload import NewUploadWindow, UploadTracker

APP_NAME = "capdesk"

username = getpass.getuser()
client = None

class ApiTokenDialog(PySide.QtGui.QDialog):
    def __init__(self, parent=None):
        super(ApiTokenDialog, self).__init__(parent)
        self.resize(250, 100)

        self.setWindowTitle('API Token')
        self.instructions = PySide.QtGui.QLabel('Please enter your Captricity API Token', self)
        self.api_token_text = PySide.QtGui.QLineEdit(self)
        self.ok_button = PySide.QtGui.QPushButton('Ok', self)
        self.ok_button.clicked.connect(self.handle_ok)

        actions_layout = PySide.QtGui.QHBoxLayout()
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.ok_button)

        layout = PySide.QtGui.QVBoxLayout()
        layout.addWidget(self.instructions)
        layout.addWidget(self.api_token_text)
        layout.addLayout(actions_layout)
        self.setLayout(layout)

    def handle_ok(self):
        self.api_token = str(self.api_token_text.text()).strip()
        try:
            self.client = Client(self.api_token)
            self.client.read_user_profile()
            keyring.set_password(APP_NAME, username, self.api_token)
            self.accept()
        except:
            PySide.QtGui.QMessageBox.warning(self, 'Required API Token', 'A valid Captricity API Token is required to use the Captricity Desktop Client')


# Now initialize the main app
class MainWindow(PySide.QtGui.QMainWindow):
    def __init__(self, client, parent=None):
        self.cap_client = client
        self.pool = multiprocessing.Pool(multiprocessing.cpu_count() * 2)
        super(MainWindow, self).__init__(parent)

        self.resize(350, 250)
        self.setWindowTitle(APP_NAME)

        new_upload = PySide.QtGui.QAction('New Upload', self)
        new_upload.setShortcut('Ctrl+N')
        new_upload.setStatusTip('Initiate a new upload to Captricity')
        self.connect(new_upload, PySide.QtCore.SIGNAL('triggered()'), self.initiate_new_upload)

        exit = PySide.QtGui.QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, PySide.QtCore.SIGNAL('triggered()'), PySide.QtCore.SLOT('close()'))

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
        self.new_upload_window = NewUploadWindow(self.cap_client, self)
        self.new_upload_window.resize(350, 250)
        self.new_upload_window.show()

    def close_new_upload(self):
        self.new_upload_window = None

    def add_upload_tracker(self, upload_manager):
        self.main_widget.add_upload_tracker(upload_manager)

class MainWidget(PySide.QtGui.QWidget):
    def __init__(self, parent=None):
        self.progress_bars = []
        super(MainWidget, self).__init__(parent)

        self.container_widget = PySide.QtGui.QWidget()
        self.container_layout = PySide.QtGui.QVBoxLayout(self)
        self.container_widget.setLayout(self.container_layout)

        self.scroll_area = PySide.QtGui.QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(PySide.QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(PySide.QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.container_widget)
        
        self.layout_ = PySide.QtGui.QVBoxLayout(self)
        self.layout_.addWidget(self.scroll_area)
        self.setLayout(self.layout_)

    def add_upload_tracker(self, upload_manager):
        pbar = UploadTracker(upload_manager)
        self.progress_bars.append(pbar)
        self.container_layout.addWidget(pbar)
        upload_manager.start()
        self.container_widget.resize(1000, 75 * len(self.progress_bars))

if __name__ == '__main__':
    app = PySide.QtGui.QApplication(sys.argv)

    # Obtain the API token from the keyring if it exists. Otherwise, have the user enter it.
    api_token = keyring.get_password(APP_NAME, username)
    if not api_token:
        #Open dialog box to obtain api_token from user and store it
        dialog = ApiTokenDialog()
        if not dialog.exec_() == PySide.QtGui.QDialog.Accepted:
            sys.exit(0)
        client = dialog.client
    else:
        client = Client(api_token)

    main = MainWindow(client)
    main.show()
    if sys.platform == 'darwin':
        main.raise_()
    sys.exit(app.exec_())
