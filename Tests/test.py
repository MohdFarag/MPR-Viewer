import vtk

# Global variables to store the line widgets
line_widget_x = None
line_widget_y = None

start_point, end_point = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]

def on_line_widget_move(obj, event):
    # This function will be called whenever the line widget is moved
    interactor = obj.GetInteractor()
    
    # Get the movement vector of the line widget
    start_point = [0.0, 0.0, 0.0]
    end_point = [0.0, 0.0, 0.0]
    
    start_point, end_point = obj.GetPolyData(obj)
    movement_vector = [end_point[i] - start_point[i] for i in range(3)]
    
    # Update the other line widget with the same movement vector
    global line_widget_x, line_widget_y
    if obj == line_widget_x:
        line_widget_y.SetPoint1(line_widget_y.GetPoint1()[0] + movement_vector[0], 0, 0)
        line_widget_y.SetPoint2(line_widget_y.GetPoint2()[0] + movement_vector[0], 0, 0)
    elif obj == line_widget_y:
        line_widget_x.SetPoint1(0, line_widget_x.GetPoint1()[1] + movement_vector[1], 0)
        line_widget_x.SetPoint2(0, line_widget_x.GetPoint2()[1] + movement_vector[1], 0)

    interactor.Render()

def main():
    # Step 2: Load your .mhd file
    filename = "./Resources/Dataset/out.mhd"

    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(filename)
    reader.Update()
    image_data = reader.GetOutput()

    # Step 3: Create the rendering components
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.2, 0.3, 0.4)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Calculate the length of the axes based on image dimensions
    image_dims = image_data.GetDimensions()
    axes_length = max(image_dims) * 0.5  # Set the axes length to half of the maximum dimension

    # Create the X-axis line widget
    global line_widget_x
    line_widget_x = vtk.vtkLineWidget()
    line_widget_x.SetInteractor(interactor)
    line_widget_x.SetResolution(100)  # Set the resolution of the line
    line_widget_x.SetPoint1(-axes_length, 0, 0)
    line_widget_x.SetPoint2(axes_length, 0, 0)
    line_widget_x.GetLineProperty().SetColor(1, 0, 0)  # Set the color of the X-axis to red

    # Create the Y-axis line widget
    global line_widget_y
    line_widget_y = vtk.vtkLineWidget()
    line_widget_y.SetInteractor(interactor)
    line_widget_y.SetResolution(100)  # Set the resolution of the line
    line_widget_y.SetPoint1(0, -axes_length, 0)
    line_widget_y.SetPoint2(0, axes_length, 0)
    line_widget_y.GetLineProperty().SetColor(0, 1, 0)  # Set the color of the Y-axis to green

    # Add event observers for line widget movement
    line_widget_x.AddObserver(vtk.vtkCommand.EndInteractionEvent, on_line_widget_move)
    line_widget_y.AddObserver(vtk.vtkCommand.EndInteractionEvent, on_line_widget_move)

    # Start the line widget interaction
    line_widget_x.On()
    line_widget_y.On()

    # Start the interaction
    interactor.Initialize()
    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    main()
