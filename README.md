# RhinoMeshTools

Tools for importing and processing mesh files from the command line using Rhino. Can also be used as a regular python package.

## ✅ Pre-requisites

1.  Rhino 8 needs to be installed at `C:\Program Files\Rhino 8\System\Rhino.exe`
2.  Python 3.x
3.  Your Python Scripts directory (e.g., `Python\Python3xx\Scripts`) needs to be in the `PATH` environment variable. The installer attempts to help with this.

## 📦 Installation

To get started, we recommend creating a dedicated virtual environment using Python's built-in `venv` module to manage the package and its dependencies.

1.  **Download or clone this repository.**
2.  **Extract the folder** (if zipped).
3.  **Open a terminal or PowerShell window** inside the root folder of the repository (the one containing `setup.py`).
4.  **Create a Python virtual environment** (e.g., named `my_package_env`):

    ```bash
    python -m venv my_package_env
    ```

5.  **Activate the new virtual environment:**

    * **On Windows:**
        ```bash
        .\my_package_env\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source my_package_env/bin/activate
        ```

6.  **Install the package and its dependencies** into the activated environment (don't forget the dot **.**):

    ```bash
    pip install .
    ```



## 🚀 Usage

Once installed, the command-line tools can be run from anywhere in your terminal. The package can also be imported and used in your Python scripts.

**Important Note:** Most functionalities of this package require Rhino to be running, as they automate Rhino commands. The scripts are designed to launch Rhino if it's not already running when a command-line tool is invoked or when a Python script using this package is run outside of Rhino.

### 📖 Command-line commands

#### 1. `mesh2cad`

This command launches Rhino and converts the given mesh file(s) to a CAD format using the full pipeline.

**Usage:**

```bash
mesh2cad --input <input_file_or_folder_path> [--output <output_folder_path>] [other options...]
```

**Arguments:**
*   `--input <path>`: Path to the input file or folder. Defaults to the current folder if not given. If a folder is given, all files in that folder will be processed.
*   `--output <path>`: Output folder. Defaults to the input folder (if input is a file) or the current folder (if input is a folder and output is not specified). This **must always be a folder path**, not a file path. Results will be saved in a "results" subfolder within this path.
*   `--nopreprocessing`: Turns off preprocessing. If not stated, preprocessing is enabled by default.
*   `--preprocessing <type>`: Type of preprocessing. Choose between `'shrinkwrap'`, `'fixholes'`, or `'fixshell'`. Defaults to `'shrinkwrap'`. This option is ignored if `--nopreprocessing` is used.
*   `--nosubd`: Turns off the SubD to NURBS conversion pathway. If not stated, subdivision (QuadRemesh -> SubD -> NURBS) is enabled by default. If `--nosubd` is used, the pathway will be QuadRemesh -> ToNURBS.
*   `--quadremeshlength <mm>`: Sets the target edge length for the QuadRemesh function in millimeters. Defaults to `2`mm.
*   `--shrinkwraplength <mm>`: Sets the target edge length for the ShrinkWrap function in millimeters (if `'shrinkwrap'` is the selected preprocessing type). Defaults to `1`mm. This option is ignored if a different preprocessing type is selected or if `--nopreprocessing` is used.
*   `--filetype <type>`: File type of the output CAD model. Defaults to `'igs'`. Can also be `'iges'`, `'stp'`, or `'step'`.
*   `--heatmap`: If stated, generates a heatmap visualization of the distances between the preprocessed mesh (or original if no preprocessing) and the final CAD model. The heatmap image (PNG) and data (PLY) are saved in the output folder. If not stated, no heatmap will be created.
*   `--savedistances`: If stated, calculates Chamfer and Hausdorff distances between the preprocessed mesh (or original if no preprocessing) and the final CAD model. The distances are stored in a CSV file in the output folder.

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
fix-mesh [--input <path>] [--output <path>] [--preprocessing <type>]
```

**Arguments:**

*   `--input <path>`: Path to the input file or folder. Defaults to the current folder if not given.
*   `--output <path>`: Output folder. Defaults to the current folder if not given. This **must always be a folder path**, not a file path. File(s) will be saved with the extension of the input file.
*   `--preprocessing <type>`: Type of preprocessing. Choose between `'shrinkwrap'`, `'fixholes'`, or `'fixshell'`. Defaults to `'shrinkwrap'`.

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

#### Available Functions:

The following functions are available when you import `rhinoMeshTools`:

*   **`importFile(inputPath)`**:
    *   Imports a mesh file into Rhino.
    *   `inputPath`: Path to the file.
    *   Returns: Rhino object ID of the imported mesh.

*   **`PreProcessing(mesh, outputPath, fileName, preProcessing='shrinkwrap', outputType='igs', resolution=1, smoothing=0, deleteInput=True, saveOutput=False)`**:
    *   Performs pre-processing on a mesh.
    *   `mesh`: Rhino object ID of the mesh to process.
    *   `outputPath`: Directory to save the processed mesh.
    *   `fileName`: Name for the output file (without extension).
    *   `preProcessing`: Type of preprocessing ('shrinkwrap', 'fixholes', 'fixshell').
    *   `outputType`: File type for saving (e.g., 'igs', 'stl').
    *   `resolution`: Resolution for shrinkwrap.
    *   `smoothing`: Smoothing value for shrinkwrap.
    *   `deleteInput`: Boolean, whether to delete the input Rhino object after processing.
    *   `saveOutput`: Boolean, whether to save the processed mesh.
    *   Returns: Rhino object ID of the processed mesh.

*   **`stl2cad(mesh, targetEdgeLength=2, adaptiveSize=100, deleteInputs=True)`**:
    *   Converts a mesh (typically after pre-processing) to a CAD model (NURBS).
    *   `mesh`: Rhino object ID of the mesh.
    *   `targetEdgeLength`: Target edge length for QuadRemesh.
    *   `adaptiveSize`: Adaptive size percentage for QuadRemesh.
    *   `deleteInputs`: Boolean, whether to delete intermediate objects (like the QuadRemesh result).
    *   Returns: Rhino object ID of the final NURBS model, or `None` if failed.

*   **`fullPipeline(inputFile, preProcess=True, edgePreProcessing=1, edgeConversion=2, smoothing=0, saveOutput=True)`**:
    *   Runs the full pipeline: import -> (optional) pre-process -> convert to CAD -> (optional) export.
    *   `inputFile`: Path to the input STL/mesh file.
    *   `preProcess`: Boolean, whether to perform pre-processing.
    *   `edgePreProcessing`: Resolution for shrinkwrap if `preProcess` is True.
    *   `edgeConversion`: Target edge length for QuadRemesh.
    *   `smoothing`: Smoothing for shrinkwrap.
    *   `saveOutput`: Boolean, whether to save the final CAD model as IGS.
    *   Returns: Tuple of (originalMesh ID, shrinkWrappedMesh ID or None, cad_model ID or None).

*   **`fullPipelineBatch(inputPath, outputPath, preProcess=True, edgePreProcessing=1, edgeConversion=2, smoothing=0)`**:
    *   Runs the `fullPipeline` for all mesh files in a given input directory.
    *   `inputPath`: Directory containing input mesh files.
    *   `outputPath`: Directory to save output IGS files.
    *   Other parameters are similar to `fullPipeline`.

*   **`meshDistanceCalculator(mesh1, mesh2)`**:
    *   Calculates distances from faces of `mesh2` to `mesh1` along normals.
    *   `mesh1`, `mesh2`: Rhino object IDs of the meshes.
    *   Prints average, max, min error, and number of no intersections.
    *   Returns: List of distance values (or `None` for no intersection).

*   **`chamferDistance(mesh1, mesh2, quads=True)`**:
    *   Calculates Chamfer distance and Hausdorff distance between two meshes.
    *   `mesh1`, `mesh2`: Rhino object IDs of the meshes.
    *   `quads`: Boolean, set based on whether meshes are quad or tri.
    *   Returns: List `[chamfer_distance, hausdorff_distance]` or `[None, None]` if inputs are invalid.

*   **`heatmap(inputPath, outputPath, edgeConversion=2, quads=True)`**:
    *   Generates a heatmap visualization of the distance between an original (shrinkwrapped) mesh and its NURBS conversion.
    *   `inputPath`: Path to the original input mesh file.
    *   `outputPath`: Directory to save heatmap image and PLY data.
    *   `edgeConversion`: Target edge length used for the `stl2cad` conversion step.
    *   `quads`: Boolean, indicates if the meshes for distance calculation are primarily quads or triangles.
    *   Saves a PNG screenshot and a PLY file with vertex color data.

*   **`deleteNonsense()`**:
    *   Prompts the user in Rhino to select a mesh they want to keep. All other objects are then deleted.
    *   Useful for cleaning up the Rhino document.
