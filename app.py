import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from QtViewer import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPR Viewer")
        
        # Create a central widget and set the layout
        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QHBoxLayout()
        
        self.QtAxialOrthoViewer = QtViewer(f"Axial Viewer - XY", orientation=SLICE_ORIENTATION_XY)    
        self.QtCoronalOrthoViewer = QtViewer(f"Coronal Viewer - XZ", orientation=SLICE_ORIENTATION_XZ)    
        self.QtSagittalOrthoViewer = QtViewer(f"Sagittal Viewer - YZ", orientation=SLICE_ORIENTATION_YZ)    
        self.QtSegmentationOrthoViewer = QtViewer(f"Other Viewer")    
            
        # Set up the main layout
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        right_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        left_splitter.addWidget(self.QtAxialOrthoViewer)
        left_splitter.addWidget(self.QtCoronalOrthoViewer)

        right_splitter.addWidget(self.QtSagittalOrthoViewer)
        right_splitter.addWidget(self.QtSegmentationOrthoViewer)

        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)

        # Set the central widget
        central_layout.addWidget(main_splitter)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
                        
        # Add menu bar
        self.create_menu()

        # Connect signals and slots
        self.connect()
               
    def connect(self):
        pass
                    
    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        open_action = QtWidgets.QAction("Open Image", self)
        open_action.setShortcut("Ctrl+o")

        open_action.triggered.connect(self.open_data)

        file_menu.addAction(open_action)

    def open_data(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Image Files (*.mhd)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                try:
                    self.load_data(filename)
                    self.display_data()
                except Exception as e:
                    print(e)
                    QtWidgets.QMessageBox.critical(self, "Error", "Unable to open the image file.")                    


    def load_data(self, filename):
        # Load the image
        self.QtAxialOrthoViewer.connect_on_data(filename)
        self.QtCoronalOrthoViewer.connect_on_data(filename)
        self.QtSagittalOrthoViewer.connect_on_data(filename)
        self.QtSegmentationOrthoViewer.connect_on_data(filename)

    def display_data(self):
        # Set up the image slice views
        self.QtAxialOrthoViewer.display_data()
        self.QtCoronalOrthoViewer.display_data()
        self.QtSagittalOrthoViewer.display_data()
        self.QtSegmentationOrthoViewer.display_data()

    # Close the application
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.QtAxialOrthoViewer.close()
        self.QtCoronalOrthoViewer.close()
        self.QtSagittalOrthoViewer.close()
        self.QtSegmentationOrthoViewer.close()
        
    def exit(self):
        self.close()
