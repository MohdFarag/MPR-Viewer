
from SegmentationViewer import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Worker import *

from QtViewer import *

class QtSegmentationViewer(QtViewer):

    def __init__(self, otherViewers):
        super(QtSegmentationViewer, self).__init__()

        # Properties
        self.otherViewers = otherViewers
        
        ## Render Viewer
        self.viewer = SegmentationViewer(self.otherViewers)

        # Initialize the UI        
        self._init_UI()
        
        # Connect signals and slots
        self.connect()

    def _init_UI(self):
        super()._init_UI()
        
        # Set up the layout
        self.mainLayout.addItem(QSpacerItem(10, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))