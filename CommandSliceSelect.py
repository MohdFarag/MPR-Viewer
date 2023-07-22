from typing import Any
from vtk import *
from vtkmodules.vtkCommonCore import vtkObject
from VtkAdditions import *
from PyQt5.QtWidgets import *

class CommandSliceSelect(object):
    
    def __init__(self) -> None:
        super().__init__()
        self.imagePlaneWidgets = [vtkImagePlaneWidget(), vtkImagePlaneWidget(), vtkImagePlaneWidget()]
        self.resliceCursorWidgets = [vtkResliceCursorWidget(), vtkResliceCursorWidget(), vtkResliceCursorWidget()]
        self.sliders = [QSlider(), QSlider(), QSlider()]
        self.resliceCursor = None
        
    def __call__(self, caller, ev) -> Any:
        
        if isinstance(caller,vtk.vtkResliceCursor):
            rc = caller
        else:
            rc = None

        if rc:
            for i in range(0,3):
                self.imagePlaneWidgets[i].UpdatePlacement()
                self.resliceCursorWidgets[i].Render()
                # pass
                        
        if isinstance(caller,vtk.vtkResliceCursorWidget):
            rcw = caller
        else:
            rcw = None
            
        if rcw :
            # rep = vtk.vtkResliceCursorLineRepresentation.SafeDownCast(rcw.GetRepresentation())
            # rc = rep.GetResliceCursorActor().GetCursorAlgorithm().GetResliceCursor()
            for i in range(0,3):
                # polyDayaAlgo = self.imagePlaneWidgets[i].GetPolyDataAlgorithm()
                # polyDayaAlgo.SetNormal(rc.GetPlane(i).GetNormal())
                # polyDayaAlgo.SetCenter(rc.GetPlane(i).GetOrigin())
                self.sliders[i].setValue(int(self.resliceCursor.GetCenter()[i]))
                # self.imagePlaneWidgets[i].UpdatePlacement()
                self.resliceCursorWidgets[i].Render()
