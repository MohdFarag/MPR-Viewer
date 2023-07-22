
from vtk import *
from VtkAdditions import *
from CommandSliceSelect import *

class VtkBase():
    
    # Constructor
    def __init__(self) -> None:
        
        # Global attributes
        self.viewUp = [[0, 0, -1], [0, 0, 1], [0, 1, 0]]
        
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
        self.imageShiftScale.SetShift(-float(self.slicesRange[0]))
        self.imageShiftScale.UpdateWholeExtent()
        
        ### Image Window Level *
        self.imageWindowLevel = vtkImageMapToWindowLevelColors()
        self.imageWindowLevel.SetInputConnection(self.imageShiftScale.GetOutputPort())
        self.imageWindowLevel.SetWindow(100.0)
        self.imageWindowLevel.SetLevel(50.0)
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

        ### Segmentation ***
        self.segmentationImage = vtkImageData()
        self.segmentationImage.DeepCopy(self.imageShiftScale.GetOutput())            
        self.segmentationImage.Modified()
        
        self.segmentationLabelImage = vtkImageMapToColors()
        self.segmentationLabelImage.SetInputData(self.segmentationImage)
        self.segmentationLabelImage.SetOutputFormatToRGBA()

        self.segmentationLabelLookupTable = vtkLookupTable()                    
        self.segmentationLabelLookupTable.SetNumberOfTableValues(256)
        self.segmentationLabelLookupTable.SetTableRange(0, 255)
        self.segmentationLabelLookupTable.SetTableValue(0, 0, 1, 0, 0.0)
        self.segmentationLabelLookupTable.SetTableValue(1, 1.0, 0, 0, 0.5)

        self.segmentationLabelImage.SetLookupTable(self.segmentationLabelLookupTable)
        self.segmentationLabelImage.UpdateWholeExtent()
        
        ## Image Blend
        self.imageBlend = vtkImageBlend()
        self.imageBlend.AddInputData(self.imageMapToColors.GetOutput())
        self.imageBlend.AddInputData(self.segmentationLabelImage.GetOutput())
        self.imageBlend.UpdateWholeExtent()
        
        ## Picker        
        self.picker = vtkCellPicker()
        self.picker.SetTolerance(0.05)
        
        ## Property
        self.property = vtk.vtkProperty()

        ## Image Reslice
        self.resliceCursor = vtk.vtkResliceCursor()
        self.resliceCursor.SetThickMode(0)
        self.resliceCursor.SetThickness(10, 10, 10)
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
        self.imageShiftScale.SetShift(-float(self.slicesRange[0]))
        if self.slicesRange[1] != self.slicesRange[0]:
            self.imageShiftScale.SetScale(255.0/(float(self.slicesRange[1] - self.slicesRange[0])))
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

        ### Segmentation
        self.segmentationImage.DeepCopy(self.imageShiftScale.GetOutput())
        self.segmentationImage.Modified()
        
        self.segmentationLabelImage.SetInputData(self.segmentationImage)
        self.segmentationLabelImage.UpdateWholeExtent()
        
        ### Image Blend
        self.imageBlend.RemoveAllInputs()
        self.imageBlend.AddInputData(self.imageMapToColors.GetOutput())
        self.imageBlend.AddInputData(self.segmentationLabelImage.GetOutput())
        self.imageBlend.SetOpacity(0, 1.0)
        self.imageBlend.SetOpacity(1, 0.0)
        self.imageBlend.UpdateWholeExtent() 
        
        ### Reslice Cursor        
        self.resliceCursor.SetCenter(self.imageBlend.GetOutput().GetCenter())
        self.resliceCursor.SetImage(self.imageBlend.GetOutput())
        
    # Update data information
    def update_data_information(self):
        self.slicesRange = self.imageReader.GetOutput().GetScalarRange()
        self.imageDimensions = self.imageReader.GetOutput().GetDimensions()
        
        self.extent = self.imageReader.GetDataExtent()
        self.spacing = self.imageReader.GetDataSpacing()
        self.origin = self.imageReader.GetDataOrigin()

        self.center[0] = self.origin[0] + self.spacing[0] * 0.5 * (self.extent[0] + self.extent[1])
        self.center[1] = self.origin[1] + self.spacing[1] * 0.5 * (self.extent[2] + self.extent[3])
        self.center[2] = self.origin[2] + self.spacing[2] * 0.5 * (self.extent[4] + self.extent[5])

        self.bounds = self.imageReader.GetOutput().GetBounds()
