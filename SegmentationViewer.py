# ignore pylint
# pylint: disable-msg=E0611,E0602
import numpy as np

from vtk import *
from VtkViewer import *

# Segmentation Viewer
class SegmentationViewer(VtkViewer):

    # Constructor
    def __init__(self, vtkBaseClass:VtkBase, label:str="Segmentation Viewer"):
        super(SegmentationViewer, self).__init__(label=label, vtkBaseClass=vtkBaseClass)                           
        
        self.picker = self.vtkBaseClass.picker
        self.property = self.vtkBaseClass.property
        
        # Image Plane Widgets
        self.imagePlaneWidgets = [vtkImagePlaneWidget(), vtkImagePlaneWidget(), vtkImagePlaneWidget()]
        for imagePlaneWidget in self.imagePlaneWidgets:
            imagePlaneWidget.SetInteractor(self.renderWindowInteractor)
            imagePlaneWidget.SetInputData(self.vtkBaseClass.imageBlend.GetOutput())
            imagePlaneWidget.SetDefaultRenderer(self.renderer)
            imagePlaneWidget.SetPicker(self.picker)
            imagePlaneWidget.RestrictPlaneToVolumeOn()
            imagePlaneWidget.SetTexturePlaneProperty(self.property)
            imagePlaneWidget.TextureInterpolateOff()
            imagePlaneWidget.SetResliceInterpolateToLinear()
            imagePlaneWidget.DisplayTextOn()
            imagePlaneWidget.On()
            imagePlaneWidget.InteractionOn()
            
        ## Renderer Settings
        self.renderer.SetBackground(0.05, 0.05, 0.05)
        self.renderer.GetActiveCamera().Elevation(110)
        self.renderer.GetActiveCamera().SetViewUp(0, 0, -1)
        self.renderer.GetActiveCamera().Azimuth(45)
        self.renderer.GetActiveCamera().Dolly(1.15)
        self.renderer.ResetCameraClippingRange()

    # Connect on data
    def connect_on_data(self, path:str):
        super().connect_on_data(path)