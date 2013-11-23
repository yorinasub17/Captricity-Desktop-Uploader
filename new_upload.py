'''
Contains all the GUI and backend code to initiate new uploads to Captricity.
'''

from PyQt4 import QtCore, QtGui

class NewUploadWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(NewUploadWindow, self).__init__(parent)

        upload_to_template = QtGui.QPushButton('Upload to Template', self)
        self.connect(upload_to_template, QtCore.SIGNAL('clicked()'), self.upload_to_template)

        upload_to_job = QtGui.QPushButton('Upload to Job', self)
        self.connect(upload_to_job, QtCore.SIGNAL('clicked()'), self.upload_to_job)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(upload_to_template)
        vbox.addWidget(upload_to_job)
        self.set_layout(vbox)

    def upload_to_template(self):
        print 'Uploading to template'

    def upload_to_job(self):
        print 'Uploading to job'
