# ignore pylint
# pylint: disable-msg=E0611,E0602

from vtk import *
import vtk.qt
vtk.qt.QVTKRWIBase = "QGLWidget"
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

SLICE_ORIENTATION_YZ = 0
SLICE_ORIENTATION_XZ = 1
SLICE_ORIENTATION_XY = 2
SLICE_ORIENTATION_ORTHO = 3

class OrthoViewer(QVTKRenderWindowInteractor):

    def __init__(self, orientation):
        super(OrthoViewer, self).__init__()
 
         # Properties
        self.orientation = orientation
        self.current_slice = 0
        self.max_slice = 0
        self.min_slice = 0
   
        # Vtk Stuff        
        ## Reader
        self.reader = vtkMetaImageReader() 
        
        ## Filters
        self.imageShiftScale = vtkImageShiftScale()
        self.imageWindowLevel = vtkImageMapToWindowLevelColors()
        self.imageMapToColors = vtkImageMapToColors()
        self.grayscaleLut = vtkLookupTable()
        self.segmentationImage = vtkImageData()
        self.segmentationLabelImage = vtkImageMapToColors()
        self.segmentationLabelLookupTable = vtkLookupTable()
        self.imageBlender = vtkImageBlend()
        self.vtkImageReslice = vtkImageReslice()
        self.vtkImageActor = vtkImageActor()
        self.vtkTextActor = vtkTextActor()        
        self.vtkTextActor.SetPosition(5, 5)
        L, W, x, y, z = 50.0, 100.0, 0.0, 0.0, 0.0
        text = f"L/W: {L}/{W} | (x,y,z): ({x}, {y}, {z})"
        self.vtkTextActor.SetInput(text)
        
        ## Renderer
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(0, 0, 0)
        self.renderer.AddActor2D(self.vtkTextActor)
        
        ## Render Window
        self.renderWindow = self.GetRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
        self.renderWindow.SetWindowName("OrthoViewer")

        ## Render Window Interactor
        self.renderWindowInteractor = self.GetRenderWindow().GetInteractor()
        self.renderWindowInteractor.SetRenderWindow(self.renderWindow)

        ## Interactor Style Image
        self.interactorStyleImage = vtk.vtkInteractorStyleImage()
        self.renderWindowInteractor.SetInteractorStyle(self.interactorStyleImage)

        self.set_orientation_index(self.orientation) 
        self.initialize()
                 
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.Finalize()
    
    def initialize(self):
        self.reader.SetFileName("./temp/out.mhd")
        self.reader.UpdateWholeExtent()
        slicesRange = self.reader.GetOutput().GetScalarRange()

        # Filter the data
        ## Shift and scale the data
        self.imageShiftScale.SetInputData(self.reader.GetOutput())
        self.imageShiftScale.SetOutputScalarTypeToUnsignedChar()
        self.imageShiftScale.SetShift(-slicesRange[0])
        self.imageShiftScale.SetScale(255.0/(slicesRange[1]-slicesRange[0]))
        self.imageShiftScale.UpdateWholeExtent()

        ## Set the window and level
        self.imageWindowLevel.SetInputConnection(self.imageShiftScale.GetOutputPort())
        self.imageWindowLevel.SetWindow(100.0)
        self.imageWindowLevel.SetLevel(50.0)
        self.imageWindowLevel.UpdateWholeExtent()

        ## Map the image through the lookup table
        self.imageMapToColors.SetOutputFormatToRGBA()
        self.imageMapToColors.SetInputData(self.imageWindowLevel.GetOutput())

        ## Create a greyscale lookup table
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
            self.segmentationImage.DeepCopy(self.imageShiftScale.GetOutput())            
                   
            self.segmentationLabelImage.SetInputData(self.segmentationImage)
            self.segmentationLabelImage.SetOutputFormatToRGBA()
        
            self.segmentationLabelLookupTable.SetNumberOfTableValues(256)
            self.segmentationLabelLookupTable.SetTableRange(0, 255)
            self.segmentationLabelLookupTable.SetTableValue(0, 0, 1, 0, 0.0)
            self.segmentationLabelLookupTable.SetTableValue(1, 1.0, 0, 0, 0.5)
            
            self.segmentationLabelImage.SetLookupTable(self.segmentationLabelLookupTable)
            self.segmentationLabelImage.UpdateWholeExtent()
            
            self.imageBlender.AddInputData(self.segmentationLabelImage.GetOutput())
            self.imageBlender.SetOpacity(0, 1)
        else:
            self.imageBlender.AddInputData(self.imageMapToColors.GetOutput())
            self.imageBlender.SetOpacity(0, 1)
        self.imageBlender.UpdateWholeExtent() 
        
        # self.renderer.GetActiveCamera().SetParallelProjection(1) 
        self.interactorStyleImage.SetInteractor(self.renderWindowInteractor)
        self.interactorStyleImage.AddObserver(vtkCommand.UserEvent, self.fun1)
        # self.interactorStyleImage.AddObserver(vtkCommand.WindowLevelEvent, self.fun2)
        # self.interactorStyleImage.AddObserver(vtkCommand.StartWindowLevelEvent, self.fun3)
        self.interactorStyleImage.AddObserver(vtkCommand.SelectionChangedEvent, self.fun4)
        
        self.vtkImageReslice.SetInputData(self.imageBlender.GetOutput())
        self.vtkImageReslice.SetOutputDimensionality(2)
        self.vtkImageReslice.SetInterpolationModeToLinear()
        self.vtkImageReslice.UpdateWholeExtent()
        
        if self.orientation == SLICE_ORIENTATION_ORTHO:
            self.vtkImageActor.SetInputData(self.vtkImageReslice.GetOutput())
            self.vtkImageActor.SetUserMatrix(self.vtkImageReslice.GetResliceAxes())
            self.renderer.AddActor(self.vtkImageActor)
        else:
            self.vtkImageActor.SetInputData(self.vtkImageReslice.GetOutput())
            self.renderer.AddActor(self.vtkImageActor)
        
    def connect_on_data(self, path:str):
        # Set file name
        self.reader.SetFileName(path)
        self.reader.UpdateWholeExtent()
        slicesRange = self.reader.GetOutput().GetScalarRange()

        # Filter the data
        ## Shift and scale the data
        self.imageShiftScale.SetShift(-slicesRange[0])
        self.imageShiftScale.SetScale(255.0/(slicesRange[1]-slicesRange[0]))
        self.imageShiftScale.UpdateWholeExtent()

        ## Set the window and level
        self.imageWindowLevel.SetWindow(100.0)
        self.imageWindowLevel.SetLevel(50.0)
        self.imageWindowLevel.UpdateWholeExtent()

        # Set the slice range
        self.min_slice = 0
        self.max_slice = 255

    def set_slice(self, slice_index):
        self.current_slice = slice_index

    def fun1(self, obj, event):
        print("fun1")
    
    def fun2(self, obj, event):
        print("fun2")
    
    def fun3(self, obj, event):
        print("fun3")
    
    def fun4(self, obj, event):
        print("fun4")
    
        
    def get_slice(self):
        return self.current_slice
    
    def get_slices_range(self):
        return self.min_slice, self.max_slice
    
    def set_orientation_index(self, orientation):
        self.orientation = orientation
        if self.orientation == SLICE_ORIENTATION_YZ:
            self.vtkImageReslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, -1, 0, 0, 0, 1)
        elif self.orientation == SLICE_ORIENTATION_XZ:
            self.vtkImageReslice.SetResliceAxesDirectionCosines(0, 1, 0, 0, 0, 1, 1, 0, 0)
        elif self.orientation == SLICE_ORIENTATION_XY:
            self.vtkImageReslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
        else:
            return

    def setContrast(self, value):
        pass

    def set_brightness(self, value):
        pass

    def display(self):
        self.renderWindow.Render()
        