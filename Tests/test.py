import vtk

class VTKRenderer:
    def __init__(self):
        # Create a renderer
        self.renderer = vtk.vtkRenderer()
        
        # Create a render window
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        
        # Create an interactor
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
    
    def add_actor(self, actor):
        # Add an actor to the renderer
        self.renderer.AddActor(actor)
    
    def set_background(self, color):
        # Set the background color of the renderer
        self.renderer.SetBackground(color)
    
    def start(self):
        # Start the rendering and interaction
        self.render_window.Render()
        self.interactor.Start()

    def openFile(self, fileName):
        # Read the MHD file
        reader = vtk.vtkMetaImageReader()
        reader.SetFileName(fileName)
        reader.Update()
        
        # Get the output data
        data = reader.GetOutput()
        
        # Create a mapper
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(data)
        
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        # Add the actor to the renderer
        self.add_actor(actor)
        
        # Set the background color
        self.set_background([0,0,0])
        
        # Start the rendering
        self.start()
        
    
def main():
    # Create an instance of the VTKRenderer class
    vtk_renderer = VTKRenderer()
    vtk_renderer.openFile(r"C:\Users\moham\OneDrive\Desktop\MohdAhmed\MRI\Task01\out.mhd")

if __name__ == '__main__':
    main()
