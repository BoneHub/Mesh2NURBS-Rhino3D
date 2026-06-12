# RhinoMeshTools

Tools for importing and processing mesh files from the command line using Rhino. Can also be used as a regular python package.

## ✅ Requirements

1.  Rhino 8 needs to be installed and able to be executed from `C:\Program Files\Rhino 8\System\Rhino.exe`
2.  Python 3.x

## Installation

To get started, we recommend creating a dedicated virtual environment using Python's built-in `venv` module to manage the package and its dependencies.


1.  **Create a conda environment**:

    ```bash
    conda create -n mesh2nurbs-rhino-env python==3.10
    ```

2.  **Activate the environment:**
    ```bash
    conda activate mesh2nurbs-rhino-env
    ```


3.  **Clone this repository**:
    ```bash
    git clone https://github.com/BoneHub/mesh2nurbs-rhino3d.git
    ```

4. **Install the package**:
    ```bash
    cd mesh2nurbs-rhino3d
    pip install -e .
    ```


## 🚀 Usage

### 📖 Command-line

**Note**: The previously create conda environment must be activated first.

#### 1. `mesh2cad`

This command launches Rhino and converts the given mesh file(s) to a CAD format using the full pipeline.

**Usage:**

```bash
mesh2cad --input <input_file_or_folder_path> --output <output_folder_path> [other options...]
```

**Options:**
*   `--input <path>`: Path to the input file or folder. Defaults to the current folder if not given. If a folder is given, all files in that folder will be processed.
*   `--output <path>`: Output folder. Defaults to the input folder (if input is a file) or the current folder (if input is a folder and output is not specified). This **must always be a folder path**, not a file path. Results will be saved in a "results" subfolder within this path.
*   `--nopreprocessing`: Turns off preprocessing. If not stated, preprocessing is enabled by default.
*   `--preprocessing <type>`: Type of preprocessing. Choose between `'shrinkwrap'`, `'fixholes'`, or `'fixshell'`. Defaults to `'shrinkwrap'`. This option is ignored if `--nopreprocessing` is used.
*   `--nosubd`: Turns off the SubD to NURBS conversion pathway. If not stated, subdivision (QuadRemesh -> SubD -> NURBS) is enabled by default. If `--nosubd` is used, the pathway will be QuadRemesh -> ToNURBS.
*   `--subdtype <type>`: Sets the type of SubD to NURBS conversion. `'1'` (default) attempts to merge faces, `'2'` may result in more individual faces (uses RhinoCommon).
*   `--quadremeshlength <mm>`: Sets the target edge length for the QuadRemesh function in millimeters. Defaults to `2`mm.
*   `--shrinkwraplength <mm>`: Sets the target edge length for the ShrinkWrap function in millimeters (if `'shrinkwrap'` is the selected preprocessing type). Defaults to `1`mm. This option is ignored if a different preprocessing type is selected or if `--nopreprocessing` is used.
*   `--filetype <type>`: File type of the output CAD model. Defaults to `'igs'`. Can also be `'iges'`, `'stp'`, or `'step'`.
*   `--heatmap`: If stated, generates a heatmap visualization of the distances between the preprocessed mesh (or original if no preprocessing) and the final CAD model. The heatmap image (PNG) and data (PLY) are saved in the output folder. If not stated, no heatmap will be created.
*   `--savedistances`: If stated, calculates Chamfer and Hausdorff distances between the preprocessed mesh (or original if no preprocessing) and the final CAD model. The distances are stored in a CSV file in the output folder.
*   `--keepopen`: If stated, keeps Rhino open after the process is done. Without this flag, Rhino is closed automatically.

**Example:**

```bash
mesh2cad --input "C:\Path\To\Your\meshfile.ply" --output "C:\Path\To\OutputFolder" --filetype igs
```

This will:

1.  Launch Rhino (if not already running).
2.  Import the specified `.ply` file.
3.  Run the full conversion pipeline.
4.  Save the result in the output folder.

You can also use `--help` to see all arguments:
```bash
mesh2cad --help
```

#### 2. `fix-mesh`

This command launches Rhino and performs pre-processing on a specified mesh file or all mesh files in a folder.

**Usage:**

```bash
fix-mesh --input <path> --output <path> --preprocessing <type>
```

**Arguments:**

*   `--input <path>`: Path to the input file or folder. Defaults to the current folder if not given.
*   `--output <path>`: Output folder. Defaults to the current folder if not given. This **must always be a folder path**, not a file path. File(s) will be saved with the extension of the input file in a "results" subfolder.
*   `--preprocessing <type>`: Type of preprocessing. Choose between `'shrinkwrap'`, `'fixholes'`, or `'fixshell'`. Defaults to `'shrinkwrap'`.
*   `--smoothing <value>`: Sets the smoothing value for the ShrinkWrap function (if `'shrinkwrap'` is the selected preprocessing type). Defaults to `0`. It is advised to keep this at its default unless the input mesh has a blocky surface, as increasing it can lower accuracy.
*   `--edgelength <mm>`: Sets the target edge length for the ShrinkWrap function in millimeters (if `'shrinkwrap'` is the selected preprocessing type). Defaults to `1`mm.
*   `--keepopen`: If stated, keeps Rhino open after the process is done. Without this flag, Rhino is closed automatically.

**Examples:**

*   Pre-process a single file using shrinkwrap and save to a specific output folder:
    ```bash
    fix-mesh --input "C:\Path\To\Your\meshfile.stl" --output "C:\Path\To\OutputFolder" --preprocessing shrinkwrap
    ```
*   Pre-process all files in the current directory using default shrinkwrap and save to `D:\ProcessedMeshes`:
    ```bash
    fix-mesh --output "D:\ProcessedMeshes"
    ```

You can also use `--help` to see all arguments and their descriptions:
```bash
fix-mesh --help
```

### 🐍 As Python code

You can import and use the functionalities directly in your Python scripts. If the script is run outside of Rhino, it will attempt to launch Rhino.
Functions are available from the `rhinoMeshTools.tools` module.

#### Available Functions:

The following functions are available from `rhinoMeshTools.tools`:

*   **`importFile(inputPath)`**:
    *   Imports a mesh file into Rhino.
    *   `inputPath`: Path to the file.
    *   Returns: Rhino object ID of the imported mesh.

*   **`PreProcessing(mesh, outputPath, fileName=None, preProcessing='shrinkwrap', outputType='igs', resolution=1, smoothing=0, deleteInput=True, saveOutput=False)`**:
    *   Performs pre-processing operations on a mesh object.
    *   `mesh`: The input mesh object.
    *   `outputPath`: The directory to save the output file.
    *   `fileName (str, optional)`: Name of the output file. Defaults to None.
    *   `preProcessing (str, optional)`: Type of pre-processing. Options: 'shrinkwrap', 'fixholes', 'fixshell'. Defaults to 'shrinkwrap'.
    *   `outputType (str, optional)`: File type for the output. Defaults to 'igs'.
    *   `resolution (int, optional)`: Resolution for shrinkwrap. Defaults to 1.
    *   `smoothing (int, optional)`: Smoothing iterations for shrinkwrap. Defaults to 0.
    *   `deleteInput (bool, optional)`: Whether to delete the input mesh after processing. Defaults to True.
    *   `saveOutput (bool, optional)`: Whether to save the processed mesh. Defaults to False.
    *   Returns: The processed mesh object, or `None` if processing fails.

*   **`exportMesh(mesh, outputPath, fileType, fileName)`**:
    *   Exports a mesh object to a specified file type.
    *   `mesh`: The mesh object to export.
    *   `outputPath`: The directory to save the exported file.
    *   `fileType (str)`: The desired file type (e.g., 'igs', 'step').
    *   `fileName (str)`: The name for the exported file.

*   **`stl2cad(mesh, targetEdgeLength=2, adaptiveSize=100, deleteInputs=True, subd=True, type='1')`**:
    *   Converts an STL-like mesh to a CAD format (NURBS or SubD).
    *   `mesh`: The input mesh object.
    *   `targetEdgeLength (int, optional)`: Target edge length for QuadRemesh. Defaults to 2.
    *   `adaptiveSize (int, optional)`: Adaptive size percentage for QuadRemesh. Defaults to 100.
    *   `deleteInputs (bool, optional)`: Whether to delete intermediate objects. Defaults to True.
    *   `subd (bool, optional)`: If True, converts to SubD then NURBS. If False, directly to NURBS from QuadRemesh. Defaults to True.
    *   `type (str, optional)`: Specifies the SubD to NURBS conversion method. '1' uses `subd_to_nurbs`, '2' uses `subd_to_nurbs_many_faces`. Defaults to '1'.
    *   Returns: The converted CAD object (NURBS or SubD), or `None` if conversion fails.

*   **`fullPipeline(mesh, inputPath, outputPath, prep, preProcess=True, edgePreProcessing=1, edgeConversion=2, smoothing=0, heat=False, subd=True, type='1')`**:
    *   Processes a single mesh through pre-processing and CAD conversion.
    *   `mesh`: The input mesh object.
    *   `inputPath (str)`: Path of the input file (used for naming in heatmap).
    *   `outputPath (str)`: Path to the directory for potential outputs.
    *   `prep (str)`: The type of pre-processing to apply (e.g., 'shrinkwrap').
    *   `preProcess (bool, optional)`: Whether to perform pre-processing. Defaults to True.
    *   `edgePreProcessing (int, optional)`: Resolution for pre-processing. Defaults to 1.
    *   `edgeConversion (int, optional)`: Target edge length for stl2cad conversion. Defaults to 2.
    *   `smoothing (int, optional)`: Smoothing iterations for pre-processing. Defaults to 0.
    *   `heat (bool, optional)`: Placeholder for heatmap generation. Defaults to False.
    *   `subd (bool, optional)`: Whether to use SubD in the stl2cad conversion. Defaults to True.
    *   `type (str, optional)`: SubD to NURBS conversion type for `stl2cad`. Defaults to '1'.
    *   Returns: Tuple of (originalMesh ID, shrinkWrappedMesh ID or None, cad_model ID or None).

*   **`fullPipelineBatch(inputPath, outputPath, preProcess=True, edgePreProcessing=1, edgeConversion=2, smoothing=0)`**:
    *   Processes a batch of STL files from an input directory, converts them to CAD, and saves them.
    *   `inputPath (str)`: Path to the directory containing input STL files.
    *   `outputPath (str)`: Path to the directory to save output IGS files.
    *   `preProcess (bool, optional)`: Whether to perform pre-processing. Defaults to True.
    *   `edgePreProcessing (int, optional)`: Resolution for pre-processing (e.g., ShrinkWrap). Defaults to 1.
    *   `edgeConversion (int, optional)`: Target edge length for stl2cad conversion. Defaults to 2.
    *   `smoothing (int, optional)`: Smoothing iterations for pre-processing. Defaults to 0.

*   **`meshDistanceCalculator(mesh1, mesh2)`**:
    *   Calculates the distance between two meshes by ray casting from faces of `mesh2` to `mesh1`.
    *   `mesh1`: The first mesh object (target for ray casting).
    *   `mesh2`: The second mesh object (source of rays from face centers).
    *   Returns: List of distances for each face center of `mesh2` that intersected `mesh1`. `None` is appended if no intersection or intersection is beyond cutoff.

*   **`chamferDistance(mesh1, mesh2, quads=True)`**:
    *   Calculates Chamfer and Hausdorff distances between two meshes.
    *   `mesh1`: The first mesh object.
    *   `mesh2`: The second mesh object.
    *   `quads (bool, optional)`: Indicates if the meshes are primarily quads. This affects how face vertices are extracted. Defaults to True.
    *   Returns: List `[chamfer_distance, hausdorff_distance]` or `[None, None]` if input meshes are invalid.

*   **`heatmap(mesh1, mesh2, inputPath, outputPath, plyPath, edgeConversion=2, quads=True, filename=None)`**:
    *   Generates a heatmap visualization of the distance between two meshes. Saves a 2D screenshot and a 3D PLY file.
    *   `mesh1`: The first mesh object (e.g., shrink-wrapped mesh, points for coloring).
    *   `mesh2`: The second mesh object (e.g., NURBS mesh, reference for distance calculation).
    *   `inputPath (str)`: Path of the original input file (used for naming outputs if `filename` is None).
    *   `outputPath (str)`: Directory to save the 2D heatmap image (PNG).
    *   `plyPath (str)`: Directory to save the 3D PLY heatmap data.
    *   `edgeConversion (int, optional)`: Edge conversion value, used for output naming. Defaults to 2.
    *   `quads (bool, optional)`: Indicates if meshes are primarily quads for face extraction. Defaults to True.
    *   `filename (str, optional)`: Custom filename for outputs. If None, derived from `inputPath`. Defaults to None.

*   **`deleteNonsense()`**:
    *   Prompts the user in Rhino to select a mesh they want to keep. All other objects are then deleted.
    *   Useful for cleaning up the Rhino document.

*   **`mesh_to_subd(mesh_id)`**:
    *   Convert a mesh to SubD and return the SubD object ID.
    *   `mesh_id`: Rhino object ID of the mesh.
    *   Returns: object ID of the SubD, or `None` if failed.

*   **`subd_to_nurbs(subd_id)`**:
    *   Convert a SubD object to NURBS using `rs.Command` and return the NURBS object ID.
    *   `subd_id`: Rhino object ID of the SubD.
    *   Returns: object ID of the NURBS, or `None` if failed.

*   **`subd_to_nurbs_many_faces(subd_id)`**:
    *   Convert a SubD object to NURBS using RhinoCommon and return the NURBS object ID.
    *   `subd_id`: Rhino object ID of the SubD.
    *   Returns: object ID of the NURBS, or `None` if failed.
