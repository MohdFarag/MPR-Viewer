# ignore pylint
# pylint: disable-msg=E0611,E0602
import numpy as np

from vtk import *
from VtkViewer import *
from VtkAdditions import *

class OrthoViewer(VtkViewer):

    def __init__(self, orientation):
        super(OrthoViewer, self).__init__(label="Orthogonal Viewer")

        # Properties
        self.orientation = orientation
        self.current_slice = 0
        self.min_slice, self.max_slice = 0, 0
                       
        # Vtk Stuff
        ### Image Map To Colors
        self.imageMapToColors = vtkImageMapToColors()
        self.imageMapToColors.SetOutputFormatToRGBA()
        self.imageMapToColors.SetInputData(self.imageWindowLevel.GetOutput())

        ### Grayscale LUT.        
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

        ### Image Blend
        self.imageBlend.AddInputData(self.imageMapToColors.GetOutput())
        self.imageBlend.SetOpacity(0, 1)        
        self.imageBlend.UpdateWholeExtent() 

        # Set Orientation
        self.set_orientation(self.orientation)

        # Interactor Style Image and Events
        self.interactorStyleImage = vtk.vtkInteractorStyleImage()
        self.interactorStyleImage.SetInteractor(self.GetRenderWindow().GetInteractor())
        self.interactorStyleImage.AddObserver(vtkCommand.UserEvent, self.fun1)
        # self.interactorStyleImage.AddObserver(vtkCommand.WindowLevelEvent, self.fun2)
        # self.interactorStyleImage.AddObserver(vtkCommand.StartWindowLevelEvent, self.fun3)
        self.interactorStyleImage.AddObserver(vtkCommand.SelectionChangedEvent, self.fun4)
        self.interactorStyleImage.SetInteractionModeToImageSlicing()
        
        ## Render Window Interactor
        self.renderWindowInteractor = self.GetRenderWindow().GetInteractor()        
        self.renderWindowInteractor.SetInteractorStyle(self.interactorStyleImage)

        # Image Reslice
        self.imageReslice.SetInputData(self.imageBlend.GetOutput())
        self.imageReslice.SetOutputDimensionality(2)
        self.imageReslice.SetInterpolationModeToLinear()
        self.imageReslice.UpdateWholeExtent()

        self.imageActor = vtkImageActor()
        self.imageActor.SetInputData(self.imageReslice.GetOutput())
        self.renderer.AddActor(self.imageActor)
        
        # Create the axis line widget
        self.axes_widget = vtkAxesWidget()
        self.axes_widget.SetInteractor(self.GetRenderWindow().GetInteractor())
        self.axes_widget.SetResolution(100)  # Set the resolution of the line
        self.axes_widget.AddObservers()
        self.axes_widget.SetColor((0, 1, 0), (1, 0, 0))  # Set the color of the X-axis to red    

        self.imagePlaneWidget = vtkImagePlaneWidget()
        self.imagePlaneWidget.SetInteractor(self.GetRenderWindow().GetInteractor())
        self.imagePlaneWidget.SetInputData(self.imageReslice.GetOutput())
        self.imagePlaneWidget.SetPlaneOrientationToZAxes()  # Z axis
        self.imagePlaneWidget.SetSliceIndex(0)
        self.imagePlaneWidget.RestrictPlaneToVolumeOn()
        self.imagePlaneWidget.DisplayTextOn()
        
        ### Style
        self.imagePlaneWidget.GetPlaneProperty().SetColor(1, 1, 0)
        self.imagePlaneWidget.GetPlaneProperty().SetLineWidth(4)   
        self.imagePlaneWidget.GetSelectedPlaneProperty().SetColor(1, 1, 1)
        self.imagePlaneWidget.GetSelectedPlaneProperty().SetLineWidth(4)    
        
    # Connect on data
    def connect_on_data(self, path:str):
        super().connect_on_data(path)
        self.set_slice_range()
        
        ### Image Map To Colors
        self.imageMapToColors.SetOutputFormatToRGBA()
        self.imageMapToColors.SetInputData(self.imageWindowLevel.GetOutput())
        self.imageMapToColors.UpdateWholeExtent()

        ### Image Blend
        self.imageBlend.AddInputData(self.imageMapToColors.GetOutput())
        self.imageBlend.SetOpacity(0, 1)        
        self.imageBlend.UpdateWholeExtent()

        # Image Reslice
        self.imageReslice.SetInputData(self.imageBlend.GetOutput())
        self.imageReslice.SetInterpolationModeToLinear()
        self.imageReslice.UpdateWholeExtent()

        self.imageActor.SetInputData(self.imageReslice.GetOutput())
        self.renderer.AddActor(self.imageActor)

        bounds = self.imageActor.GetBounds()
        print(bounds)
        self.axes_widget.SetBounds(bounds)
        self.axes_widget.SetSize((bounds[1] - bounds[0]), (bounds[3] - bounds[2]))
        self.axes_widget.SetPosition((bounds[1] + bounds[0])/2, (bounds[3] + bounds[2])/2)
        self.axes_widget.On()
        
        self.imagePlaneWidget.SetInputData(self.imageReslice.GetOutput())        
        self.imagePlaneWidget.On()

    def set_orientation(self, orientation):
        self.orientation = orientation
        if self.orientation == SLICE_ORIENTATION_YZ:
            self.imageReslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 1, 0, 0, 0, 1)
        elif self.orientation == SLICE_ORIENTATION_XZ:
            self.imageReslice.SetResliceAxesDirectionCosines(0, 1, 0, 0, 0, 1, 1, 0, 0)
        elif self.orientation == SLICE_ORIENTATION_XY:
            self.imageReslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
    
    def get_slices_range(self):
        return self.min_slice, self.max_slice

    def set_slice_range(self):
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

    def get_slice(self):
        return self.current_slice
    
    def set_slice(self, slice_index):      
        self.current_slice = slice_index

        if self.orientation == SLICE_ORIENTATION_YZ:
            self.imageReslice.SetResliceAxesOrigin(0, 0, slice_index)
        elif self.orientation == SLICE_ORIENTATION_XZ:
            self.imageReslice.SetResliceAxesOrigin(slice_index, 0, 0)
        elif self.orientation == SLICE_ORIENTATION_XY:
            self.imageReslice.SetResliceAxesOrigin(0, slice_index, 0)
            
        self.imageReslice.UpdateWholeExtent()
        self.GetRenderWindow().Render()
