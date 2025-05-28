#! python3

def importer():
    """Imports necessary libraries for the script."""
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore

def PreProcessing(mesh, outputPath, fileName=None, preProcessing='shrinkwrap', outputType='igs', resolution=1, smoothing=0, deleteInput=True, saveOutput=False):
    """
    Performs pre-processing operations on a mesh object.

    Args:
        mesh: The input mesh object.
        outputPath: The directory to save the output file.
        fileName (str, optional): Name of the output file. Defaults to None.
        preProcessing (str, optional): Type of pre-processing.
            Options: 'shrinkwrap', 'fixholes', 'fixshell'. Defaults to 'shrinkwrap'.
        outputType (str, optional): File type for the output. Defaults to 'igs'.
        resolution (int, optional): Resolution for shrinkwrap. Defaults to 1.
        smoothing (int, optional): Smoothing iterations for shrinkwrap. Defaults to 0.
        deleteInput (bool, optional): Whether to delete the input mesh after processing. Defaults to True.
        saveOutput (bool, optional): Whether to save the processed mesh. Defaults to False.

    Returns:
        The processed mesh object, or None if processing fails.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    obj1 = mesh
    rs.SelectObject(obj1)
    if preProcessing == 'shrinkwrap':
        rs.Command(f"_-NoEcho _-ShrinkWrap Resolution={resolution} Offset=0 Smooth={smoothing} PolygonOptimize=0 FillHoles=On VertexColors=Off DeleteInput={deleteInput} Preview=Off DrawWires=On HideInput=Off Enter")
        rs.Command(f'_SelLast')
        obj2 = rs.SelectedObjects()[0]
        rs.Command(f"_Invert ")
        rs.Command(f"_Delete ")
    elif preProcessing == 'fixholes':
        rs.Command("_-FillMeshHoles Enter")
        rs.Command("_-SelAll Enter")
        obj2 = rs.SelectedObjects()[0]
    elif preProcessing == 'fixshell':
        rs.Command("_-SelAll Enter")
        rs.Command("_-SplitDisjointMesh Enter")
        rs.Command("_-SelAll Enter")
        allMeshes = rs.SelectedObjects()
        area = []
        for mesh in allMeshes:
            area.append(rs.MeshArea(mesh)[1])
        rs.UnselectAllObjects()
        rs.Command("_-Invert Enter")
        rs.Command("_-Delete Enter")
        rs.Command("_-SelAll Enter")
        obj2 = rs.SelectedObjects()[0]
    else:
        print("Wrong input given, choose between 'shrinkwrap', 'fixholes', or 'fixshell'")
        obj2 = None
    if saveOutput and obj2 != None:
        exportMesh(obj2, outputPath, outputType, fileName)

    return obj2

def exportMesh(mesh, outputPath, fileType, fileName):
    """
    Exports a mesh object to a specified file type.

    Args:
        mesh: The mesh object to export.
        outputPath: The directory to save the exported file.
        fileType (str): The desired file type (e.g., 'igs', 'step').
        fileName (str): The name for the exported file.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    rs.SelectObject(mesh)
    name = fileName
    if fileType == 'igs' or fileType == 'iges' or fileType == 'step' or fileType == 'stp':
        outputFile = f"{outputPath}\{name}.{fileType}"
        rs.Command(f"_-Export ({outputFile}) Enter")
    else:
        print("Wrong filetype inputted, choose between 'igs', 'iges', 'step', 'stp'")

def stl2cad(mesh, targetEdgeLength=2, adaptiveSize=100, deleteInputs=True, subd=True):
    """
    Converts an STL-like mesh to a CAD format (NURBS or SubD).

    Args:
        mesh: The input mesh object.
        targetEdgeLength (int, optional): Target edge length for QuadRemesh. Defaults to 2.
        adaptiveSize (int, optional): Adaptive size percentage for QuadRemesh. Defaults to 100.
        deleteInputs (bool, optional): Whether to delete intermediate objects. Defaults to True.
        subd (bool, optional): If True, converts to SubD then NURBS. 
                               If False, directly to NURBS from QuadRemesh. Defaults to True.

    Returns:
        The converted CAD object (NURBS or SubD), or None if conversion fails.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    shrink = mesh
    retry = True

    while retry:

        rs.SelectObject(shrink)
        rs.Command(f"_-NoEcho _-QuadRemesh TargetEdgeLength={targetEdgeLength} AdaptiveSize={adaptiveSize} Enter") # quad remeshing
        quad = rs.FirstObject()
        
    
        if quad != shrink and quad != None:   
            rs.Command('_SelLast')
            if not subd:
                rs.Command("_-NoEcho _-ToNurbs DeleteInputObjects=No Enter") # convert subD to nurbs
                rs.Command(f"_SelLast ")
                outMesh = rs.SelectedObjects()[0]
                if deleteInputs == True:
                    rs.DeleteObject(quad)
            else:
                subd = mesh_to_subd(quad)
                outMesh = subd_to_nurbs(subd)
            retry = False
        else:
            print("Error: quadremesh failed, trying again...")
            retry = True
    return outMesh
    
def meshDistanceCalculator(mesh1, mesh2):
    """
    Calculates the distance between two meshes by ray casting from faces of mesh2 to mesh1.

    Args:
        mesh1: The first mesh object (target for ray casting).
        mesh2: The second mesh object (source of rays from face centers).

    Returns:
        list: A list of distances for each face center of mesh2 that intersected mesh1.
              None is appended if no intersection or intersection is beyond cutoff.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    id1 = mesh1
    id2 = mesh2



    normals1 = rs.MeshFaceNormals(id1)
    faces1 = rs.MeshFaces(id1)

    norm = np.array(normals1)
    normPoints = np.array([[p.X, p.Y, p.Z] for p in norm.flatten()])
    normals1 = normPoints.reshape(-1,3)
    normLen = np.linalg.norm(normals1, axis=1)[:, np.newaxis]
    normals1 = normals1 / normLen

    arr = np.array(faces1)
    # Delete every 4th row to get rid of duplicates caused by having triangles
    arr_new = np.delete(arr, np.arange(3, arr.shape[0], 4), axis=0)
    # Flatten + extract coordinates
    points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr_new.flatten()])
    # Reshape into faces
    faces1 = points_xyz.reshape(-1, 3, 3)




    normals2 = rs.MeshFaceNormals(id2)
    faces2 = rs.MeshFaces(id2)

    norm = np.array(normals2)
    normPoints = np.array([[p.X, p.Y, p.Z] for p in norm.flatten()])
    normals2 = normPoints.reshape(-1,3)
    #normalize normals just in case
    normLen = np.linalg.norm(normals2, axis=1)[:, np.newaxis]
    normals2 = normals2 / normLen

    arr = np.array(faces2)
    # Flatten + extract coordinates
    points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr.flatten()])
    # Reshape into faces
    faces2 = points_xyz.reshape(-1, 4, 3)



    # calculate centers
    centers1 = []
    for i in range(0, len(faces1)):
        current_face = faces1[i]
        centers1.append([(current_face[0,0]+current_face[1,0]+current_face[2,0])/3, (current_face[0,1]+current_face[1,1]+current_face[2,1])/3, (current_face[0,2]+current_face[1,2]+current_face[2,2])/3])

    centers2 = []
    for i in range(0, len(faces2)):
        current_face = faces2[i]
        centers2.append([(current_face[0,0]+current_face[1,0]+current_face[2,0]+current_face[3,0])/4, (current_face[0,1]+current_face[1,1]+current_face[2,1]+current_face[3,1])/4, (current_face[0,2]+current_face[1,2]+current_face[2,2]+current_face[3,2])/4])


    # calculate distance
    dist = []
    cutoffValue = 10
    for i in range(0, len(centers2)):
        mesh = rs.coercemesh(id1)
        origin = rg.Point3d(float(centers2[i][0]),float(centers2[i][1]), float(centers2[i][2]))
        direction = rg.Vector3d(float(normals2[i][0]), float(normals2[i][1]), float(normals2[i][2]))
        ray = rg.Ray3d(origin, direction)
        intersect = rg.Intersect.Intersection.MeshRay(mesh, ray)

        if intersect > 0 and intersect < cutoffValue:
            hit_point = ray.PointAt(intersect)
            dist.append( ((centers2[i][0]-hit_point.X)**2 + (centers2[i][1]-hit_point.Y)**2 + (centers2[i][2]-hit_point.Z)**2 )**0.5 )

        else:
            origin = rg.Point3d(float(centers2[i][0]),float(centers2[i][1]), float(centers2[i][2]))
            direction = rg.Vector3d(float(-normals2[i][0]), float(-normals2[i][1]), float(-normals2[i][2]))
            ray = rg.Ray3d(origin, direction)
            intersect = rg.Intersect.Intersection.MeshRay(mesh, rg.Ray3d(origin, direction))

            if intersect > 0 and intersect < cutoffValue:
                hit_point = ray.PointAt(intersect)
                dist.append( ((centers2[i][0]-hit_point.X)**2 + (centers2[i][1]-hit_point.Y)**2 + (centers2[i][2]-hit_point.Z)**2 )**0.5 )

            else:
                dist.append(None)
        print(f"{i}/{len(centers2)}")



    # outputs
    print('Average error is ', str(np.average([i for i in dist if i is not None])), 'mm')
    print('Maximum error is ', str(max([i for i in dist if i is not None])), 'mm')
    print('Minimum error is ', str(min([i for i in dist if i is not None])), 'mm')
    print('No intersections found at ', str(sum(x is None for x in dist)), 'positions')

    # Adding visual line for debugging
    org = centers2[dist.index(max([i for i in dist if i is not None]))]
    dir = normals2[dist.index(max([i for i in dist if i is not None]))]
    vec = org + dir
    lenVec = max([i for i in dist if i is not None])
    rs.AddLine(org, org+lenVec*dir)

    return dist

def deleteNonsense():
    """Allows the user to select a mesh to keep and deletes all other objects."""
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    rs.GetObjects("Select mesh you want to keep", 32, True, False, True, None, 1, 0, None)
    rs.Command(f'_-Invert ')
    rs.Command(f'_-Delete ')
    return

def chamferDistance(mesh1, mesh2, quads=True):
    """
    Calculates Chamfer and Hausdorff distances between two meshes.

    Args:
        mesh1: The first mesh object.
        mesh2: The second mesh object.
        quads (bool, optional): Indicates if the meshes are primarily quads.
                                 This affects how face vertices are extracted. Defaults to True.

    Returns:
        list: A list containing Chamfer distance and Hausdorff distance,
              or [None, None] if input meshes are invalid.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    dist = []
    id1 = mesh1
    id2 = mesh2
    rs.SelectObject(id2)
    rs.Command('_-NoEcho _-Mesh DetailedOptions=Yes JaggedSeams=No SimplePlane=No Refine=Yes PackTextures=No Enter')
    rs.Command(f'_SelLast ')
    id2 = rs.SelectedObjects()[0]
    print("Computing distances...")
    if quads == True:
        if rs.IsMesh(id1) and rs.IsMesh(id2):

            faces1 = rs.MeshFaces(id1)
            faces2 = rs.MeshFaces(id2)

            arr = np.array(faces1)
            # Get points
            points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr.flatten()])
            # Reshape into faces
            faces1 = points_xyz.reshape(-1, 3)

            arr = np.array(faces2)
            # Get points
            points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr.flatten()])
            # Reshape into faces
            faces2 = points_xyz.reshape(-1, 3)

            dist.append(pcu.chamfer_distance(faces1, faces2)) 
            dist.append(pcu.hausdorff_distance(faces1, faces2))
        else:
            dist = [None, None]
            print("Invalid input meshes")
    else:
        if rs.IsMesh(id1) and rs.IsMesh(id2):
            faces1 = rs.MeshFaces(id1)
            faces2 = rs.MeshFaces(id2)

            arr = np.array(faces1)
            # Delete every 4th row to get rid of duplicates caused by having triangles
            arr_new = np.delete(arr, np.arange(3, arr.shape[0], 4), axis=0)
            # Flatten + extract coordinates
            points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr_new.flatten()])
            # Reshape into faces
            faces1 = points_xyz.reshape(-1, 3)

            arr = np.array(faces2)
            # Delete every 4th row to get rid of duplicates caused by having triangles
            arr_new = np.delete(arr, np.arange(3, arr.shape[0], 4), axis=0)
            # Flatten + extract coordinates
            points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr_new.flatten()])
            # Reshape into faces
            faces2 = points_xyz.reshape(-1, 3)

            dist.append(pcu.chamfer_distance(faces1, faces2)) 
            dist.append(pcu.hausdorff_distance(faces1, faces2))
        else:
            dist = [None, None]
            print("Invalid input meshes")
    return dist

def importFile(inputPath):
    """
    Imports a file into Rhino, creating a new document.

    Args:
        inputPath (str): The full path to the file to be imported.

    Returns:
        The imported mesh object (last object created).
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore

    # Open new file
    rs.Command(f"_-NoEcho _-New No None Enter")
    path = inputPath
    file = f'_-Import "{path}" Enter'
    Rhino.RhinoApp.RunScript(file, False)
    rs.Command(f'_SelLast')
    originalMesh = rs.LastObject()
    return originalMesh

def fullPipelineBatch(inputPath, outputPath, preProcess=True, edgePreProcessing=1, edgeConversion=2, smoothing=0):
    """
    Processes a batch of STL files from an input directory, converts them to CAD, and saves them.

    Args:
        inputPath (str): Path to the directory containing input STL files.
        outputPath (str): Path to the directory to save output IGS files.
        preProcess (bool, optional): Whether to perform pre-processing. Defaults to True.
        edgePreProcessing (int, optional): Resolution for pre-processing (e.g., ShrinkWrap). Defaults to 1.
        edgeConversion (int, optional): Target edge length for stl2cad conversion. Defaults to 2.
        smoothing (int, optional): Smoothing iterations for pre-processing. Defaults to 0.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    
    input_stl_path = inputPath
    igs_path = outputPath
    dir_list = os.listdir(input_stl_path)
    igs_list = [f[:-3] + "igs" for f in dir_list]

    scriptcontext.doc.Views.RedrawEnabled = False
    # loop through all files

    for i, direc in enumerate(dir_list):

        # Print info
        start = time.time()
        print(f"Current File: {i+1}/{len(dir_list)}")
        print("-------------------------------------")

        # import
        pathFile = f"{input_stl_path}\{direc}"
        originalMesh = importFile(pathFile)

        if preProcess == True:
            # pre-process
            shrinkWrappedMesh = PreProcessing(originalMesh, edgePreProcessing, smoothing, 'Off')

            # convert to cad
            cad = stl2cad(shrinkWrappedMesh, edgeConversion)
        else:
            cad = stl2cad(originalMesh, edgeConversion)

        # Export as igs
        if cad:
            rs.SelectObject(cad)
            rs.Command(f"_-Export ({igs_path}\{igs_list[i]}) Enter")

        # Print info
        stop = time.time()
        print("-------------------------------------")
        progress = i/len(dir_list) * 100
        print(f"Progress: {progress:.2f}%")
        print(f"Previous iteration took: {(stop-start):.2f} seconds")

def fullPipeline(mesh, inputPath, outputPath, prep, preProcess=True, edgePreProcessing=1, edgeConversion=2, smoothing=0, heat=False, subd=True):
    """
    Processes a single mesh through pre-processing and CAD conversion.

    Args:
        mesh: The input mesh object.
        inputPath (str): Path of the input file (used for naming in heatmap).
        outputPath (str): Path to the directory for potential outputs.
        prep (str): The type of pre-processing to apply (e.g., 'shrinkwrap').
        preProcess (bool, optional): Whether to perform pre-processing. Defaults to True.
        edgePreProcessing (int, optional): Resolution for pre-processing. Defaults to 1.
        edgeConversion (int, optional): Target edge length for stl2cad conversion. Defaults to 2.
        smoothing (int, optional): Smoothing iterations for pre-processing. Defaults to 0.
        heat (bool, optional): Placeholder for heatmap generation (not fully implemented in this function). Defaults to False.
        subd (bool, optional): Whether to use SubD in the stl2cad conversion. Defaults to True.

    Returns:
        tuple: A tuple containing the original mesh, the shrink-wrapped mesh (or None), and the CAD object.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    

    scriptcontext.doc.Views.RedrawEnabled = False

    originalMesh = mesh
    if preProcess:
        # pre-process
        shrinkWrappedMesh = PreProcessing(mesh=originalMesh, outputPath=outputPath, preProcessing=prep, saveOutput=False, resolution=edgePreProcessing, smoothing=0)
        # convert to cad
        cad = stl2cad(shrinkWrappedMesh, edgeConversion, subd=subd)
    else:
        cad = stl2cad(originalMesh, edgeConversion, subd=subd)
        shrinkWrappedMesh = None

    return originalMesh, shrinkWrappedMesh, cad

def heatmap(mesh1, mesh2, inputPath, outputPath, plyPath, edgeConversion=2, quads=True, filename=None):
    """
    Generates a heatmap visualization of the distance between two meshes.

    Saves a 2D screenshot of the heatmap and a 3D PLY file of the mesh with vertex colors.

    Args:
        mesh1: The first mesh object (e.g., shrink-wrapped mesh, points for coloring).
        mesh2: The second mesh object (e.g., NURBS mesh, reference for distance calculation).
        inputPath (str): Path of the original input file (used for naming outputs if filename is None).
        outputPath (str): Directory to save the 2D heatmap image.
        plyPath (str): Directory to save the 3D PLY heatmap data.
        edgeConversion (int, optional): Edge conversion value, used for output naming. Defaults to 2.
        quads (bool, optional): Indicates if meshes are primarily quads for face extraction. Defaults to True.
        filename (str, optional): Custom filename for outputs. If None, derived from inputPath. Defaults to None.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore


    nurbsMesh = mesh2
    shrinkWrappedMesh = mesh1

    rs.SelectObject(nurbsMesh)
    rs.Command('_-NoEcho _-Mesh DetailedOptions=Yes JaggedSeams=No SimplePlane=No Refine=Yes PackTextures=No Enter')
    rs.Command(f'_SelLast ')
    nurbsMesh = rs.SelectedObjects()[0]

    print("Creating heatmap...")
    faces1 = rs.MeshFaces(shrinkWrappedMesh)
    faces2 = rs.MeshFaces(nurbsMesh)
    if quads == True:
        arr = np.array(faces1)
        # Get points
        points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr.flatten()])
        # Reshape into faces
        faces1 = points_xyz.reshape(-1, 3)
        arr = np.array(faces2)
        # Get points
        points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr.flatten()])
        # Reshape into faces
        faces2 = points_xyz.reshape(-1, 3)

    else:
        arr = np.array(faces1)
        # Delete every 4th row to get rid of duplicates caused by having triangles
        arr_new = np.delete(arr, np.arange(3, arr.shape[0], 4), axis=0)
        # Flatten + extract coordinates
        points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr_new.flatten()])
        # Reshape into faces
        faces1 = points_xyz.reshape(-1, 3)
        arr = np.array(faces2)
        # Delete every 4th row to get rid of duplicates caused by having triangles
        arr_new = np.delete(arr, np.arange(3, arr.shape[0], 4), axis=0)
        # Flatten + extract coordinates
        points_xyz = np.array([[p.X, p.Y, p.Z] for p in arr_new.flatten()])
        # Reshape into faces
        faces2 = points_xyz.reshape(-1, 3)
    
    tree = KDTree(faces2)
    distances, _ = tree.query(faces1, k=1)
    if filename:
        name = filename
        ident = f"File_{name}_Edge_{edgeConversion}"
    else:
        name = os.path.splitext(os.path.basename(inputPath))[0]
        ident = f"File_{name}_Edge_{edgeConversion}"
    
    """
    Visualizes both meshes, heatmap, max error, saves a 2D screenshot from Y-axis view,
    and saves the primary 3D heatmap actor with vertex colors in PLY format.
    """
    SHRINK_POINT_SIZE = 5
    DENSE_POINT_SIZE = 3
    DENSE_MESH_COLOR = 'grey'
    DENSE_MESH_ALPHA = 0.5
    MAX_ERROR_MARKER_SIZE_FACTOR = 1
    if faces1 is None or faces2 is None or distances is None:
        print("Missing data for visualization.")
        
    print("Preparing visualization and saving...")
    # 1. Create vedo objects
    shrink_viz = Points(faces1, r=SHRINK_POINT_SIZE)
    dense_viz = Points(faces2, r=DENSE_POINT_SIZE, c=DENSE_MESH_COLOR, alpha=DENSE_MESH_ALPHA)
    # Add distance data to the points object for scalar bar reference
    shrink_viz.pointdata["Distance"] = distances
    # 2. Calculate and Assign Vertex Colors Manually
    print("Calculating vertex colors...")
    shrink_viz.pointdata["Distance"] = distances
    shrink_viz.cmap("viridis", "Distance")  # Automatically color by scalar data
        
    # Add scalar bar to the shrink_viz object itself
    shrink_viz.add_scalarbar(title="Distance", c='k')
    # 3. Find and mark max error point
    max_dist_index = np.argmax(distances)
    max_dist_point = faces1[max_dist_index]
    max_dist_value = distances[max_dist_index]
    max_error_marker = Sphere(pos=max_dist_point,
                              r=SHRINK_POINT_SIZE * MAX_ERROR_MARKER_SIZE_FACTOR,
                              c='red')
    max_error_marker.name = "MaxErrorPoint"
    # 4. Calculate statistics
    min_dist = np.min(distances)
    mean_dist = np.average(distances)
    max_dist = max_dist_value
    stats_text = f"Distances:\nMin: {min_dist:.4f}\nMean: {mean_dist:.4f}\nMax: {max_dist:.4f}"
    stats_display = Text2D(stats_text, pos="top-left", s=0.8, bg='yellow', alpha=0.8)
    # --- Saving Section ---
    # 5. Setup Plotter for Screenshot
    plt = Plotter(title='Test', axes=1, offscreen=True)
    # Add actors needed for the screenshot (shrink_viz now has explicit colors and scalar bar)
    plt.add(shrink_viz, dense_viz, max_error_marker, stats_display)
    # 6. Set Camera View (Y-axis perspective)
    center = shrink_viz.center_of_mass()
    cam_pos = center + np.array([0, (shrink_viz.diagonal_size()) * 3, 0])
    plt.camera.SetPosition(cam_pos)
    plt.camera.SetFocalPoint(center)
    plt.camera.SetViewUp([0, 0, 1]) # Z-axis up
    plt.reset_clipping_range()
    # 7. Render and Save 2D screenshot
    output_image_path =f"{outputPath}\{ident}_heatmap.png"
    print(f"Saving 2D screenshot to: {output_image_path}")
    plt.render()
    plt.screenshot(output_image_path)
    # 8. Save 3D heatmap actor (shrink_viz) as ASCII PLY with vertex colors
    output_3d_path_ply = f"{plyPath}\{ident}_heatmapData.ply"
    print(f"Attempting save as ASCII PLY with uint8 vertex colors: {output_3d_path_ply}")
    try:
        # Save the shrink_viz object which now has .pointcolors set as uint8
        write(shrink_viz, output_3d_path_ply, binary=False)
        if os.path.exists(output_3d_path_ply) and os.path.getsize(output_3d_path_ply) > 0:
            print(f"Successfully saved ASCII PLY: {output_3d_path_ply}")
        else:
             print(f"PLY file not created by vedo.write (check vedo logs above).")
    except Exception as e_ply:
        print(f"Error saving 3D heatmap data as PLY: {e_ply}")

def mesh_to_subd(mesh_id):
    """
    Convert a mesh to SubD and return the SubD object ID.
    Args:
        mesh_id: Rhino object ID of the mesh.
    Returns:
        object ID of the SubD, or None if failed.
    """
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore

    print("Converting mesh to SubD...")
    rs.SelectObject(mesh_id)
    rs.Command("_-ToSubD _UseMesh=ControlPoints _MeshCreases=No _MeshCorners=No _UseSurface=Location _SurfaceCorners=No _DeleteInput=No _Enter")
    time.sleep(0.5)
    subd_objs = rs.LastCreatedObjects()
    rs.UnselectAllObjects()
    if not subd_objs:
        print("Error: ToSubD failed.")
        return None
    for obj in reversed(subd_objs):
        if rs.ObjectType(obj) in [262144, 32]:  # SubD types
            return obj
    print("Error: Could not find SubD object.")
    return None

def subd_to_nurbs(subd_id):
    """
    Convert a SubD object to NURBS using RhinoCommon and return the NURBS object ID.
    Args:
        subd_id: Rhino object ID of the SubD.
    Returns:
        object ID of the NURBS, or None if failed.
    """
    print("Converting SubD to NURBS using RhinoCommon...")
    import rhinoscriptsyntax as rs # type: ignore
    import Rhino.Geometry as rg # type: ignore  
    import scriptcontext # type: ignore
    import Rhino # type: ignore
    import numpy as np # type: ignore
    import time
    import point_cloud_utils as pcu # type: ignore
    import os
    import csv
    import shutil
    import pandas as pd # type: ignore
    from vedo import Points, show, Plotter, Sphere, Text2D, settings, write, Assembly # type: ignore
    import matplotlib.colors as mcolors # type: ignore
    import matplotlib.cm as cm # type: ignore
    import matplotlib.pyplot as plt_mpl # type: ignore
    from scipy.spatial import KDTree # type: ignore
    import System  # type: ignore
    try:
        subd_geometry = rs.coercegeometry(subd_id)
        if not isinstance(subd_geometry, Rhino.Geometry.SubD):
            print("Error: Input object ID {} is not a SubD.".format(subd_id))
            return None
        nurbs_brep = subd_geometry.ToBrep()
        if nurbs_brep is None:
            print("Error: RhinoCommon SubD.ToBrep() failed for SubD ID {}.".format(subd_id))
            return None
        if scriptcontext.doc:
            nurbs_id = scriptcontext.doc.Objects.AddBrep(nurbs_brep)
            if nurbs_id == System.Guid.Empty:
                print("Error: Failed to add the converted NURBS object to the document.")
                return None
            scriptcontext.doc.Views.Redraw()
            print("SubD successfully converted to NURBS object ID:", nurbs_id)
            return nurbs_id
        else:
            print("Error: Script not running in Rhino document context.")
            return None
    except Exception as e:
        print("An error occurred during SubD to NURBS conversion: {}".format(e))
        return None


