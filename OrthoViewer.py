import numpy as np

from vtk import *
import vtk.qt
vtk.qt.QVTKRWIBase = "QGLWidget"
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

SLICE_ORIENTATION_YZ = 0
SLICE_ORIENTATION_XZ = 1
SLICE_ORIENTATION_XY = 2
SLICE_ORIENTATION_ORTHO = 3

class OrthoViewer(QVTKRenderWindowInteractor):

    def __init__(self, label, orientation, other_viewers=None):
        super(OrthoViewer, self).__init__()
        
        # Properties
        self.orientation = orientation
        self.label = label
        self.current_slice = 0
        self.min_slice, self.max_slice = 0, 0
        self.lineWidgets = []
        if self.orientation == SLICE_ORIENTATION_ORTHO:
            self.other_viewers = other_viewers
        
        
        # Vtk Stuff        
        ## Reader
        self.imageReader = vtkMetaImageReader()
        temp_path = "./resources/Dataset/out.mhd"
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
        
        ### Image Map To Colors
        self.imageMapToColors = vtkImageMapToColors()
        
        self.imageMapToColors.SetOutputFormatToRGBA()
        self.imageMapToColors.SetInputData(self.imageWindowLevel.GetOutput())

        # Grayscale LUT.        
        self.grayscaleLut = vtkLookupTable()
        self.grayscaleLut.SetNumberOfTableValues(256)
        self.grayscaleLut.SetTableRange(0, 255)
        self.grayscaleLut.SetRampToLinear()
        self.grayscaleLut.SetHueRange(0, 0)
        self.grayscaleLut.SetSaturationRange(0, 0)
        self.grayscaleLut.SetValueRange(0, 1)
        self.grayscaleLut.SetAlphaRange(1, 1)
        self.grayscaleLut.Build()
        self.imageMapToColors.SetLookupTable(self.grayscaleLut)
        self.imageMapToColors.UpdateWholeExtent()
        
        if self.orientation == SLICE_ORIENTATION_ORTHO:
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

        self.imageBlend = vtkImageBlend()
        
        if self.orientation == SLICE_ORIENTATION_ORTHO:
            self.imageBlend.AddInputData(self.segmentationLabelImage.GetOutput())
            self.imageBlend.SetOpacity(0, 1)
        else:
            self.imageBlend.AddInputData(self.imageMapToColors.GetOutput())
            self.imageBlend.SetOpacity(0, 1)        
        self.imageBlend.UpdateWholeExtent() 
        
        if self.orientation != SLICE_ORIENTATION_ORTHO:
            self.imageReslice = vtkImageReslice()
            if self.orientation == SLICE_ORIENTATION_YZ:
                self.imageReslice.SetResliceAxesDirectionCosines(1, 0, 0,      0, -1, 0,      0, 0, 1)
            elif self.orientation == SLICE_ORIENTATION_XZ:
                self.imageReslice.SetResliceAxesDirectionCosines(0, 1, 0,      0, 0,  1,      1, 0, 0)
            elif self.orientation == SLICE_ORIENTATION_XY:
                self.imageReslice.SetResliceAxesDirectionCosines(1, 0, 0,      0, 0,  -1,      0, 1, 0)

        # Image Actor
        if self.orientation != SLICE_ORIENTATION_ORTHO:
            self.imageActor = vtkImageActor()

        ## Renderer
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(7/255,8/255, 9/255)
        self.renderer.SetBackgroundAlpha(1.0)
        # self.renderer.GetActiveCamera().SetParallelProjection(1)
        
        ## Interactor Style Image
        if self.orientation != SLICE_ORIENTATION_ORTHO:
            self.interactorStyleImage = vtk.vtkInteractorStyleImage()
            self.interactorStyleImage.SetInteractor(self.GetRenderWindow().GetInteractor())

            self.interactorStyleImage.AddObserver(vtkCommand.UserEvent, self.fun1)
            # self.interactorStyleImage.AddObserver(vtkCommand.WindowLevelEvent, self.fun2)
            # self.interactorStyleImage.AddObserver(vtkCommand.StartWindowLevelEvent, self.fun3)
            self.interactorStyleImage.AddObserver(vtkCommand.SelectionChangedEvent, self.fun4)
            self.interactorStyleImage.SetInteractionModeToImageSlicing()
            
        self.labelTextActor = vtkTextActor() 
        windowSize = self.GetRenderWindow().GetSize()
        # self.labelTextActor.SetPosition(5,5)
        self.renderer.AddActor2D(self.labelTextActor)
        s = f"{self.label}"
        self.labelTextActor.SetInput(s)

        ## Render Window
        self.renderWindow = self.GetRenderWindow()
        self.renderWindow.AddObserver(vtkCommand.ModifiedEvent, self.changeSizeEvent)
        self.renderWindow.AddRenderer(self.renderer)
        
        ## Render Window Interactor
        self.renderWindowInteractor = self.GetRenderWindow().GetInteractor()
        
        if self.orientation != SLICE_ORIENTATION_ORTHO:
            self.renderWindowInteractor.SetInteractorStyle(self.interactorStyleImage)

            # Image Reslice
            self.imageReslice.SetInputData(self.imageBlend.GetOutput())
            self.imageReslice.SetOutputDimensionality(2)
            self.imageReslice.SetInterpolationModeToLinear()
            # self.imageReslice.SetInterpolationModeToNearestNeighbor()
            self.imageReslice.UpdateWholeExtent()

        if self.orientation != SLICE_ORIENTATION_ORTHO:
            self.imageActor.SetInputData(self.imageReslice.GetOutput())
            self.renderer.AddActor(self.imageActor)
        else:
            for viewer in self.other_viewers:
                imageActorOrtho = vtkImageActor()
                imageActorOrtho.SetInputData(viewer.imageReslice.GetOutput())
                imageActorOrtho.SetUserMatrix(viewer.imageReslice.GetResliceAxes())
                self.renderer.AddActor(imageActorOrtho)
        
        if self.orientation != SLICE_ORIENTATION_ORTHO:          
            self.imagePlaneWidget = vtkImagePlaneWidget()
            self.imagePlaneWidget.SetInteractor(self.GetRenderWindow().GetInteractor())
            self.imagePlaneWidget.SetInputData(self.imageReslice.GetOutput())
            self.imagePlaneWidget.SetPlaneOrientationToZAxes()  # Z axis
            self.imagePlaneWidget.SetSliceIndex(0)
            self.imagePlaneWidget.RestrictPlaneToVolumeOn()
            self.imagePlaneWidget.DisplayTextOn()
            # self.imagePlaneWidget.AddObserver(vtkCommand.WindowLevelEvent,self.xxxx)

            # Style
            # self.imagePlaneWidget.GetPlaneProperty().SetColor(1, 1, 0)
            self.imagePlaneWidget.GetPlaneProperty().SetLineWidth(2.5)   
            self.imagePlaneWidget.GetSelectedPlaneProperty().SetColor(1, 1, 1)
            self.imagePlaneWidget.GetSelectedPlaneProperty().SetLineWidth(2.5)

            self.imagePlaneWidget.On()
        
    def xxxx(self,obj, event):
        print(self.imagePlaneWidget.GetCursorData())
    
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.renderer.FastDelete()
        if self.orientation != SLICE_ORIENTATION_ORTHO:
            self.imageReslice.FastDelete()
            self.imageActor.FastDelete()
        self.imageReader.FastDelete()
        self.Finalize()      
    
        # self.renderer.AddActor(self.imageActor)
              
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
        
        # Set the slice range
        self.set_slice_range()
        self.GetRenderWindow().Render()

    def changeSizeEvent(self, obj, event):
        windowSize = self.GetRenderWindow().GetSize()
        self.labelTextActor.SetPosition(windowSize[0]-120,windowSize[1]-30)

    def set_slice_range(self):
        if self.orientation != SLICE_ORIENTATION_ORTHO:
            self.imageReader.GetOutput()
            if self.orientation == SLICE_ORIENTATION_YZ:
                self.min_slice = int(self.imageReader.GetOutput().GetBounds()[4])
                self.max_slice = int(self.imageReader.GetOutput().GetBounds()[5])
            elif self.orientation == SLICE_ORIENTATION_XZ:
                self.min_slice = int(self.imageReader.GetOutput().GetBounds()[2])
                self.max_slice = int(self.imageReader.GetOutput().GetBounds()[3])
            elif self.orientation == SLICE_ORIENTATION_XY:
                self.min_slice = int(self.imageReader.GetOutput().GetBounds()[0])
                self.max_slice = int(self.imageReader.GetOutput().GetBounds()[1])
    
            self.set_slice((self.max_slice+self.min_slice)//2)
    
    def set_slice(self, slice_index):      
        print(slice_index) 
        self.current_slice = slice_index

        if self.orientation == SLICE_ORIENTATION_YZ:
            self.imageReslice.SetResliceAxesOrigin(0, 0, slice_index)
        elif self.orientation == SLICE_ORIENTATION_XZ:
            self.imageReslice.SetResliceAxesOrigin(slice_index, 0, 0)
        elif self.orientation == SLICE_ORIENTATION_XY:
            self.imageReslice.SetResliceAxesOrigin(0, slice_index, 0)
            
        self.imageReslice.UpdateWholeExtent()
        self.GetRenderWindow().Render()

    def get_slice(self):
        return self.current_slice
    
    def get_slices_range(self):
        return self.min_slice, self.max_slice
    
    def set_orientation(self, orientation):
        self.orientation = orientation
        if self.orientation == SLICE_ORIENTATION_YZ:
            self.imageReslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, -1, 0, 0, 0, 1)
        elif self.orientation == SLICE_ORIENTATION_XZ:
            self.imageReslice.SetResliceAxesDirectionCosines(0, 1, 0, 0, 0, 1, 1, 0, 0)
        elif self.orientation == SLICE_ORIENTATION_XY:
            self.imageReslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
      
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