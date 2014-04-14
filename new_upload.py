'''
Contains all the GUI and backend code to initiate new uploads to Captricity.
'''
import os
import glob
from captools.api import Client

from PySide import QtCore, QtGui

from utils import delete_layout, natural_sort, is_supported_file

class NewUploadWindow(QtGui.QWidget):
    MENU_WINDOW = 0
    LIST_WINDOW = 1
    CREATE_WINDOW = 2
    CONFIRM_WINDOW = 3
    DEFAULT_BATCH_NAME = 'New Batch'

    def __init__(self, cap_client, main_window, parent=None):
        self.cap_client = cap_client
        self.main_window = main_window
        self.upload_manager = None

        self.menu_layout = QtGui.QVBoxLayout()
        self.menu_widget = QtGui.QWidget()
        self.menu_widget.setLayout(self.menu_layout)

        self.list_layout = QtGui.QVBoxLayout()
        self.list_widget = QtGui.QWidget()
        self.list_widget.setLayout(self.list_layout)

        self.confirm_layout = QtGui.QVBoxLayout()
        self.confirm_widget = QtGui.QWidget()
        self.confirm_widget.setLayout(self.confirm_layout)

        self.create_layout = QtGui.QVBoxLayout()
        self.create_widget = QtGui.QWidget()
        self.create_widget.setLayout(self.create_layout)

        self.layout_ = QtGui.QStackedLayout()
        self.layout_.addWidget(self.menu_widget)
        self.layout_.addWidget(self.list_widget)
        self.layout_.addWidget(self.create_widget)
        self.layout_.addWidget(self.confirm_widget)

        super(NewUploadWindow, self).__init__(parent)

        self.setLayout(self.layout_)
        self.load_menu_window()

        self.new_batch_name = NewUploadWindow.DEFAULT_BATCH_NAME

    def upload_to_batch(self):
        batch_getter = lambda: self.cap_client.read_batches('?status=setup')
        self.load_list_window(batch_getter, self.batch_upload_callback_func_generator)

    def create_batch(self):
        new_batch = self.cap_client.create_batches({'name': self.new_batch_name})
        self.batch_upload_callback_func_generator(new_batch)()

    def cancel(self):
        self.close()
        self.main_window.close_new_upload()

    def batch_upload_callback_func_generator(self, batch):
        def callback():
            directory = str(QtGui.QFileDialog.getExistingDirectory(None, 'Select directory to upload'))
            if directory:
                self.upload_manager = UploadToBatch(self.main_window.cap_client, self.main_window.pool, batch['id'], directory)
                self.load_confirm_window(self.upload_manager)
        return callback

    def upload(self):
        # Trigger upload
        self.close()
        self.main_window.add_upload_tracker(self.upload_manager)

    def load_menu_window(self):
        delete_layout(self.menu_layout, delete_container=False)
        self.layout_.setCurrentIndex(NewUploadWindow.MENU_WINDOW)

        self.load_prev_window = self.cancel
        self.load_current_window = self.load_menu_window

        self.close()
        self.resize(350, 250)

        upload_to_batch = QtGui.QPushButton('Upload to Batch', self)
        self.connect(upload_to_batch, QtCore.SIGNAL('clicked()'), self.upload_to_batch)

        cancel = QtGui.QPushButton('Cancel', self)
        self.connect(cancel, QtCore.SIGNAL('clicked()'), self.load_prev_window)

        self.menu_layout.addWidget(upload_to_batch)
        self.menu_layout.addWidget(cancel)

    def load_list_window(self, get_captricity_objects, callback_func_generator):
        delete_layout(self.list_layout, delete_container=False)
        self.layout_.setCurrentIndex(NewUploadWindow.LIST_WINDOW)

        self.load_prev_window = self.load_menu_window
        self.load_current_window = lambda: self.load_list_window(get_captricity_objects, callback_func_generator)

        captricity_objects = get_captricity_objects()

        buttons = []
        for obj in captricity_objects:
            button = QtGui.QPushButton(obj['name'], self)
            self.connect(button, QtCore.SIGNAL('clicked()'), callback_func_generator(obj))
            buttons.append(button)

        create_button = QtGui.QPushButton('Create', self)
        self.connect(create_button, QtCore.SIGNAL('clicked()'), self.load_create_window)

        refresh_button = QtGui.QPushButton('Refresh', self)
        self.connect(refresh_button, QtCore.SIGNAL('clicked()'), self.load_current_window)

        back_button = QtGui.QPushButton('Back', self)
        self.connect(back_button, QtCore.SIGNAL('clicked()'), self.load_prev_window)

        actions_layout = QtGui.QHBoxLayout()
        actions_layout.addStretch(1)
        actions_layout.addWidget(create_button)
        actions_layout.addWidget(refresh_button)
        actions_layout.addWidget(back_button)

        button_layout = QtGui.QVBoxLayout()
        for button in buttons:
            button_layout.addWidget(button)

        self.list_layout.addLayout(button_layout)
        self.list_layout.addLayout(actions_layout)

    def load_confirm_window(self, upload_manager):
        delete_layout(self.confirm_layout, delete_container=False)
        self.layout_.setCurrentIndex(NewUploadWindow.CONFIRM_WINDOW)

        self.load_prev_window = self.load_current_window
        self.load_current_window = lambda: self.load_confirm_window(upload_manager)

        instructions = QtGui.QLabel('We will upload the following files:')

        list_widget = QtGui.QListWidget()
        for fname in upload_manager.files:
            list_widget.addItem(os.path.basename(fname))

        next_button = QtGui.QPushButton('Next')
        self.connect(next_button, QtCore.SIGNAL('clicked()'), self.upload)

        cancel_button = QtGui.QPushButton('Cancel', self)
        self.connect(cancel_button, QtCore.SIGNAL('clicked()'), self.load_prev_window)

        actions_layout = QtGui.QHBoxLayout()
        actions_layout.addStretch(1)
        actions_layout.addWidget(cancel_button)
        actions_layout.addWidget(next_button)

        self.confirm_layout.addWidget(instructions)
        self.confirm_layout.addWidget(list_widget)
        self.confirm_layout.addLayout(actions_layout)

    def load_create_window(self):
        delete_layout(self.create_layout, delete_container=False)
        self.layout_.setCurrentIndex(NewUploadWindow.CREATE_WINDOW)

        self.load_prev_window = self.load_current_window
        self.load_current_window = lambda: self.load_create_window()

        instructions = QtGui.QLabel('Name this batch')

        self.new_batch_name = NewUploadWindow.DEFAULT_BATCH_NAME
        name_box = QtGui.QLineEdit(self)
        def name_box_changed(text):
            self.new_batch_name = text
        name_box.textChanged[str].connect(name_box_changed)

        next_button = QtGui.QPushButton('Next')
        self.connect(next_button, QtCore.SIGNAL('clicked()'), self.create_batch)

        cancel_button = QtGui.QPushButton('Cancel', self)
        self.connect(cancel_button, QtCore.SIGNAL('clicked()'), self.load_prev_window)

        actions_layout = QtGui.QHBoxLayout()
        actions_layout.addStretch(1)
        actions_layout.addWidget(cancel_button)
        actions_layout.addWidget(next_button)

        self.create_layout.addWidget(instructions)
        self.create_layout.addWidget(name_box)
        self.create_layout.addLayout(actions_layout)

class UploadTracker(QtGui.QWidget):
    image_uploaded = QtCore.Signal()

    def __init__(self, upload_manager, parent=None):
        self.upload_manager = upload_manager
        self.upload_manager.link_pbar(self)
        super(UploadTracker, self).__init__(parent)

        self.load_window()

        self.image_uploaded.connect(self.handle_update)
        
    def load_window(self):
        self.resize(300, 50)
        self.label = QtGui.QLabel(self.upload_manager.label, self)
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setValue(0)
        self.pbar.setGeometry(0, 25, 200, 25)

    def handle_update(self):
        self.pbar.setValue(self.upload_manager.progress)

class Uploader(object):
    def __init__(self, client, pool, directory):
        self.result_set = None
        self.linked_pbar = None
        self.client = client
        self.pool = pool
        self.directory = directory
        self.files = natural_sort(filter(is_supported_file, glob.glob(os.path.join(directory, '*'))))

    def link_pbar(self, pbar):
        self.linked_pbar = pbar

    def start(self):
        assert self.linked_pbar is not None
        if self.batch_id is None:
            new_batch = self.client.create_batchs()
            self.batch_id = new_batch['id']
        self.result_set = [0 for i in xrange(len(self.files))]
        for idx, f in enumerate(self.files):
            self.pool.apply_async(upload_file, (self.client.api_token, self.batch_id, f), callback=self.upload_finished_callback_generator(idx))

    def upload_finished_callback_generator(self, idx):
        def callback(result):
            if self.result_set is not None:
                self.result_set[idx] = 1
            # Trigger a signal
            self.linked_pbar.image_uploaded.emit()
        return callback

    @property
    def progress(self):
        return int(sum(self.result_set) * 100 / len(self.result_set))

class UploadToBatch(Uploader):
    def __init__(self, client, pool, batch_id, directory):
        self.batch_id = batch_id
        super(UploadToBatch, self).__init__(client, pool, directory)
        self.label = 'Batch %s: %s' % (self.batch_id, self.directory)

def upload_file(api_token, batch_id, f):
    client = Client(api_token)
    client.create_batch_files(batch_id, {'uploaded_file': open(f)})
