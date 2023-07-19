
import vtk
import numpy as np

class vtkAxesWidget():
    def __init__(self) -> None:
        super().__init__()

        self.x_line_pos = 0 # X-axis position
        self.y_line_pos = 0 # Y-axis position
        self.width = 0 # Width
        self.height = 0 # Height
        self.x = 0
        self.y = 0
        self.bounds = (0,0,0,0,0,0)
        
        # Create the X-axis line widget
        self.line_widget_x = vtk.vtkLineWidget()
        self.line_widget_x.SetAlignToZAxis()

        # Create the Y-axis line widget
        self.line_widget_y = vtk.vtkLineWidget()
        self.line_widget_y.SetAlignToZAxis()
       
        self.AddObservers()
    
    def SetInteractor(self, interactor):
        self.line_widget_x.SetInteractor(interactor)
        self.line_widget_y.SetInteractor(interactor)
    
    def SetBounds(self, bounds):
        self.bounds = bounds
                    
    def SetResolution(self, resolution):
        self.line_widget_x.SetResolution(resolution)
        self.line_widget_y.SetResolution(resolution)
        
    def SetSize(self, width, height):
        self.width = width # Width
        self.height = height # Height

    def SetPosition(self, x, y):
        self.x = x
        self.y = y
        self.line_widget_x.SetPoint1(x-self.width/2, 0, 0)
        self.line_widget_x.SetPoint2(x+self.width/2, 0, 0)
        self.line_widget_y.SetPoint1(0, y-self.height/2, 0)
        self.line_widget_y.SetPoint2(0, y+self.height/2, 0)
    
        self.x_line_pos = self.GetPointsX()
        self.y_line_pos = self.GetPointsY()

    def SetColor(self, x_color, y_color):
        self.line_widget_x.GetLineProperty().SetColor(x_color)  # Set the color of the X-axis to red       
        self.line_widget_y.GetLineProperty().SetColor(y_color)  # Set the color of the Y-axis to green

    def On(self):
        self.line_widget_x.On()
        self.line_widget_y.On()

    def GetPointsX(self):
        p1 = list(self.line_widget_x.GetPoint1())
        p2 = list(self.line_widget_x.GetPoint2())
        return np.array([p1, p2])
    
    def GetPointsY(self):
        p1 = list(self.line_widget_y.GetPoint1())
        p2 = list(self.line_widget_y.GetPoint2())
        return np.array([p1, p2])
    
    # Events
    def AddObservers(self):    
        self.line_widget_x.AddObserver(vtk.vtkCommand.InteractionEvent, self.moveEvent)
        self.line_widget_y.AddObserver(vtk.vtkCommand.InteractionEvent, self.moveEvent)
         
    def moveEvent(self, obj, event):
        interactor = obj.GetInteractor()
           
        # Update the position of the other line widget based on the moved one
        if obj == self.line_widget_x:
            x_line_pos_new = self.GetPointsX()
            diff = x_line_pos_new -self.x_line_pos
            
            self.line_widget_y.SetPoint1(self.line_widget_y.GetPoint1() + diff[0])
            self.line_widget_y.SetPoint2(self.line_widget_y.GetPoint2() + diff[1])
        elif obj == self.line_widget_y:
            y_line_pos_new = self.GetPointsY()
            diff = y_line_pos_new - self.y_line_pos
            
            self.line_widget_x.SetPoint1(self.line_widget_x.GetPoint1() + diff[0])
            self.line_widget_x.SetPoint2(self.line_widget_x.GetPoint2() + diff[0])

        self.x_line_pos = self.GetPointsX()
        self.y_line_pos = self.GetPointsY()
        self.width = self.line_widget_x.GetPoint2()[0] - self.line_widget_x.GetPoint1()[0]
        self.height = self.line_widget_y.GetPoint2()[1] - self.line_widget_y.GetPoint1()[1]
        self.x = (self.line_widget_x.GetPoint2()[0] + self.line_widget_x.GetPoint1()[0]) / 2
        self.y = (self.line_widget_y.GetPoint2()[1] + self.line_widget_y.GetPoint1()[1]) / 2
        
        # Render the updated scene
        interactor.Render()
