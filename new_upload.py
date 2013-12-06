'''
Contains all the GUI and backend code to initiate new uploads to Captricity.
'''
import os
import glob
import itertools

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
        job_getter = lambda: self.cap_client.read_jobs('?status=setup')
        self.load_list_window(job_getter, self.job_upload_callback_func_generator)

    def cancel(self):
        self.close()
        self.main_window.close_new_upload()

    def document_upload_callback_func_generator(self, document):
        def callback():
            directory = str(QtGui.QFileDialog.getExistingDirectory(None, 'Select directory to upload'))
            if directory:
                self.upload_manager = UploadToDocument(self.main_window.cap_client, self.main_window.pool, document['id'], document['sheet_count'], directory)
                self.load_confirm_window(self.upload_manager)
        return callback

    def job_upload_callback_func_generator(self, job):
        def callback():
            directory = str(QtGui.QFileDialog.getExistingDirectory(None, 'Select directory to upload'))
            if directory:
                self.upload_manager = UploadToJob(self.main_window.cap_client, self.main_window.pool, job['id'], job['sheet_count'], directory)
                self.load_confirm_window(self.upload_manager)
        return callback

    def upload(self):
        # Trigger upload
        self.close()
        self.main_window.add_upload_tracker(self.upload_manager)

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
            self.connect(button, QtCore.SIGNAL('clicked()'), callback_func_generator(obj))
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

class UploadTracker(QtGui.QWidget):
    def __init__(self, upload_manager, parent=None):
        self.upload_manager = upload_manager
        self.upload_manager.link_pbar(self)
        super(UploadTracker, self).__init__(parent)

        self.load_window()
        
    def load_window(self):
        self.resize(300, 50)
        self.label = QtGui.QLabel(self.upload_manager.label, self)
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setValue(0)
        self.pbar.setGeometry(0, 25, 200, 25)

    def setValue(self, *args):
        self.pbar.setValue(*args)

class Uploader(object):
    def __init__(self, client, pool, sheet_count, directory):
        self.result_set = None
        self.linked_pbar = None
        self.client = client
        self.pool = pool
        self.directory = directory
        self.files = natural_sort(glob.glob(os.path.join(directory, '*')))
        self.grouped_files = itertools.izip_longest(*(iter(self.files),) * sheet_count)

    def link_pbar(self, pbar):
        self.linked_pbar = pbar

    def start(self):
        assert self.linked_pbar is not None
        if self.job_id is None:
            new_job = self.client.create_jobs({'document_id': str(self.document_id)})
            self.job_id = new_job['id']
        self.result_set = [0 for i in range(len(self.grouped_files))]
        for i, files in enumerate(self.grouped_files):
            self.pool.apply_async(upload_iset, (self.client, self.job_id, files), callback=self.upload_finished_callback_generator(i))

    def upload_finished_callback_generatory(self, idx):
        def callback():
            if self.result_set is not None:
                self.result_set[idx] = 1
                self.linked_pbar.setValue(int(sum(self.result_set) * 100 / len(self.result_set)))
        return callback

class UploadToDocument(Uploader):
    def __init__(self, client, pool, document_id, sheet_count, directory):
        self.document_id = document_id
        self.job_id = None
        super(UploadToDocument, self).__init__(client, pool, sheet_count, directory)
        self.label = 'Document %s: %s' % (self.document_id, self.directory)

class UploadToJob(Uploader):
    def __init__(self, client, pool, job_id, sheet_count, directory):
        self.job_id = job_id
        super(UploadToJob, self).__init__(client, pool, sheet_count, directory)
        self.label = 'Job %s: %s' % (self.job_id, self.directory)

def upload_iset(client, job_id, files):
    iset = client.create_instance_sets(job_id)
    for i, fname in enumerate(files):
        client.create_instance_set_instances(iset['id'], {'image_file': open(fname), 'page_number': str(i)})
