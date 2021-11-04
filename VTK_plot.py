import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from vtk import (vtkUnstructuredGridReader, vtkDataSetMapper, vtkActor,vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor)

def vtk_plot(file_name):
    '''
    
    '''
    # Read the source file.
    reader = vtkUnstructuredGridReader()
    reader.SetFileName(file_name)
    reader.Update()  # Needed because of GetScalarRange
    output = reader.GetOutput()
    output_port = reader.GetOutputPort()
    scalar_range = output.GetScalarRange()

    # obtain vtk_array and then convert them into numpy_array
    nodes_vtk_array= reader.GetOutput().GetPoints().GetData()
    # print(nodes_vtk_array)
    numpy_nodes = vtk_to_numpy(nodes_vtk_array)

    z_min = min(numpy_nodes[:,2])
    z_max = max(numpy_nodes[:,2])

    lookUpTable = vtk.vtkLookupTable()
    lookUpTable.SetTableRange(z_min,z_max)
    lookUpTable.Build()

    # Create a unsigned char array to color
    uCharArray = vtk.vtkUnsignedCharArray()
    uCharArray.SetNumberOfComponents(3)
    uCharArray.SetName("colors")

    # Assign color by extracting each color
    for i in range(output.GetNumberOfPoints()):
        point = output.GetPoint(i)
        # Get the color from lookup table
        color = [0]*3
        lookUpTable.GetColor(point[2],color)
        # Convert each color to 255
        for j in range(len(color)):
            color[j] = int(255 * color[j])
        uCharArray.InsertTypedTuple(i,color)

    # # Set Scalars
    output.GetPointData().SetScalars(uCharArray)

    # Create the mapper that corresponds the objects of the vtk file
    # into graphics elements
    mapper = vtkDataSetMapper()
    mapper.SetInputConnection(output_port)
    mapper.SetColorModeToDefault()
    mapper.SetScalarRange(scalar_range)

    # Create the Actor
    actor = vtkActor()
    actor.SetMapper(mapper)

    colors = vtk.vtkNamedColors()
    actor.GetProperty().SetColor(colors.GetColor3d("Bisque"))

    # Create the Renderer
    renderer = vtkRenderer()
    renderer.AddActor(actor)
    # renderer.AddActor(colorbar)
    renderer.SetBackground(colors.GetColor3d('Navy')) # Set background to white
    renderer.ResetCamera()

    # Create the RendererWindow
    renderer_window = vtkRenderWindow()
    renderer_window.AddRenderer(renderer)

    # Create the RendererWindowInteractor and display the vtk_file
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderer_window)
    interactor.Initialize()
    interactor.Start()