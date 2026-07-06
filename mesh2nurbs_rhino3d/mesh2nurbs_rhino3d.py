#! python3

import os
import subprocess
import argparse


def start_rhino():

    parser = argparse.ArgumentParser(
        description="Launches Rhino and converts the given mesh file(s) to a CAD format. All options below are optional, the command works as long as the current working directory only contains mesh files"
    )
    parser.add_argument(
        "-i",
        "--input-path",
        required=True,
        type=str,
        default=os.path.abspath(os.getcwd()),
        help="Path to the input file or folder, defaults to current folder if not given, If folder is given, all files in that folder will be processed.",
    )
    parser.add_argument(
        "--output-filetype",
        type=str,
        choices=["iges", "step"],
        default="iges",
        help="Filetype of the output CAD file. Defaults to 'iges'.",
    )
    parser.add_argument(
        "--preprocessing-type",
        type=str,
        choices=["none", "shrinkwrap", "fixholes", "fixshell"],
        default="none",
        help="Type of preprocessing. Does nothing if set to 'none'.",
    )
    parser.add_argument(
        "--smoothing",
        type=float,
        default=0.0,
        help="Sets the smoothing of the shrinkwrap function. Does nothing if set to 0.0. Also does nothing if '--preprocessing' is set to 'none'. It is advised to keep this at its default unless the input mesh has a blocky surface, since this lower the accuracy of the process.",
    )
    parser.add_argument(
        "--nosubd",
        action="store_true",
        help="if stated, the subd operation will be skipped, resulting in non-smooth NURBS connection of the NURBS patches.",
    )
    parser.add_argument(
        "--packed-patches",
        action="store_true",
        help="if stated, the NURBS patches will be packed together. Only works when SubD is enabled, meaning '--nosubd' is not stated.",
    )
    parser.add_argument(
        "--force-ncps-u",
        type=int,
        default=0,
        help="Sets the number of control points in the U direction for the rebuild operation. Setting this to 0 allows Rhino3D to automatically decide the value for each patch individually.",
    )
    parser.add_argument(
        "--force-ncps-v",
        type=int,
        default=0,
        help="Sets the number of control points in the V direction for the rebuild operation. Setting this to 0 allows Rhino3D to automatically decide the value for each patch individually.",
    )
    parser.add_argument(
        "--quadremesh-length",
        type=float,
        default=2.0,
        help="Sets the target edge length of the quad-remesh function in millimeters. Defaults to 2mm",
    )
    parser.add_argument(
        "--shrinkwrap-length",
        type=float,
        default=1.0,
        help="Sets the target edge length of the shrinkwrap function in millimeters. Defaults to 1mm and does nothing if a different type of preprocessing is selected.",
    )
    parser.add_argument(
        "--rhino-path",
        type=str,
        default="C:\\Program Files\\Rhino 8\\System\\Rhino.exe",
        help="Path to the Rhino executable. Defaults to 'C:\\Program Files\\Rhino 8\\System\\Rhino.exe'.",
    )
    parser.add_argument(
        "--keep-open",
        action="store_true",
        help="if stated, the Rhino application will remain open after the process is complete.",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="if stated, the Rhino application will not be displayed during the process. This can reduce the processing time.",
    )

    args = parser.parse_args()
    # Set environment variable for any args
    os.environ["INPUT_PATH"] = os.path.abspath(args.input_path)
    os.environ["OUTPUT_FILETYPE"] = args.output_filetype
    os.environ["PREPROCESSING_TYPE"] = args.preprocessing_type
    os.environ["SMOOTHING"] = str(args.smoothing)
    os.environ["NOSUBD"] = str(args.nosubd)
    os.environ["PACKED_PATCHES"] = str(args.packed_patches)
    os.environ["FORCE_NCPS_U"] = str(args.force_ncps_u)
    os.environ["FORCE_NCPS_V"] = str(args.force_ncps_v)
    os.environ["QUADREMESH_LENGTH"] = str(args.quadremesh_length)
    os.environ["SHRINKWRAP_LENGTH"] = str(args.shrinkwrap_length)
    os.environ["KEEP_OPEN"] = str(args.keep_open)
    os.environ["NO_DISPLAY"] = str(args.no_display)

    # Launch Rhino and run script
    command = f'"{args.rhino_path}" /nosplash /runscript="_-RunPythonScript ({os.path.abspath(__file__)})"'
    subprocess.run(command)


def main():

    # Disable view redraw to improve performance during processing
    if os.environ.get("NO_DISPLAY") == "True":
        import scriptcontext
        scriptcontext.doc.Views.RedrawEnabled = False

    # Retrieve args from environment variables
    input_path = os.environ.get("INPUT_PATH")
    output_filetype = os.environ.get("OUTPUT_FILETYPE")
    preprocessing_type = os.environ.get("PREPROCESSING_TYPE")
    smoothing = float(os.environ.get("SMOOTHING"))
    nosubd = os.environ.get("NOSUBD") == "True"
    packed_patches = os.environ.get("PACKED_PATCHES") == "True"
    force_ncps_u = int(os.environ.get("FORCE_NCPS_U"))
    force_ncps_v = int(os.environ.get("FORCE_NCPS_V"))
    quadremesh_length = float(os.environ.get("QUADREMESH_LENGTH"))
    shrinkwrap_length = float(os.environ.get("SHRINKWRAP_LENGTH"))
    keep_open = os.environ.get("KEEP_OPEN") == "True"

    if os.path.isfile(input_path):
        # Single file mode
        output_path = os.path.abspath(os.path.splitext(input_path)[0] + "." + output_filetype)
        print(f"Processing single file: {input_path} -> {output_path}")
        mesh2nurbs(
            input_path,
            output_path,
            preprocessing_type=preprocessing_type,
            smoothing=smoothing,
            subd=not nosubd,
            packed_patches=packed_patches,
            force_ncps_u=force_ncps_u,
            force_ncps_v=force_ncps_v,
            quadremesh_length=quadremesh_length,
            shrinkwrap_length=shrinkwrap_length,
        )

    elif os.path.isdir(input_path):
        # Batch mode
        for file_name in os.listdir(input_path):
            file = os.path.join(input_path, file_name)
            if os.path.isfile(file) and os.path.splitext(file)[1].lower() in [".stl", ".obj", ".ply"]:
                output_path = os.path.abspath(os.path.splitext(file)[0] + "." + output_filetype)
                mesh2nurbs(
                    file,
                    output_path,
                    preprocessing_type=preprocessing_type,
                    smoothing=smoothing,
                    subd=not nosubd,
                    packed_patches=packed_patches,
                    force_ncps_u=force_ncps_u,
                    force_ncps_v=force_ncps_v,
                    quadremesh_length=quadremesh_length,
                    shrinkwrap_length=shrinkwrap_length,
                )
    if not keep_open:
        import rhinoscriptsyntax as rs
        rs.Command("_-Exit No")
        subprocess.run(["taskkill", "/F", "/IM", "Rhino.exe"], check=False)


def preprocess(
    preprocessing_type="shrinkwrap",
    shrinkwrap_length=1.0,
    smoothing=0.0,
):
    """
    Performs pre-processing operations on a mesh object.

    Args:
        preprocessing_type (str): Type of pre-processing to apply. Options: 'shrinkwrap', 'fixholes', 'fixshell'.
        shrinkwrap_length (float): Resolution for shrinkwrap pre-processing. Only used if preprocessing_type is 'shrinkwrap'.
        smoothing (float): Smoothing iterations for pre-processing. Only used if preprocessing_type is 'shrinkwrap'.
    """
    import rhinoscriptsyntax as rs

    rs.Command("_SelLast Enter")
    if preprocessing_type == "shrinkwrap":
        rs.Command(
            f"_-ShrinkWrap Resolution={shrinkwrap_length} Offset=0 Smooth={smoothing} PolygonOptimize=0 FillHoles=On VertexColors=Off DeleteInput=On Preview=Off DrawWires=On HideInput=Off Enter"
        )
        rs.Command("_SelLast Enter")
        rs.Command("_Invert Enter")
        rs.Command("_Delete Enter")
    elif preprocessing_type == "fixholes":
        rs.Command("_-FillMeshHoles Enter")
        rs.Command("_-SelAll Enter")
    elif preprocessing_type == "fixshell":
        rs.Command("_-SelAll Enter")
        rs.Command("_-SplitDisjointMesh Enter")
        rs.Command("_-SelAll Enter")
        allMeshes = rs.SelectedObjects()
        area = []
        for mesh in allMeshes:
            area.append(rs.MeshArea(mesh)[1])
        rs.UnselectAllObjects()
        rs.SelectObject(allMeshes[area.index(max(area))])
        rs.Command("_-Invert Enter")
        rs.Command("_-Delete Enter")
        rs.Command("_-SelAll Enter")
    else:
        raise ValueError("Wrong preprocessing_type given, choose between 'shrinkwrap', 'fixholes', or 'fixshell'")


def mesh2nurbs(
    input_path: str,
    output_path: str,
    preprocessing_type: str = "none",
    smoothing: float = 0.0,
    subd: bool = True,
    packed_patches: bool = False,
    force_ncps_u: int = 0,
    force_ncps_v: int = 0,
    quadremesh_length: float = 2.0,
    shrinkwrap_length: float = 1.0,
):
    """
    Processes a single mesh through pre-processing and CAD conversion.

    Args:
        input_path (str): Path to the input mesh file.
        output_path (str): Path to the output NURBS file ending in '.iges' or '.step'.
        preprocessing_type (str, optional): Type of pre-processing to apply. Options: 'shrinkwrap', 'fixholes', 'fixshell'. Defaults to 'none'.
        smoothing (float, optional): Smoothing iterations for pre-processing. Defaults to 0.0.
        subd (bool, optional): If True, converts to SubD then NURBS. If False, directly to NURBS from QuadRemesh. Defaults to True.
        packed_patches (bool, optional): If True, packs patches during conversion. Defaults to False.
        force_ncps_u (int, optional): Forces the number of control points in U direction.
        force_ncps_v (int, optional): Forces the number of control points in V direction.
        quadremesh_length (float, optional): Target edge length for QuadRemesh. Defaults to 2.0.
        shrinkwrap_length (float, optional): Resolution for shrinkwrap pre-processing. Defaults to 1.0.
    """

    import rhinoscriptsyntax as rs

    # Step 1: Import the mesh and apply pre-processing if specified
    rs.Command("_-New No None Enter")
    rs.Command(f'_-Import "{input_path}" Enter')

    # Step 2: Apply pre-processing if specified
    keep_last()
    if preprocessing_type != "none":
        preprocess(
            preprocessing_type=preprocessing_type,
            shrinkwrap_length=shrinkwrap_length,
            smoothing=smoothing,
        )

    # Step 2: Convert the mesh to Quadmesh and perform SubD if specified
    keep_last()
    rs.Command(f"_-QuadRemesh TargetEdgeLength={quadremesh_length} DetectEdges=On ToSubD={'On' if subd else 'Off'} Enter")

    # Step 3: Convert NURBS
    keep_last()
    if subd:  # packed patches is available when subd is used
        if packed_patches:
            rs.Command("_-ToNurbs DeleteInputObjects=Yes SubDOptions Faces=Packed Enter Enter")
        else:
            rs.Command("_-ToNurbs DeleteInputObjects=Yes SubDOptions Faces=Unpacked Enter Enter")

    else:  # packed patches is not available when subd is not used
        rs.Command("_-ToNurbs DeleteInputObjects=Yes Enter")

    # Step 4: Rebuild NURBS if force_ncps_u or force_ncps_v is specified
    if force_ncps_u and force_ncps_v:
        # ensure that the number of control points is greater than 3 to maintain the NURBS degree=3.
        if force_ncps_u > 3 and force_ncps_v > 3:
            keep_last()
            rs.Command(f"_-Explode Enter")
            rs.Command(f"_-SelAll Enter")
            rs.Command(
                f"_-Rebuild UPointCount={force_ncps_u} VPointCount={force_ncps_v} UDegree=3 VDegree=3 DeleteInput=Yes ReTrim=No Enter"
            )
            rs.Command(f"_-SelAll Enter")
            rs.Command(f"_-Join Enter")
        else:
            raise ValueError("force_ncps_u and force_ncps_v must be greater than 3 to maintain NURBS degree=3.")

    # Step 5: Export the final NURBS object to the specified output path
    keep_last()
    rs.Command(
        f'_-Export _Version=8 _SaveSmall=No _GeometryOnly=Yes _SaveTextures=No _SaveNotes=No _SavePlugInData=No "{output_path}" _Enter _Enter'
    )


def keep_last():
    """
    Keep only the last created object in the Rhino document, deleting all others.
    """
    import rhinoscriptsyntax as rs

    rs.Command("_SelLast Enter")
    rs.Command("_Invert Enter")
    rs.Command("_Delete Enter")
    rs.Command("_SelLast Enter")


def cli_entry_point():
    """
    Entry point for the script. Determines if Rhino is running and either runs the main function or starts Rhino.
    """
    rhino_is_running = True
    try:
        import rhinoscriptsyntax as rs
    except ImportError:
        rhino_is_running = False
    if rhino_is_running:
        main()
    else:
        start_rhino()


if __name__ == "__main__":
    cli_entry_point()
