from vtk import *
from OrthoViewer import *
from SegmentationViewer import *
from CommandSliceSelect import CommandSliceSelect

class ViewersConnection():
    
    # Constructor
    def __init__(self, vtkBaseClass:VtkBase) -> None:
        # Properties
        self.commandSliceSelect = CommandSliceSelect()
        self.orthogonal_viewers = []
        self.segmentation_viewer = None
        self.vtkBaseClass = vtkBaseClass
        
    # Connect on data
    def connect_on_data(self):        
        # Set Default Renderer
        for i,ortho_viewer in zip(range(3), self.orthogonal_viewers):
            ## Image Plane Widget
            self.segmentation_viewer.imagePlaneWidgets[i].SetInputData(self.vtkBaseClass.imageBlend.GetOutput())
            
            color = [0, 0, 0]
            color[ortho_viewer.orientation] = 1
            self.segmentation_viewer.imagePlaneWidgets[i].GetPlaneProperty().SetColor(color)


            self.segmentation_viewer.imagePlaneWidgets[i].SetPlaneOrientation(ortho_viewer.orientation)
            self.segmentation_viewer.imagePlaneWidgets[i].SetSliceIndex(self.vtkBaseClass.imageDimensions[ortho_viewer.orientation] // 2)
            
            self.commandSliceSelect = self.vtkBaseClass.commandSliceSelect
            self.commandSliceSelect.imagePlaneWidgets[ortho_viewer.orientation] = self.segmentation_viewer.imagePlaneWidgets[i]

            self.segmentation_viewer.imagePlaneWidgets[i].SetWindowLevel(self.vtkBaseClass.imageWindowLevel.GetWindow(),self.vtkBaseClass.imageWindowLevel.GetLevel())
            self.segmentation_viewer.imagePlaneWidgets[i].GetColorMap().SetLookupTable(self.orthogonal_viewers[0].grayscaleLut)


        self.orthogonal_viewers[1].resliceCursorRep.SetLookupTable(self.orthogonal_viewers[0].grayscaleLut)
        self.orthogonal_viewers[2].resliceCursorRep.SetLookupTable(self.orthogonal_viewers[0].grayscaleLut)

        for ortho_viewer in self.orthogonal_viewers:
            ortho_viewer.resliceCursorRep.SetLookupTable(self.orthogonal_viewers[0].grayscaleLut)

    # Add segmentation viewer
    def add_segmentation_viewer(self, segmentation_viewer):
        self.segmentation_viewer = segmentation_viewer
    
    # Add orthogonal viewer
    def add_orthogonal_viewer(self, orthogonal_viewer):
        self.orthogonal_viewers.append(orthogonal_viewer)
    
