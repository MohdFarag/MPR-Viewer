# VTK
from vtk import *
from VtkViewer import *
from CommandSliceSelect import *

class OrthoViewer(VtkViewer):

    # Constructor
    def __init__(self, vtkBaseClass:VtkBase, orientation, label:str="Orthogonal Viewer"):
        super(OrthoViewer, self).__init__(label=label, vtkBaseClass=vtkBaseClass)

        # Properties
        self.orientation = orientation
        self.current_slice = 0
        self.min_slice = 0
        self.max_slice = 0
                       
        # Vtk Stuff
        
        ### Image Window Level        
        self.imageWindowLevel = self.vtkBaseClass.imageWindowLevel

        ### Image Map To Colors
        self.imageMapToColors = self.vtkBaseClass.imageMapToColors
        
        ### Grayscale LUT.        
        self.grayscaleLut = self.vtkBaseClass.grayscaleLut

        ## Render Window Interactor
        self.renderWindowInteractor = self.GetRenderWindow().GetInteractor()

        # Interactor Style Image and Events
        self.interactorStyleImage = vtk.vtkInteractorStyleImage()
        self.interactorStyleImage.SetInteractor(self.renderWindowInteractor)
        self.interactorStyleImage.SetInteractionModeToImageSlicing()
        self.renderWindowInteractor.SetInteractorStyle(self.interactorStyleImage)
                        
        # Picker
        self.picker = self.vtkBaseClass.picker
        
        # Property
        self.property = self.vtkBaseClass.property
                               
        ## Reslice Cursor
        self.resliceCursor = self.vtkBaseClass.resliceCursor
        
        # Reslice Cursor Widget
        self.resliceCursorWidget = vtk.vtkResliceCursorWidget()
        self.resliceCursorWidget.SetInteractor(self.renderWindowInteractor)

        # Reslice Cursor Line Representation
        self.resliceCursorRep = vtk.vtkResliceCursorLineRepresentation()
        self.resliceCursorWidget.SetRepresentation(self.resliceCursorRep)
        self.resliceCursorRep.GetResliceCursorActor().GetCursorAlgorithm().SetResliceCursor(self.resliceCursor)
        self.resliceCursorRep.GetResliceCursorActor().GetCursorAlgorithm().SetReslicePlaneNormal(self.orientation)
        self.resliceCursorRep.SetWindowLevel(self.imageWindowLevel.GetWindow(),self.imageWindowLevel.GetLevel())
        
        ## To fix problem of not showing the reslice cursor        
        for i in range(3):
            self.resliceCursorRep.GetResliceCursorActor().GetCenterlineProperty(i).SetRepresentationToWireframe()
        
        self.resliceCursorWidget.SetDefaultRenderer(self.renderer)
        self.resliceCursorWidget.EnabledOn()
        
        # Command Slice Select
        self.commandSliceSelect = self.vtkBaseClass.commandSliceSelect
        self.commandSliceSelect.resliceCursorWidgets[self.orientation] = self.resliceCursorWidget
        self.commandSliceSelect.resliceCursor = self.resliceCursor

        # Renderer Settings
        color = [0.02, 0.02, 0.02]
        color[self.orientation] = 0
        self.renderer.SetBackground(color)

        # Add observers
        self.add_observers()
                
    # Connect on data
    def connect_on_data(self, path:str):
        super().connect_on_data(path)
        self.set_slice_range()
           
    # Get slice range
    def get_slices_range(self):
        return self.min_slice, self.max_slice

    # Set slice range
    def set_slice_range(self):
        self.resliceCursor.Reset()
        self.min_slice = int(self.vtkBaseClass.bounds[self.orientation * 2 + 0])
        self.max_slice = int(self.vtkBaseClass.bounds[self.orientation * 2 + 1])   
    
    # Get slice index
    def get_slice(self):
        return self.current_slice
    
    # Set slice index
    def set_slice(self, slice_index):
        center = list(self.resliceCursor.GetCenter())
        center[self.orientation] = slice_index
        self.resliceCursor.SetCenter(center)

        self.resliceCursor.Update()
        for i in range(0,3):
            self.commandSliceSelect.imagePlaneWidgets[i].UpdatePlacement()
            self.commandSliceSelect.resliceCursorWidgets[i].Render()
        
        self.render()
                        
    # Update
    def update(self):
        super().update()
    
    # Render
    def render(self):
        super().render()

    # Events
    def add_observers(self):
        self.resliceCursorWidget.AddObserver(vtk.vtkResliceCursorWidget.ResliceAxesChangedEvent, self.commandSliceSelect)
