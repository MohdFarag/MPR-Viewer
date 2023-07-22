
from vtk import *
from CommandSliceSelect import *

class VtkBase():
    
    # Constructor
    def __init__(self) -> None:
        
        ## Reader
        self.imageReader = vtkMetaImageReader()
        temp_path = "./temp/out.mhd"
        self.imageReader.SetFileName(temp_path) 
        self.imageReader.UpdateWholeExtent()
        
        ## Update the data information
        self.update_data_information()
        
        ## Filters 
        ### Image Shift Scale
        self.imageShiftScale = vtkImageShiftScale()
        self.imageShiftScale.SetInputData(self.imageReader.GetOutput())
        self.imageShiftScale.SetOutputScalarTypeToUnsignedChar()
        self.imageShiftScale.SetShift(-float(self.scalerRange[0]))
        self.imageShiftScale.UpdateWholeExtent()
        
        ### Image Window Level *
        self.imageWindowLevel = vtkImageMapToWindowLevelColors()
        self.imageWindowLevel.SetInputConnection(self.imageShiftScale.GetOutputPort())
        self.imageWindowLevel.UpdateWholeExtent()
        
        ### Image Map To Colors **
        self.imageMapToColors = vtkImageMapToColors()
        self.imageMapToColors.SetOutputFormatToRGBA()
        self.imageMapToColors.SetInputData(self.imageWindowLevel.GetOutput())

        ### Grayscale LUT. **
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
        
        ## Image Blend
        self.imageBlend = vtkImageBlend()
        self.imageBlend.AddInputData(self.imageMapToColors.GetOutput())
        self.imageBlend.UpdateWholeExtent()
        
        ## Picker        
        self.picker = vtkCellPicker()
        self.picker.SetTolerance(0.05)
        
        ## Property
        self.property = vtk.vtkProperty()

        ## Image Reslice
        self.resliceCursor = vtk.vtkResliceCursor()
        self.resliceCursor.SetThickMode(0)
        self.resliceCursor.SetImage(self.imageBlend.GetOutput())
        self.resliceCursor.SetCenter(self.imageBlend.GetOutput().GetCenter())
       
        ## Command Slice Select
        self.commandSliceSelect = CommandSliceSelect()

    # Connect to data
    def connect_on_data(self, path:str):
        if path == "":
            return
        
        ## Reader
        self.imageReader.SetFileName(path)
        self.imageReader.UpdateWholeExtent()
        
        # Update the data information
        self.update_data_information()
        
        ## Image Shift Scale
        self.imageShiftScale.SetInputData(self.imageReader.GetOutput())
        self.imageShiftScale.SetShift(-float(self.scalerRange[0]))
        if self.scalerRange[1] != self.scalerRange[0]:
            self.imageShiftScale.SetScale(255.0/(float(self.scalerRange[1] - self.scalerRange[0])))
        self.imageShiftScale.UpdateWholeExtent()

        ### Image Window Level
        self.imageWindowLevel.SetInputConnection(self.imageShiftScale.GetOutputPort())
        self.imageWindowLevel.SetWindow(100.0)
        self.imageWindowLevel.SetLevel(50.0)
        self.imageWindowLevel.UpdateWholeExtent()

        ### Image Map To Colors
        self.imageMapToColors.SetOutputFormatToRGBA()
        self.imageMapToColors.SetInputData(self.imageWindowLevel.GetOutput())
        self.imageMapToColors.UpdateWholeExtent()
        
        ### Image Blend
        self.imageBlend.RemoveAllInputs()
        self.imageBlend.AddInputData(self.imageMapToColors.GetOutput())
        self.imageBlend.SetOpacity(0, 1.0)
        self.imageBlend.UpdateWholeExtent()
        
        ### Reslice Cursor        
        self.resliceCursor.SetImage(self.imageBlend.GetOutput())
        self.resliceCursor.SetCenter(self.imageBlend.GetOutput().GetCenter())
        
    # Update data information
    def update_data_information(self):
        # Calculate the scaler range of data
        self.scalerRange = self.imageReader.GetOutput().GetScalarRange()
        
        # Calculate the dimensions of data
        self.imageDimensions = self.imageReader.GetOutput().GetDimensions()
        
        # Calculate the bounds of the data
        self.bounds = self.imageReader.GetOutput().GetBounds()