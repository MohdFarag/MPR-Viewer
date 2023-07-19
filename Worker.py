

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
