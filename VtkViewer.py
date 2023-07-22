# ignore pylint
# pylint: disable-msg=E0611,E0602
import numpy as np
from VtkBase import VtkBase

from vtk import *
import vtk.qt
vtk.qt.QVTKRWIBase = "QGLWidget"
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

SLICE_ORIENTATION_YZ  = vtk.vtkResliceImageViewer.SLICE_ORIENTATION_YZ
SLICE_ORIENTATION_XZ  = vtk.vtkResliceImageViewer.SLICE_ORIENTATION_XZ
SLICE_ORIENTATION_XY  = vtk.vtkResliceImageViewer.SLICE_ORIENTATION_XY

class VtkViewer(QVTKRenderWindowInteractor):

    # Constructor
    def __init__(self, label:str, vtkBaseClass:VtkBase):
        super(VtkViewer, self).__init__()
        
        # Properties
        self.label = label
        self.vtkBaseClass = vtkBaseClass
        
        # Vtk Stuff
        ## Reader
        self.imageReader = self.vtkBaseClass.imageReader

        ## Image Shift Scale
        self.imageShiftScale = self.vtkBaseClass.imageShiftScale
        
        ## Image Window Level
        self.imageWindowLevel = self.vtkBaseClass.imageWindowLevel
        
        ## Image Blend
        self.imageBlend = self.vtkBaseClass.imageBlend
        
        ## Renderer
        self.renderer = vtkRenderer()
        
        ## Render Window
        self.renderWindow = self.GetRenderWindow()
        self.renderWindow.SetMultiSamples(0)
        self.renderWindow.AddRenderer(self.renderer)
                
        ## Interactor
        self.renderWindowInteractor = self.renderWindow.GetInteractor()
        
        ## Label Text Actor
        self.labelTextActor = vtkTextActor() 
        s = f"{self.label}"
        self.labelTextActor.SetInput(s)
        self.labelTextActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        self.labelTextActor.GetPositionCoordinate().SetValue(0.7, 0.87)
        self.renderer.AddActor2D(self.labelTextActor)

        # Render 
        self.render()

    # Destructor
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.renderer.FastDelete()
        self.Finalize()

    # Connect on data
    def connect_on_data(self, path:str):
        if path == "":
            return
    
    def update(self):
        self.imageReader.UpdateWholeExtent()
        self.imageShiftScale.UpdateWholeExtent()
        self.imageWindowLevel.UpdateWholeExtent()
        self.imageBlend.UpdateWholeExtent()
        self.GetRenderWindow().Modified()
        self.renderer.ResetCamera()

    # Render       
    def render(self):
        self.update()
        self.GetRenderWindow().Render()