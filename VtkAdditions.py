
import vtk
import numpy as np

class vtkAxesWidget(vtk.vtkLineWidget):
    
    # Constructor
    def __init__(self) -> None:
        super().__init__()
        
        self.x_line_pos = 0 # X-axis position
        self.y_line_pos = 0 # Y-axis position
        self.width = 0 # Width
        self.height = 0 # Height
        self.x = 0
        self.y = 0
        self.bounds = (0,0,0,0,0,0)
        self.moved = None
        
        # Create the X-axis line widget
        self.line_widget_x = vtk.vtkLineWidget()
        self.line_widget_x.SetAlignToZAxis()

        # Create the Y-axis line widget
        self.line_widget_y = vtk.vtkLineWidget()
        self.line_widget_y.SetAlignToZAxis()
       
        self.AddDefaultObservers()
    
    # Set the interactor of the X-axis and Y-axis
    def SetInteractor(self, interactor):
        self.line_widget_x.SetInteractor(interactor)
        self.line_widget_y.SetInteractor(interactor)
    
    # Get the interactor of the X-axis and Y-axis
    def GetInteractor(self):
        return self.line_widget_x.GetInteractor()
    
    # Set the bounds of the X-axis and Y-axis
    def SetBounds(self, bounds):
        self.bounds = bounds
         
    # Set the resolution of the X-axis and Y-axis           
    def SetResolution(self, resolution):
        self.line_widget_x.SetResolution(resolution)
        self.line_widget_y.SetResolution(resolution)
      
    # Set the size of the X-axis and Y-axis  
    def SetSize(self, width, height):
        self.width = width # Width
        self.height = height # Height

    # Set the position of the X-axis and Y-axis
    def SetPosition(self, x, y):
        self.x = x
        self.y = y
        self.line_widget_x.SetPoint1(x-self.width/2, 0, 1)
        self.line_widget_x.SetPoint2(x+self.width/2, 0, 1)
        self.line_widget_y.SetPoint1(0, y-self.height/2, 1)
        self.line_widget_y.SetPoint2(0, y+self.height/2, 1)
    
        self.x_line_pos = self.GetPointsX()
        self.y_line_pos = self.GetPointsY()

    # Set the color of the X-axis and Y-axis
    def SetColor(self, x_color, y_color):
        self.line_widget_x.GetLineProperty().SetColor(x_color)  # Set the color of the X-axis to red       
        self.line_widget_y.GetLineProperty().SetColor(y_color)  # Set the color of the Y-axis to green

    # Get the points of the X-axis
    def GetPointsX(self):
        p1 = list(self.line_widget_x.GetPoint1())
        p2 = list(self.line_widget_x.GetPoint2())
        return np.array([p1, p2])
    
    # Get the points of the Y-axis
    def GetPointsY(self):
        p1 = list(self.line_widget_y.GetPoint1())
        p2 = list(self.line_widget_y.GetPoint2())
        return np.array([p1, p2])

    # Update the position of the X-axis and Y-axis
    def Update(self):
        # Update the position of the X-axis/Y-axis
        self.x_line_pos = self.GetPointsX()
        self.y_line_pos = self.GetPointsY()
        
        # Update the width and height
        self.width = self.line_widget_x.GetPoint2()[0] - self.line_widget_x.GetPoint1()[0]
        self.height = self.line_widget_y.GetPoint2()[1] - self.line_widget_y.GetPoint1()[1]
        
        # Update the origin axis
        self.x = (self.line_widget_x.GetPoint2()[0] + self.line_widget_x.GetPoint1()[0]) / 2
        self.y = (self.line_widget_y.GetPoint2()[1] + self.line_widget_y.GetPoint1()[1]) / 2
        
        self.line_widget_x.GetInteractor().Render()

    # Turn on the line widget
    def On(self):
        self.line_widget_x.On()
        self.line_widget_y.On()
    
    # Move the axis by a given amount
    def Move(self, diff_x, diff_y):
        # Update the position of the X-axis
        self.line_widget_x.SetPoint1(self.line_widget_x.GetPoint1() + diff_y[0])
        self.line_widget_x.SetPoint2(self.line_widget_x.GetPoint2() + diff_y[0])

        # Update the position of the X-axis
        self.line_widget_x.SetPoint1(self.line_widget_x.GetPoint1() + diff_x[1])
        self.line_widget_x.SetPoint2(self.line_widget_x.GetPoint2() + diff_x[1])

        # Update the position of the Y-axis
        self.line_widget_y.SetPoint1(self.line_widget_y.GetPoint1() + diff_x[1])
        self.line_widget_y.SetPoint2(self.line_widget_y.GetPoint2() + diff_x[1])

        # Update the position of the Y-axis
        self.line_widget_y.SetPoint1(self.line_widget_y.GetPoint1() + diff_y[0])
        self.line_widget_y.SetPoint2(self.line_widget_y.GetPoint2() + diff_y[0])

        self.Update()
        
    def MoveX(self, diff_y):
        # Update the position of the X-axis
        self.line_widget_x.SetPoint1(self.line_widget_x.GetPoint1() + diff_y[0])
        self.line_widget_x.SetPoint2(self.line_widget_x.GetPoint2() + diff_y[1])
                
    def MoveY(self, diff_x):
        # Update the position of the X-axis
        self.line_widget_y.SetPoint1(self.line_widget_y.GetPoint1() + diff_x[0])
        self.line_widget_y.SetPoint2(self.line_widget_y.GetPoint2() + diff_x[1])
            
    def Move2(self, obj):
        if obj == self.line_widget_x:
            y_line_pos_new = self.GetPointsY()
            diff = y_line_pos_new - self.y_line_pos
            self.MoveX(diff)
        elif obj == self.line_widget_y:
            x_line_pos_new = self.GetPointsX()
            diff = x_line_pos_new - self.x_line_pos
            self.MoveY(diff)
            
        # self.Update()

    # Events   
    # Add Default observers
    def AddDefaultObservers(self):
        self.line_widget_x.AddObserver(vtk.vtkCommand.InteractionEvent, self.MoveEvent)
        self.line_widget_y.AddObserver(vtk.vtkCommand.InteractionEvent, self.MoveEvent)
    
    # When user moves the line widget, update the position of the other line widget      
    def MoveEvent(self, obj, event):       
        # self.Move2(obj)
        self.Modified()