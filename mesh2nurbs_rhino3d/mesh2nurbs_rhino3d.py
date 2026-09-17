#! python3

import os
import subprocess
import argparse

PREPROCESSING_STEPS = ["shrinkwrap", "fixholes", "remove-isolated-islands"]


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
        nargs="+",
        choices=["iges", "step"],
        default=["iges"],
        help="One or more filetypes of the output CAD file (e.g. '--output-filetype iges step' saves both). Defaults to 'iges'.",
    )
    parser.add_argument(
        "--preprocessing-steps",
        type=str,
        nargs="+",
        choices=["none"] + PREPROCESSING_STEPS,
        default=["none"],
        help="One or more preprocessing steps, applied in the given order (e.g. '--preprocessing-steps remove-isolated-islands fixholes shrinkwrap'). Does nothing if set to 'none'.",
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
    preprocessing_steps = [step for step in args.preprocessing_steps if step != "none"]
    if preprocessing_steps and len(preprocessing_steps) != len(args.preprocessing_steps):
        parser.error("'none' cannot be combined with other preprocessing steps.")

    # Set environment variable for any args
    os.environ["INPUT_PATH"] = os.path.abspath(args.input_path)
    os.environ["OUTPUT_FILETYPES"] = ",".join(dict.fromkeys(args.output_filetype))
    os.environ["PREPROCESSING_STEPS"] = ",".join(preprocessing_steps) if preprocessing_steps else "none"
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
    output_filetypes = os.environ.get("OUTPUT_FILETYPES").split(",")
    preprocessing_steps = [step for step in os.environ.get("PREPROCESSING_STEPS").split(",") if step and step != "none"]
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
        output_paths = [os.path.abspath(os.path.splitext(input_path)[0] + "." + ft) for ft in output_filetypes]
        print(f"Processing single file: {input_path} -> {', '.join(output_paths)}")
        mesh2nurbs(
            input_path,
            output_paths,
            preprocessing_steps=preprocessing_steps,
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
                output_paths = [os.path.abspath(os.path.splitext(file)[0] + "." + ft) for ft in output_filetypes]
                mesh2nurbs(
                    file,
                    output_paths,
                    preprocessing_steps=preprocessing_steps,
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
    preprocessing_steps=("shrinkwrap",),
    shrinkwrap_length=1.0,
    smoothing=0.0,
):
    """
    Performs a chain of pre-processing operations on the mesh in the active Rhino document.
    The steps are applied in the given order, each one operating on the result of the previous step.
    Afterwards, the document contains only the resulting mesh, which is selected.

    Args:
        preprocessing_steps (str or list of str): Pre-processing step(s) to apply in order.
            Options: 'shrinkwrap', 'fixholes', 'remove-isolated-islands'.
        shrinkwrap_length (float): Resolution for shrinkwrap pre-processing. Only used by the 'shrinkwrap' step.
        smoothing (float): Smoothing iterations for pre-processing. Only used by the 'shrinkwrap' step.
    """
    if isinstance(preprocessing_steps, str):
        preprocessing_steps = [preprocessing_steps]

    invalid_steps = [step for step in preprocessing_steps if step not in PREPROCESSING_STEPS]
    if invalid_steps:
        raise ValueError(f"Wrong preprocessing_steps given: {invalid_steps}. Choose from {PREPROCESSING_STEPS}")

    steps = {
        "shrinkwrap": lambda: preprocess_shrinkwrap(shrinkwrap_length=shrinkwrap_length, smoothing=smoothing),
        "fixholes": preprocess_fixholes,
        "remove-isolated-islands": preprocess_remove_isolated_islands,
    }
    for i, step in enumerate(preprocessing_steps, start=1):
        print(f"Preprocessing step {i}/{len(preprocessing_steps)}: {step}")
        steps[step]()


def preprocess_shrinkwrap(shrinkwrap_length=1.0, smoothing=0.0):
    """
    Replaces the mesh with a watertight shrink-wrapped version of it.
    """
    import rhinoscriptsyntax as rs

    rs.Command("_-SelAll Enter")
    rs.Command(
        f"_-ShrinkWrap Resolution={shrinkwrap_length} Offset=0 Smooth={smoothing} PolygonOptimize=0 FillHoles=On VertexColors=Off DeleteInput=On Preview=Off DrawWires=On HideInput=Off Enter"
    )
    rs.Command("_SelLast Enter")
    rs.Command("_Invert Enter")
    rs.Command("_Delete Enter")
    rs.Command("_-SelAll Enter")


def preprocess_fixholes():
    """
    Fills all holes of the mesh.
    """
    import rhinoscriptsyntax as rs

    rs.Command("_-SelAll Enter")
    rs.Command("_-FillMeshHoles Enter")
    rs.Command("_-SelAll Enter")


def preprocess_remove_isolated_islands():
    """
    Keeps only the largest connected mesh (island) and removes everything else.

    All mesh objects in the document are combined into one mesh, which is split into its connected pieces
    (the same connectivity Rhino's SplitDisjointMesh uses). The piece with the largest surface area is kept;
    all other pieces and objects are deleted.
    """
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

    mesh_ids = rs.ObjectsByType(rs.filter.mesh) or []
    if not mesh_ids:
        raise RuntimeError("remove-isolated-islands: no mesh found in the document.")

    combined = Rhino.Geometry.Mesh()
    for mesh_id in mesh_ids:
        combined.Append(rs.coercemesh(mesh_id))

    pieces = list(combined.SplitDisjointPieces() or []) or [combined]

    def mesh_area(mesh):
        props = Rhino.Geometry.AreaMassProperties.Compute(mesh)
        return props.Area if props else 0.0

    largest = max(pieces, key=mesh_area)
    largest.Compact()
    largest.Normals.ComputeNormals()
    print(f"remove-isolated-islands: found {len(pieces)} island(s), keeping the largest one.")

    # Put the largest island into the first mesh object and delete everything else
    rs.Command("_-SelAll Enter")
    rs.UnselectObject(mesh_ids[0])
    rs.Command("_Delete Enter")
    sc.doc.Objects.Replace(mesh_ids[0], largest)
    rs.Command("_-SelAll Enter")
    sc.doc.Views.Redraw()


def mesh2nurbs(
    input_path: str,
    output_path,
    preprocessing_steps="none",
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
        output_path (str or list of str): Path(s) to the output NURBS file(s) ending in '.iges' or '.step'.
            The result is exported once per given path.
        preprocessing_steps (str or list of str, optional): Pre-processing step(s) to apply in order. Options: 'none',
            'shrinkwrap', 'fixholes', 'remove-isolated-islands'. Defaults to 'none'.
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

    # Step 2: Apply the chain of pre-processing steps if specified
    keep_last()
    if isinstance(preprocessing_steps, str):
        preprocessing_steps = [preprocessing_steps]
    preprocessing_steps = [step for step in preprocessing_steps if step != "none"]
    if preprocessing_steps:
        preprocess(
            preprocessing_steps=preprocessing_steps,
            shrinkwrap_length=shrinkwrap_length,
            smoothing=smoothing,
        )
        # every preprocessing step leaves only the resulting mesh selected
        keep_selected()
    else:
        keep_last()

    # Step 3: Convert the mesh to Quadmesh and perform SubD if specified
    rs.Command(f"_-QuadRemesh TargetEdgeLength={quadremesh_length} DetectEdges=On ToSubD={'On' if subd else 'Off'} Enter")

    # Step 4: Convert NURBS
    keep_last()
    if subd:  # packed patches is available when subd is used
        if packed_patches:
            rs.Command("_-ToNurbs DeleteInputObjects=Yes SubDOptions Faces=Packed Enter Enter")
        else:
            rs.Command("_-ToNurbs DeleteInputObjects=Yes SubDOptions Faces=Unpacked Enter Enter")

    else:  # packed patches is not available when subd is not used
        rs.Command("_-ToNurbs DeleteInputObjects=Yes Enter")

    # Step 5: Rebuild NURBS if force_ncps_u or force_ncps_v is specified
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

    # Step 6: Export the final NURBS object to the specified output path(s)
    output_paths = [output_path] if isinstance(output_path, str) else output_path
    for path in output_paths:
        keep_last()
        rs.Command(
            f'_-Export _Version=8 _SaveSmall=No _GeometryOnly=Yes _SaveTextures=No _SaveNotes=No _SavePlugInData=No "{path}" _Enter _Enter'
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


def keep_selected():
    """
    Keep only the currently selected objects in the Rhino document, deleting all others.
    """
    import rhinoscriptsyntax as rs

    rs.Command("_Invert Enter")
    rs.Command("_Delete Enter")
    rs.Command("_-SelAll Enter")


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
