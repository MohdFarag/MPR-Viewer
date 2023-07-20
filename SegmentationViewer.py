# ignore pylint
# pylint: disable-msg=E0611,E0602
import numpy as np

from vtk import *
from VtkViewer import *

class SegmentationViewer(VtkViewer):

    # Constructor
    def __init__(self, vtkBaseClass:VtkBase, other_viewers=None, label:str="Segmentation Viewer"):
        super(SegmentationViewer, self).__init__(label=label, vtkBaseClass=vtkBaseClass)
        
        # Properties
        self.other_viewers = other_viewers
                       
        # Vtk Stuff
        ## Segmentation
        for viewer in self.other_viewers:
            imageActorOrtho = vtkImageActor()
            imageActorOrtho.SetInputData(viewer.imageReslice.GetOutput())
            imageActorOrtho.SetUserMatrix(viewer.imageReslice.GetResliceAxes())
            self.renderer.AddActor(imageActorOrtho)
            
    # Connect on data
    def connect_on_data(self, path:str):
        super().connect_on_data(path)
        
        for viewer in self.other_viewers:
            imageActorOrtho = vtkImageActor()
            imageActorOrtho.SetInputData(viewer.imageReslice.GetOutput())
            imageActorOrtho.SetUserMatrix(viewer.imageReslice.GetResliceAxes())
            self.renderer.AddActor(imageActorOrtho)
