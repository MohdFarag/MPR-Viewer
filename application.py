import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal


import vtk.qt
vtk.qt.QVTKRWIBase = "QGLWidget"

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import time

# Step 1: Create a worker class
class Worker(QObject):    
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, slices_max):
        super().__init__()
        self.slices_max = slices_max
        self._isRunning = True

    def run(self):
        """Long-running task."""
        if not self._isRunning :
            self._isRunning = True

        for i in range(0,self.slices_max):
            if self._isRunning:
                self.progress.emit(i)
                time.sleep(0.001)

        self.finished.emit()
        
    def stop(self):
        self._isRunning = False

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiplanar Reconstruction")
        self.slice_position = [0, 0, 0]
        
        self.axialThread = QThread()
        self.coronalThread = QThread()
        self.sagittalThread = QThread()

        # Step 3: Create a worker object
        self.worker = Worker(0)
        
        self.sagittal_slices_max = 0
        self.coronal_slices_max = 0
        self.axial_slices_max = 0

        # Create UI components
        self.sagittal_viewer = QVTKRenderWindowInteractor()
        self.image_viewer_sagittal = vtk.vtkImageViewer2()
        self.sagittal_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.sagittal_slider.setSingleStep(1)
        self.sagittal_slider.setValue(1)
        self.sagittal_slider.setEnabled(False)
        
        self.coronal_viewer = QVTKRenderWindowInteractor()
        self.image_viewer_coronal = vtk.vtkImageViewer2()
        self.coronal_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.coronal_slider.setSingleStep(1)
        self.coronal_slider.setValue(1)
        self.coronal_slider.setEnabled(False)

        self.axial_viewer = QVTKRenderWindowInteractor()
        self.image_viewer_axial = vtk.vtkImageViewer2()
        self.axial_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.axial_slider.setSingleStep(1)
        self.axial_slider.setValue(1)
        self.axial_slider.setEnabled(False)

        self.segmentation_viewer = QVTKRenderWindowInteractor()

        # Buttons
        self.buttons_sagittal = QtWidgets.QHBoxLayout()
        self.play_button_sagittal = QtWidgets.QPushButton("Play")
        self.pause_button_sagittal = QtWidgets.QPushButton("Pause")
        self.buttons_sagittal.addWidget(self.play_button_sagittal)
        self.buttons_sagittal.addWidget(self.pause_button_sagittal)
        
        self.buttons_coronal = QtWidgets.QHBoxLayout()
        self.play_button_coronal = QtWidgets.QPushButton("Play")
        self.pause_button_coronal = QtWidgets.QPushButton("Pause")
        self.buttons_coronal.addWidget(self.play_button_coronal)
        self.buttons_coronal.addWidget(self.pause_button_coronal)

        self.buttons_axial = QtWidgets.QHBoxLayout()        
        self.play_button_axial = QtWidgets.QPushButton("Play")
        self.pause_button_axial = QtWidgets.QPushButton("Pause")
        self.buttons_axial.addWidget(self.play_button_axial)
        self.buttons_axial.addWidget(self.pause_button_axial)

        # Set up the layouts
        sagittal_layout = QtWidgets.QVBoxLayout()
        top_sagittal_layout = QtWidgets.QHBoxLayout()
        top_sagittal_layout.addWidget(self.sagittal_viewer)
        top_sagittal_layout.addWidget(self.sagittal_slider)
        sagittal_layout.addLayout(top_sagittal_layout)
        sagittal_layout.addLayout(self.buttons_sagittal)
        sagittal_widget = QtWidgets.QWidget()
        sagittal_widget.setLayout(sagittal_layout)

        coronal_layout = QtWidgets.QVBoxLayout()
        top_coronal_layout = QtWidgets.QHBoxLayout()
        top_coronal_layout.addWidget(self.coronal_viewer)
        top_coronal_layout.addWidget(self.coronal_slider)
        coronal_layout.addLayout(top_coronal_layout)
        coronal_layout.addLayout(self.buttons_coronal)
        coronal_widget = QtWidgets.QWidget()
        coronal_widget.setLayout(coronal_layout)

        axial_layout = QtWidgets.QVBoxLayout()
        top_axial_layout = QtWidgets.QHBoxLayout()
        top_axial_layout.addWidget(self.axial_viewer)
        top_axial_layout.addWidget(self.axial_slider)
        axial_layout.addLayout(top_axial_layout)
        axial_layout.addLayout(self.buttons_axial)
        axial_widget = QtWidgets.QWidget()
        axial_widget.setLayout(axial_layout)

        segmentation_layout = QtWidgets.QVBoxLayout()
        segmentation_layout.addWidget(self.segmentation_viewer)
        segmentation_widget = QtWidgets.QWidget()
        segmentation_widget.setLayout(segmentation_layout)
        
        # Set up the main layout
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        right_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        left_splitter.addWidget(axial_widget)
        left_splitter.addWidget(coronal_widget)

        right_splitter.addWidget(sagittal_widget)
        right_splitter.addWidget(segmentation_widget)

        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)

        # Create a central widget and set the layout
        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QVBoxLayout()
        central_layout.addWidget(main_splitter)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
                        
        # Add menu bar
        self.create_menu()

        # Connect signals and slots
        self.connect()
               
    def connect(self):
        # Connect slider signals to slice update slots
        self.sagittal_slider.valueChanged.connect(lambda value: self.update_slice(self.image_viewer_sagittal, value))
        self.coronal_slider.valueChanged.connect(lambda value: self.update_slice(self.image_viewer_coronal, value))
        self.axial_slider.valueChanged.connect(lambda value: self.update_slice(self.image_viewer_axial, value))
        
        self.play_button_sagittal.clicked.connect(lambda: self.playSlices(0))
        self.play_button_coronal.clicked.connect(lambda: self.playSlices(1))
        self.play_button_axial.clicked.connect(lambda: self.playSlices(2))
        
        self.pause_button_sagittal.clicked.connect(lambda: self.worker.stop())
        self.pause_button_coronal.clicked.connect(lambda: self.worker.stop())
        self.pause_button_axial.clicked.connect(lambda: self.worker.stop())
                
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = QtWidgets.QAction("Open Image", self)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

    def open_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Image Files (*.mhd)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                image = self.load_image(filename)
                if image is None:
                    QtWidgets.QMessageBox.critical(self, "Error", "Unable to open the image file.")
                else:
                    self.display_image(image)

    def load_image(self, filename):
        try:
            reader = vtk.vtkMetaImageReader()
            reader.SetFileName(filename)
            reader.Update()
            image = reader.GetOutput()
            return image
        
        except Exception as e:
            print(str(e))
            return None

    def display_image(self, image):
        self.sagittal_slices_max = image.GetExtent()[1]
        self.coronal_slices_max  = image.GetExtent()[3]
        self.axial_slices_max    = image.GetExtent()[5]
        
        # Set slider properties
        if image is not None:
            self.sagittal_slider.setMinimum(0)
            self.sagittal_slider.setMaximum(self.sagittal_slices_max)
            self.sagittal_slider.setEnabled(True)
            self.sagittal_slider.setValue(int(0.5*self.sagittal_slices_max))
            
            self.coronal_slider.setMinimum(0)
            self.coronal_slider.setMaximum(self.coronal_slices_max)
            self.coronal_slider.setEnabled(True)
            self.coronal_slider.setValue(int(0.5*self.coronal_slices_max))
            
            self.axial_slider.setMinimum(0)
            self.axial_slider.setMaximum(self.axial_slices_max)
            self.axial_slider.setEnabled(True)
            self.axial_slider.setValue(int(0.5*self.axial_slices_max))
            
        sagittal_viewer = self.sagittal_viewer.GetRenderWindow()
        coronal_viewer = self.coronal_viewer.GetRenderWindow()
        axial_viewer = self.axial_viewer.GetRenderWindow()

        shiftScaleFilter = vtk.vtkImageShiftScale()
        shiftScaleFilter.SetOutputScalarTypeToUnsignedChar()
        shiftScaleFilter.SetInputData(image)
        shiftScaleFilter.SetShift(-10)
        shiftScaleFilter.SetScale(1/15)
        shiftScaleFilter.Update()
        
        # Set up the image slice views
        self.image_viewer_sagittal.SetInputData(shiftScaleFilter.GetOutput())
        self.image_viewer_sagittal.SetSliceOrientationToYZ()
        self.image_viewer_sagittal.SetRenderWindow(sagittal_viewer)
        self.image_viewer_sagittal.GetRenderer().ResetCamera()
        self.image_viewer_sagittal.SetSlice(int(0.5*self.sagittal_slices_max))
        self.image_viewer_sagittal.Render()

        self.image_viewer_coronal.SetInputData(shiftScaleFilter.GetOutput())
        self.image_viewer_coronal.SetSliceOrientationToXZ()
        self.image_viewer_coronal.SetRenderWindow(coronal_viewer)
        self.image_viewer_coronal.GetRenderer().ResetCamera()
        self.image_viewer_coronal.SetSlice(int(0.5*self.coronal_slices_max))
        self.image_viewer_coronal.Render()

        self.image_viewer_axial.SetInputData(shiftScaleFilter.GetOutput())
        self.image_viewer_axial.SetSliceOrientationToXY()
        self.image_viewer_axial.SetRenderWindow(axial_viewer)
        self.image_viewer_axial.GetRenderer().ResetCamera()
        self.image_viewer_axial.SetSlice(int(0.5*self.axial_slices_max))
        self.image_viewer_axial.Render()

    def update_slice(self, viewer, slice_index):
        viewer.SetSlice(slice_index)
        viewer.Render()

    # TODO: Implement this function by threads
    def playSlices(self, viewer_index):
        if viewer_index == 0:
            slices_max = self.sagittal_slices_max
            # Step 2: Create a QThread object
            self.sagittalThread = QThread()

        elif viewer_index == 1:
            slices_max = self.coronal_slices_max
            # Step 2: Create a QThread object
            self.coronalThread = QThread()
        elif viewer_index == 2:
            slices_max = self.axial_slices_max
            # Step 2: Create a QThread object
            self.axialThread = QThread()

        # Step 3: Create a worker object
        self.worker = Worker(slices_max)
                
        # Final resets
        if viewer_index == 0:
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.sagittalThread)
            # Step 5: Connect signals and slots
            self.sagittalThread.started.connect(self.worker.run)
            self.worker.finished.connect(self.sagittalThread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.sagittalThread.finished.connect(self.sagittalThread.deleteLater)

            self.worker.progress.connect(self.playSagittalSlices)
            # Step 6: Start the thread
            self.sagittalThread.start()
            self.play_button_sagittal.setEnabled(False)
            self.sagittal_slider.setEnabled(False)
            self.sagittalThread.finished.connect(
                lambda: self.play_button_sagittal.setEnabled(True)
            )

        elif viewer_index == 1:
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.coronalThread)
            # Step 5: Connect signals and slots
            self.coronalThread.started.connect(self.worker.run)
            self.worker.finished.connect(self.coronalThread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.coronalThread.finished.connect(self.coronalThread.deleteLater)

            self.worker.progress.connect(self.playCoronalSlices)
            # Step 6: Start the thread
            self.coronalThread.start()
            self.play_button_coronal.setEnabled(False)
            self.coronal_slider.setEnabled(False)
            self.coronalThread.finished.connect(
                lambda: self.play_button_coronal.setEnabled(True)
            )
            
        elif viewer_index == 2:
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.axialThread)
            # Step 5: Connect signals and slots
            self.axialThread.started.connect(self.worker.run)
            self.worker.finished.connect(self.axialThread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.axialThread.finished.connect(self.axialThread.deleteLater)
            
            self.worker.progress.connect(self.playAxialSlices)
            # Step 6: Start the thread
            self.axialThread.start()
            self.play_button_axial.setEnabled(False)
            self.axial_slider.setEnabled(False)
            self.axialThread.finished.connect(
                lambda: self.play_button_axial.setEnabled(True)
            )
      
    def playAxialSlices(self, slice_index):
        self.axial_slider.setValue(slice_index)
        self.update_slice(self.image_viewer_axial, slice_index)            

    def playCoronalSlices(self, slice_index):
        self.coronal_slider.setValue(slice_index)
        self.update_slice(self.image_viewer_coronal, slice_index)
        
    def playSagittalSlices(self, slice_index):
        self.sagittal_slider.setValue(slice_index)
        self.update_slice(self.image_viewer_sagittal, slice_index)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
