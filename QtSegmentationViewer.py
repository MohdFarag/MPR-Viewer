
from SegmentationViewer import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from QtViewer import *

class QtSegmentationViewer(QtViewer):

    def __init__(self, vtkBaseClass, label:str="Segmentation Viewer"):
        super(QtSegmentationViewer, self).__init__()

        # Properties
        self.label = label

        ## Render Viewer
        self.viewer = SegmentationViewer(vtkBaseClass, self.label)

        # Initialize the UI        
        self._init_UI()
        
        # Connect signals and slots
        self.connect()

    def _init_UI(self):
        super()._init_UI()
        
        # Set up the layout
        self.mainLayout.addItem(QSpacerItem(10,20))