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

    def __init__(self, label:str, vtkBaseClass:VtkBase):
        super(VtkViewer, self).__init__()
        
        # Properties
        self.label = label
        self.vtkBaseClass = vtkBaseClass
        
        # Vtk Stuff        
        ## Reader
        self.imageReader = self.vtkBaseClass.imageReader

        ## Filters
        ### Image Shift Scale
        self.imageShiftScale = self.vtkBaseClass.imageShiftScale
        
        ### Image Window Level
        self.imageWindowLevel = self.vtkBaseClass.imageWindowLevel
        
        # Image Blend
        self.imageBlend = self.vtkBaseClass.imageBlend
        
        # Image Reslice
        self.imageReslice = vtkImageReslice()
        
        ## Renderer
        self.renderer = vtkRenderer()
                
        # Label Text Actor
        self.labelTextActor = vtkTextActor() 
        self.renderer.AddActor2D(self.labelTextActor)
        s = f"{self.label}"
        self.labelTextActor.SetInput(s)

        ## Render Window
        self.renderWindow = self.GetRenderWindow()
        self.renderWindow.AddObserver(vtkCommand.ModifiedEvent, self.changeSizeEvent)
        self.renderWindow.AddRenderer(self.renderer)
                
        self.Render()

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.renderer.FastDelete()
        self.Finalize()
    
    def connect_on_data(self, path:str):
        if path == "":
            return
             
    def Render(self):
        self.renderer.ResetCamera()
        self.GetRenderWindow().Render()

    def changeSizeEvent(self, obj, event):
        windowSize = self.GetRenderWindow().GetSize()
        self.labelTextActor.SetPosition(windowSize[0]-150,windowSize[1]-30)