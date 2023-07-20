
from vtk import *
from VtkAdditions import *

class VtkBase():
    
    # Constructor
    def __init__(self) -> None:
        
        ## Reader *
        self.imageReader = vtkMetaImageReader()
        temp_path = "./temp/out.mhd"
        self.imageReader.SetFileName(temp_path) 
        self.imageReader.UpdateWholeExtent()
        slicesRange = self.imageReader.GetOutput().GetScalarRange()

        ## Filters 
        ### Image Shift Scale *
        self.imageShiftScale = vtkImageShiftScale()
        self.imageShiftScale.SetInputData(self.imageReader.GetOutput())
        self.imageShiftScale.SetOutputScalarTypeToUnsignedChar()
        self.imageShiftScale.SetShift(-float(slicesRange[0]))
        self.imageShiftScale.SetScale(255.0/(float(slicesRange[1]-slicesRange[0])))
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
        
    def connect_on_data(self, path:str):
        if path == "":
            return

        ## Reader
        self.imageReader.SetFileName(path)
        self.imageReader.UpdateWholeExtent()
        slicesRange = self.imageReader.GetOutput().GetScalarRange()
        
        ## Image Shift Scale
        self.imageShiftScale.SetShift(-float(slicesRange[0]))
        self.imageShiftScale.SetScale(255.0/(float(slicesRange[1]-slicesRange[0])))
        self.imageShiftScale.UpdateWholeExtent()

        ### Image Window Level
        self.imageWindowLevel.SetWindow(100.0)
        self.imageWindowLevel.SetLevel(50.0)
        self.imageWindowLevel.UpdateWholeExtent()

        ### Image Map To Colors
        self.imageMapToColors.SetInputData(self.imageWindowLevel.GetOutput())
        self.imageMapToColors.SetOutputFormatToRGBA()
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