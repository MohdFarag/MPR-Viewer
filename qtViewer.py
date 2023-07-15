
from OrthoViewer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QtViewer(QWidget):

    def __init__(self, label, orientation=SLICE_ORIENTATION_ORTHO):
        super(QtViewer, self).__init__()

        # Properties
        self.label = label
        
        # PyQt Stuff
        ## Render Viewer
        self.orthoViewer = OrthoViewer(orientation)

        ## Slider
        self.slider = QSlider(Qt.Vertical)
        self.slider.setSingleStep(1)
        self.slider.setValue(0)
        self.slider.setEnabled(False)
        
        ## Buttons
        self.buttonsLayout = QHBoxLayout()
        self.playPause_button = QPushButton("play")
        self.prev_button = QPushButton("previous")
        self.stop_button = QPushButton("stop")
        self.next_button = QPushButton("next")
        self.buttonsLayout.addWidget(self.playPause_button)
        self.buttonsLayout.addWidget(self.prev_button)
        self.buttonsLayout.addWidget(self.stop_button)
        self.buttonsLayout.addWidget(self.next_button)
        
        # Set up the layouts
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        topLayout.addWidget(self.orthoViewer)
        topLayout.addWidget(self.slider)
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(self.buttonsLayout)
        self.setLayout(mainLayout)
        
        self.connect()

    def connect(self):
        # Connect slider signals to slice update slots
        self.slider.valueChanged.connect(self.update_slice)
        
        # Connect buttons to slots
        # self.playPause_button.clicked.connect(lambda: self.playSlices(0))        
        # self.prev_button.clicked.connect(lambda: self.playSlices(0))        
        # self.stop_button.clicked.connect(lambda: self.worker.stop())
        # self.next_button.clicked.connect(lambda: self.worker.stop())
    
    def update_slice(self, slice_index):
        self.orthoViewer.set_slice(slice_index)
        
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.orthoViewer.Finalize()
        
    def getOrthoViewer(self):
        return self.orthoViewer

    def connect_on_data(self, path):
        self.orthoViewer.connect_on_data(path)
    
    def display_data(self):
        # Settings of the slider
        self.slider.setEnabled(True)
        self.slider.setMaximum(self.orthoViewer.max_slice)
        self.slider.setMinimum(self.orthoViewer.min_slice)
        self.slider.setValue(self.orthoViewer.current_slice)
        # Display the data
        self.orthoViewer.display()