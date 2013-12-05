'''
Contains all the GUI and backend code to initiate new uploads to Captricity.
'''
import os
import glob

from PyQt4 import QtCore, QtGui

from utils import delete_layout, natural_sort

class NewUploadWindow(QtGui.QWidget):
    def __init__(self, cap_client, main_window, parent=None):
        self.cap_client = cap_client
        self.main_window = main_window
        self.layout_ = None
        self.upload_manager = None
        super(NewUploadWindow, self).__init__(parent)

        self.load_menu_window()

    def refresh_layout(self):
        self.setLayout(self.layout_)
        self.show()

    def upload_to_document(self):
        document_getter = lambda: self.cap_client.read_documents('?user_visible=true&active=true')
        self.load_list_window(document_getter, self.document_upload_callback_func_generator)

    def upload_to_job(self):
        job_getter = lambda: self.cap_client.read_jobs('?status=pending')
        self.load_list_window(job_getter, self.job_upload_callback_func_generator)

    def cancel(self):
        self.close()
        self.main_window.close_new_upload()

    def document_upload_callback_func_generator(self, document_id):
        def callback():
            directory = str(QtGui.QFileDialog.getExistingDirectory(None, 'Select directory to upload'))
            if directory:
                self.upload_manager = UploadToDocument(document_id, directory)
                self.load_confirm_window(self.upload_manager)
        return callback

    def job_upload_callback_func_generator(self, job_id):
        def callback():
            directory = str(QtGui.QFileDialog.getExistingDirectory(None, 'Select directory to upload'))
            if directory:
                self.upload_manager = UploadToJob(job_id, directory)
                self.load_confirm_window(self.upload_manager)
        return callback

    def upload(self):
        # Trigger upload
        self.close()
        print 'Triggering upload!'

    def load_menu_window(self):
        delete_layout(self.layout_)
        self.load_prev_window = self.cancel
        self.load_current_window = self.load_menu_window

        self.close()
        self.resize(350, 250)

        upload_to_document = QtGui.QPushButton('Upload to Template', self)
        self.connect(upload_to_document, QtCore.SIGNAL('clicked()'), self.upload_to_document)

        upload_to_job = QtGui.QPushButton('Upload to Job', self)
        self.connect(upload_to_job, QtCore.SIGNAL('clicked()'), self.upload_to_job)

        cancel = QtGui.QPushButton('Cancel', self)
        self.connect(cancel, QtCore.SIGNAL('clicked()'), self.load_prev_window)

        self.layout_ = QtGui.QVBoxLayout()
        self.layout_.addWidget(upload_to_document)
        self.layout_.addWidget(upload_to_job)
        self.layout_.addWidget(cancel)
        self.refresh_layout()

    def load_list_window(self, get_captricity_objects, callback_func_generator):
        delete_layout(self.layout_)
        self.load_prev_window = self.load_menu_window
        self.load_current_window = lambda: self.load_list_window(get_captricity_objects, callback_func_generator)

        captricity_objects = get_captricity_objects()

        buttons = []
        for obj in captricity_objects:
            button = QtGui.QPushButton(obj['name'], self)
            self.connect(button, QtCore.SIGNAL('clicked()'), callback_func_generator(obj['id']))
            buttons.append(button)

        refresh_button = QtGui.QPushButton('Refresh', self)
        self.connect(refresh_button, QtCore.SIGNAL('clicked()'), lambda: self.load_list_window(get_captricity_objects, callback_func_generator))

        back_button = QtGui.QPushButton('Back', self)
        self.connect(back_button, QtCore.SIGNAL('clicked()'), self.load_prev_window)

        actions_layout = QtGui.QHBoxLayout()
        actions_layout.addStretch(1)
        actions_layout.addWidget(refresh_button)
        actions_layout.addWidget(back_button)

        button_layout = QtGui.QVBoxLayout()
        for button in buttons:
            button_layout.addWidget(button)

        self.layout_ = QtGui.QVBoxLayout()
        self.layout_.addLayout(button_layout)
        self.layout_.addLayout(actions_layout)
        self.refresh_layout()

    def load_confirm_window(self, upload_manager):
        delete_layout(self.layout_)
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

        self.layout_ = QtGui.QVBoxLayout()
        self.layout_.addWidget(instructions)
        self.layout_.addWidget(list_widget)
        self.layout_.addLayout(actions_layout)
        self.refresh_layout()

class UploadToDocument(object):
    def __init__(self, document_id, directory):
        self.document_id = document_id
        self.directory = directory
        self.files = natural_sort(glob.glob(os.path.join(directory, '*')))

class UploadToJob(object):
    def __init__(self, job_id, directory):
        self.job_id = job_id
        self.directory = directory
        self.files = natural_sort(glob.glob(os.path.join(directory, '*')))
