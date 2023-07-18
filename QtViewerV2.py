
from OrthoViewerV2 import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time

class Worker(QObject):    
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, slider:QSlider):
        super().__init__()
        self.slider = slider
        self._isRunning = True

    def run(self):
        """Long-running task."""
        if not self._isRunning :
            self._isRunning = True

        i = self.slider.value()
        slider_max = self.slider.maximum()
        while i <= slider_max:
            if self._isRunning:
                self.progress.emit(i)
                time.sleep(0.0001)
            else:
                break
            
            i += 1

        self.slider.setValue(i)
        self.finished.emit()
        
    def pause(self):
        self._isRunning = False

class QtViewer(QWidget):

    def __init__(self, label, orientation):
        super(QtViewer, self).__init__()

        # Properties
        self.label = label
        self.orientation = orientation
        self.status = False
   
        # UI
        self._init_UI()
        
        # Thread
        self.thread = QThread()
        self.worker = Worker(self.slider)
        # Connect    
        self.connect()

    def _init_UI(self):
        # PyQt Stuff
        ## Render Viewer
        self.orthoViewer = OrthoViewer(self.label, self.orientation)


        ## Slider
        self.slider = QSlider(Qt.Vertical)
        self.slider.setSingleStep(1)
        self.slider.setValue(0)
        self.slider.setEnabled(False)
        
        ## Buttons
        self.buttonsLayout = QHBoxLayout()
        
        self.prevBtn = QPushButton()
        self.prevBtn.setIcon(QIcon("./assets/decrease.svg"))
        self.prevBtn.setStyleSheet("font-size:15px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px; background: black")
        self.prevBtn.setDisabled(True)
        
        self.playBtn = QPushButton()
        self.playBtn.setIcon(QIcon("./assets/play.ico"))
        self.playBtn.setStyleSheet("font-size:15px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        self.playBtn.setDisabled(True)
        
        self.nextBtn = QPushButton()
        self.nextBtn.setIcon(QIcon("./assets/increase.svg"))
        self.nextBtn.setStyleSheet("font-size:15px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px; background: black")
        self.nextBtn.setDisabled(True)
        
        self.buttonsLayout.addSpacerItem(QSpacerItem(80, 10))
        self.buttonsLayout.addWidget(self.prevBtn,4)
        self.buttonsLayout.addWidget(self.playBtn,5)
        self.buttonsLayout.addWidget(self.nextBtn,4)
        self.buttonsLayout.addSpacerItem(QSpacerItem(80, 10))
        
        # Set up the layouts
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        topLayout.addWidget(self.orthoViewer)
        topLayout.addWidget(self.slider)
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(self.buttonsLayout)
        self.setLayout(mainLayout)
        
        self.connect_on_data("./Resources/Dataset/out.mhd")

    def connect(self):
        # Connect slider signals to slice update slots
        self.slider.valueChanged.connect(self.update_slice)
        
        # Connect buttons to slots
        self.playBtn.clicked.connect(self.playPauseBtn)

    def update_slice(self, slice_index):
        self.orthoViewer.set_slice(slice_index)
        
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.orthoViewer.Finalize()
        
    def getOrthoViewer(self):
        return self.orthoViewer
    
    def connect_on_data(self, path):
        self.orthoViewer.connect_on_data(path)

        # Settings of the button
        self.prevBtn.setEnabled(True)
        self.playBtn.setEnabled(True)
        self.nextBtn.setEnabled(True)
    
        # Settings of the slider
        self.slider.setEnabled(True)
        self.slider.setMinimum(self.orthoViewer.min_slice)
        self.slider.setMaximum(self.orthoViewer.max_slice)
        self.slider.setValue((self.slider.maximum() + self.slider.minimum())//2)    
        
    def playSlices(self):
        self.thread = QThread()
        self.worker = Worker(self.slider)
        self.status = True
        
        # Play Button icon
        self.playBtn.setIcon(QIcon("./assets/pause.ico"))
                
        # Final resets
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_slice)
        
        # Start the thread
        self.thread.start()
        self.slider.setHidden(True)
        self.thread.finished.connect(
            lambda: self.slider.setHidden(False)
        )
        self.thread.finished.connect(
            self.pauseSlices
        )

    def pauseSlices(self):
        self.playBtn.setIcon(QIcon("./assets/play.ico"))
        self.worker.pause()
        self.status = False
        
    def playPauseBtn(self):
        if self.status == False:
            self.playSlices()
        else:
            self.pauseSlices()