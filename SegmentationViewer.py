# ignore pylint
# pylint: disable-msg=E0611,E0602
import numpy as np

from vtk import *
import vtk.qt
vtk.qt.QVTKRWIBase = "QGLWidget"
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from OrthoViewerV2 import OrthoViewer

class SegmentationViewer(OrthoViewer):

    def __init__(self, label, orientation, other_viewers=None):
        super(OrthoViewer, self).__init__()
        
        # Properties
        self.other_viewers = other_viewers
        
        # Vtk Stuff           
        
        ## Segmentation     
        self.segmentationImage = vtkImageData()
        self.segmentationImage.DeepCopy(self.imageShiftScale.GetOutput())            
        self.segmentationImage.Modified()
        
        self.segmentationLabelImage = vtkImageMapToColors()
        self.segmentationLabelImage.SetInputData(self.segmentationImage)
        self.segmentationLabelImage.SetOutputFormatToRGBA()

        self.segmentationLabelLookupTable = vtkLookupTable()                    
        self.segmentationLabelLookupTable.SetNumberOfTableValues(256)
        self.segmentationLabelLookupTable.SetTableRange(0, 255)
        self.segmentationLabelLookupTable.SetTableValue(0, 0, 1, 0, 0.0)
        self.segmentationLabelLookupTable.SetTableValue(1, 1.0, 0, 0, 0.5)

        self.segmentationLabelImage.SetLookupTable(self.segmentationLabelLookupTable)
        self.segmentationLabelImage.UpdateWholeExtent()
        
        # Image Blend
        self.imageBlend.AddInputData(self.segmentationLabelImage.GetOutput())
        self.imageBlend.SetOpacity(0, 1)
        self.imageBlend.UpdateWholeExtent() 

        for viewer in self.other_viewers:
            imageActorOrtho = vtkImageActor()
            imageActorOrtho.SetInputData(viewer.imageReslice.GetOutput())
            imageActorOrtho.SetUserMatrix(viewer.imageReslice.GetResliceAxes())
            self.renderer.AddActor(imageActorOrtho)