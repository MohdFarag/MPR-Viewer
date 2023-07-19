# ignore pylint
# pylint: disable-msg=E0611,E0602
import numpy as np

from vtk import *
import vtk.qt
vtk.qt.QVTKRWIBase = "QGLWidget"
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

SLICE_ORIENTATION_YZ  = 0
SLICE_ORIENTATION_XZ  = 1
SLICE_ORIENTATION_XY  = 2

class VtkViewer(QVTKRenderWindowInteractor):

    def __init__(self, label):
        super(VtkViewer, self).__init__()
        
        # Properties
        self.label = label
        
        # Vtk Stuff        
        ## Reader
        self.imageReader = vtkMetaImageReader()
        temp_path = "./temp/out.mhd"
        self.imageReader.SetFileName(temp_path) 
        self.imageReader.UpdateWholeExtent()
        slicesRange = self.imageReader.GetOutput().GetScalarRange()

        ## Filters
        ### Image Shift Scale
        self.imageShiftScale = vtkImageShiftScale()
        self.imageShiftScale.SetInputData(self.imageReader.GetOutput())
        self.imageShiftScale.SetOutputScalarTypeToUnsignedChar()
        self.imageShiftScale.SetShift(-float(slicesRange[0]))
        if slicesRange[1] - slicesRange[0] != 0:
            self.imageShiftScale.SetScale(255.0/(float(slicesRange[1]-slicesRange[0])))
        else:
            self.imageShiftScale.SetScale(0)
        self.imageShiftScale.UpdateWholeExtent()
        
        ### Image Window Level
        self.imageWindowLevel = vtkImageMapToWindowLevelColors()
        self.imageWindowLevel.SetInputConnection(self.imageShiftScale.GetOutputPort())
        self.imageWindowLevel.SetWindow(100.0)
        self.imageWindowLevel.SetLevel(50.0)
        self.imageWindowLevel.UpdateWholeExtent()

        # Image Blend
        self.imageBlend = vtkImageBlend()
        
        # Image Reslice
        self.imageReslice = vtkImageReslice()
        
        ## Renderer
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(7/255,7/255, 7/255)
        # self.renderer.GetActiveCamera().SetParallelProjection(1)
        
        self.labelTextActor = vtkTextActor() 
        self.renderer.AddActor2D(self.labelTextActor)
        s = f"{self.label}"
        self.labelTextActor.SetInput(s)

        ## Render Window
        self.renderWindow = self.GetRenderWindow()
        self.renderWindow.AddObserver(vtkCommand.ModifiedEvent, self.changeSizeEvent)
        self.renderWindow.AddRenderer(self.renderer)
        
        self.GetRenderWindow().Render()

    def xxxx(self,obj, event):
        print(self.imagePlaneWidget.GetCursorData())
    
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.renderer.FastDelete()
        self.imageReslice.FastDelete()
        self.imageReader.FastDelete()
        self.Finalize()
                  
    def connect_on_data(self, path:str):
        if path == "":
            return

        self.imageReader.SetFileName(path)
        self.imageReader.UpdateWholeExtent()
        slicesRange = self.imageReader.GetOutput().GetScalarRange()
        
        ## Image Shift Scale
        self.imageShiftScale.SetShift(-float(slicesRange[0]))
        self.imageShiftScale.SetScale(255.0/(float(slicesRange[1]-slicesRange[0])))
        self.imageShiftScale.UpdateWholeExtent()

        ### Image Window Level
        self.imageWindowLevel.SetWindow(100.0)
        self.imageWindowLevel.SetLevel(50.0)
        self.imageWindowLevel.UpdateWholeExtent()

        
    def render(self):
        self.renderer.ResetCamera()
        self.GetRenderWindow().Render()

    def changeSizeEvent(self, obj, event):
        windowSize = self.GetRenderWindow().GetSize()
        self.labelTextActor.SetPosition(windowSize[0]-150,windowSize[1]-30)
              
    def move_axis(self, obj, event):
        print("move_axis")
            
    # Events
    def fun1(self, obj, event):
        print("fun1")
    
    def fun2(self, obj, event):
        print("fun2")
    
    def fun3(self, obj, event):
        print("fun3")
        
    def fun4(self, obj, event):
        print("fun4")