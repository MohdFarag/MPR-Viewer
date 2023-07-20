# ignore pylint
# pylint: disable-msg=E0611,E0602
import numpy as np

from vtk import *
from VtkViewer import *
from VtkAdditions import *

class OrthoViewer(VtkViewer):

    def __init__(self, vtkBaseClass:VtkBase, orientation, label:str="Orthogonal Viewer"):
        super(OrthoViewer, self).__init__(label=label, vtkBaseClass=vtkBaseClass)

        # Properties
        self.orientation = orientation
        self.current_slice = 0
        self.min_slice, self.max_slice = 0, 0
                       
        # Vtk Stuff
        ## Set Background
        color = [0,0,0]   
        color[self.orientation] = 2/255
        self.renderer.SetBackground(color)

        ### Image Map To Colors
        self.imageMapToColors = self.vtkBaseClass.imageMapToColors

        ### Grayscale LUT.        
        self.grayscaleLut = self.vtkBaseClass.grayscaleLut

        # Set Orientation
        self.set_orientation(self.orientation)

        # Interactor Style Image and Events
        self.interactorStyleImage = vtk.vtkInteractorStyleImage()
        self.interactorStyleImage.SetInteractor(self.GetRenderWindow().GetInteractor())
        self.interactorStyleImage.SetInteractionModeToImageSlicing()
        
        ## Render Window Interactor
        self.renderWindowInteractor = self.GetRenderWindow().GetInteractor()        
        self.renderWindowInteractor.SetInteractorStyle(self.interactorStyleImage)

        # Image Reslice
        self.imageReslice.SetInputData(self.imageBlend.GetOutput())
        self.imageReslice.SetInputConnection(self.imageBlend.GetOutputPort())
        self.imageReslice.SetOutputDimensionality(2)
        self.imageReslice.SetInterpolationModeToLinear()
        self.imageReslice.UpdateWholeExtent()
                        
        self.imageActor = vtkImageActor()
        self.imageActor.SetInputData(self.imageReslice.GetOutput())
        self.renderer.AddActor(self.imageActor)
        
        # Picker
        self.picker = self.vtkBaseClass.picker

        ## Image Plane Widget
        self.imagePlaneWidget = vtkImagePlaneWidget()
        self.imagePlaneWidget.SetInteractor(self.GetRenderWindow().GetInteractor())
        self.imagePlaneWidget.SetInputData(self.imageReslice.GetOutput())
        self.imagePlaneWidget.SetPlaneOrientationToZAxes()  # Z axis
        self.imagePlaneWidget.SetSliceIndex(0)
        self.imagePlaneWidget.RestrictPlaneToVolumeOn()
        self.imagePlaneWidget.SetPicker(self.picker)
        self.imagePlaneWidget.UseContinuousCursorOn()
        self.imagePlaneWidget.DisplayTextOn()
        self.imagePlaneWidget.On()
        self.imagePlaneWidget.InteractionOff()

        resliceAxes = self.imagePlaneWidget.GetUseContinuousCursor()
        print((resliceAxes))        
        
        ### Properties                
        self.imagePlaneWidget.GetPlaneProperty().SetColor(1, 1, 0)
        self.imagePlaneWidget.GetPlaneProperty().SetLineWidth(4)
        self.imagePlaneWidget.GetSelectedPlaneProperty().SetLineWidth(4)    
        
        # Create the axis line widget
        self.axesWidget = vtkAxesWidget()
        self.axesWidget.SetInteractor(self.GetRenderWindow().GetInteractor())
        self.axesWidget.SetResolution(1000)  # Set the resolution of the line
        self.axesWidget.SetColor((0, 0, 1), (0, 1, 0))  # Set the color of the X-axis to red        

        # Add observers
        self.AddObservers()
                
    # Connect on data
    def connect_on_data(self, path:str):
        super().connect_on_data(path)
                
        # Image Reslice
        self.imageReslice.SetInputData(self.imageBlend.GetOutput())
        self.imageReslice.SetInterpolationModeToLinear()
        self.imageReslice.UpdateWholeExtent()

        self.imageActor.SetInputData(self.imageReslice.GetOutput())
        self.renderer.AddActor(self.imageActor)

        bounds = self.imageActor.GetBounds()
        self.axesWidget.SetBounds(bounds)
        self.axesWidget.SetSize((bounds[1] - bounds[0]), (bounds[3] - bounds[2]))
        self.axesWidget.SetPosition((bounds[1] + bounds[0])/2, (bounds[3] + bounds[2])/2)
        self.axesWidget.On()
        
        self.imagePlaneWidget.SetInputData(self.imageReslice.GetOutput())        
        self.imagePlaneWidget.On()
        
        self.set_slice_range()

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
                self.min_slice = int(self.imageReader.GetOutput().GetExtent()[4])
                self.max_slice = int(self.imageReader.GetOutput().GetExtent()[5])
            elif self.orientation == SLICE_ORIENTATION_XZ:
                self.min_slice = int(self.imageReader.GetOutput().GetExtent()[0])
                self.max_slice = int(self.imageReader.GetOutput().GetExtent()[1])
            elif self.orientation == SLICE_ORIENTATION_XY:
                self.min_slice = int(self.imageReader.GetOutput().GetExtent()[2])
                self.max_slice = int(self.imageReader.GetOutput().GetExtent()[3])
    
            self.set_slice_index((self.max_slice+self.min_slice)//2)

    def get_slice(self):
        return self.current_slice
    
    def set_slice_index(self, slice_index):
        self.current_slice = slice_index
        if self.orientation == SLICE_ORIENTATION_YZ:
            self.imageReslice.SetResliceAxesOrigin(0, 0, slice_index)
        elif self.orientation == SLICE_ORIENTATION_XZ:
            self.imageReslice.SetResliceAxesOrigin(slice_index, 0, 0)
        elif self.orientation == SLICE_ORIENTATION_XY:
            self.imageReslice.SetResliceAxesOrigin(0, slice_index, 0)

        self.Update()            
        self.Render()
    
    def Update(self):
        self.imageReslice.UpdateWholeExtent()
        
    def Render(self):
        super().Render()

    # Events
    def AddObservers(self):
        # self.interactorStyleImage.AddObserver(vtkCommand.UserEvent, self.fun1)
        # self.interactorStyleImage.AddObserver(vtkCommand.WindowLevelEvent, self.fun2)
        # self.interactorStyleImage.AddObserver(vtkCommand.StartWindowLevelEvent, self.fun3)
        # self.interactorStyleImage.AddObserver(vtkCommand.SelectionChangedEvent, self.fun4)
        self.axesWidget.AddObservers()


    def fun1(self, obj, event):
        print("fun1")
    
    def fun2(self, obj, event):
        print("fun2")
    
    def fun3(self, obj, event):
        print("fun3")
        
    def fun4(self, obj, event):
        print("fun4")