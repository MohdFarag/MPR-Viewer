from vtk import *
from PyQt5.QtWidgets import *

class CommandSliceSelect(object):
    
    # Constructor
    def __init__(self) -> None:
        super().__init__()
        self.imagePlaneWidgets = [vtkImagePlaneWidget(), vtkImagePlaneWidget(), vtkImagePlaneWidget()]
        self.resliceCursorWidgets = [vtkResliceCursorWidget(), vtkResliceCursorWidget(), vtkResliceCursorWidget()]
        self.sliders = [QSlider(), QSlider(), QSlider()]
        self.resliceCursor = None
        
    def __call__(self, caller, ev) -> None:
               
        # If the reslice cursor has changed, update it on the 3D widget and the slice sliders
        if isinstance(caller,vtkResliceCursorWidget):
            rcw = caller
        else:
            rcw = None
            
        if rcw:
            rep = vtkResliceCursorLineRepresentation.SafeDownCast(rcw.GetRepresentation())
            rc = rep.GetResliceCursorActor().GetCursorAlgorithm().GetResliceCursor()
            for i in range(0,3):
                # Update the image plane widget from the reslice cursor
                polyDataAlgo = self.imagePlaneWidgets[i].GetPolyDataAlgorithm()
                polyDataAlgo.SetNormal(rc.GetPlane(i).GetNormal())
                polyDataAlgo.SetCenter(rc.GetPlane(i).GetOrigin())
                self.imagePlaneWidgets[i].UpdatePlacement() # This is necessary to update the image plane widget
                
                # Update sliders                
                self.sliders[i].setValue(int(self.resliceCursor.GetCenter()[i]))
