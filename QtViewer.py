
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QtViewer(QWidget):

    # Constructor
    def __init__(self):
        super(QtViewer, self).__init__()
        self.viewer = None
        
    # Destructor
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.viewer.Finalize()

    # Initialize the UI
    def _init_UI(self):
        # Set up the layouts
        self.mainLayout = QVBoxLayout()
        
        self.topLayout = QHBoxLayout()
        self.topLayout.addWidget(self.viewer)
        self.mainLayout.addLayout(self.topLayout)
        
        self.setLayout(self.mainLayout)
        
    # Connect signals and slots
    def connect(self):
        pass

    # Getters and setters
    def get_viewer(self):
        return self.viewer
    
    # Connect on data    
    def connect_on_data(self, path):
        self.viewer.connect_on_data(path)
    
    # Render the viewer
    def render(self):
        self.viewer.render()