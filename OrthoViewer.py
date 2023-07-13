
from vtk import *
from PyQt5.QtWidgets import *


class OrthoViewer(QWidget):

    # Vtk Stuff
    vecRenderer = vtkRenderer()
    imageReader =vtkMetaImageReader()
    imageShiftScale =  vtkImageShiftScale()
    imageWindowLevel = vtkImageMapToWindowLevelColors()
    imageMapToColors = vtkImageMapToColors()
    grayscaleLut = vtkLookupTable()
    segmentationImage = vtkImageData()
    segmentationLabelImage = vtkImageMapToColors()
    segmentationLabelLookupTable = vtkLookupTable()
    imageBlender = vtkImageBlend()
    vecReslice = vtkImageReslice()
    vecImageActor = vtkImageActor()
    vecImageActorOrtho = vtkImageActor()
    vecInteractorStyle = vtkInteractorStyleMy2D()
    vecTextActor = vtkTextActor
    commandSliceSelect = CommandSliceSelect()
    commandSegment = CommandSegment()

    def __init__(self, parent=0):
        super().__init__()
        self.imageReader = vtkMetaImageReader()
                

    def connect_on_data(self, orientation):
        self.imageReader.
    
    def set_slice(self, slice_index):
        self.current_slice = slice_index
        self.data_viewer.SetSliceOrientation(self.current_slice)
        
    def setContrast(self, value):
        pass
    
    def set_brightness(self, value):
        pass