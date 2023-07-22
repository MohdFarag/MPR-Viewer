

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

    # Play the worker thread
    def play(self):
        if not self._isRunning :
            self._isRunning = True

        i = self.slider.value()
        slider_max = self.slider.maximum()
        while i <= slider_max:
            if self._isRunning:
                self.progress.emit(i)
                time.sleep(0.01)
            else:
                break
            
            i += 1

        self.slider.setValue(i) # Set the slider to the last value
        self.finished.emit()
    
    # Pause the worker thread        
    def pause(self):
        self._isRunning = False
