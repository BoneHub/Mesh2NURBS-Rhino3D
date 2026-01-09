#! python3
# r: numpy
# r: vedo
# r: point_cloud_utils
# r: pandas
# r: matplotlib
# r: scipy

import sys
import os
import argparse


def main():

    # Show help without launching Rhino
    if "--help" in sys.argv or "-h" in sys.argv:
        parser = argparse.ArgumentParser(description="Launches Rhino and fixes the given mesh file(s) according to the options below. All options are optional, the command works as long as the current working directory only contains mesh files")
        parser.add_argument("--input", type=str, help="Path to the input file or folder, defaults to current folder if not given")
        parser.add_argument("--output", type=str, help="Output folder, defaults to current folder if not given. Needs to be a folder directory, not a file. File(s) will always be saved as the extension of the input file")
        parser.add_argument("--preprocessing", help="Type of preprocessing, either 'shrinkwrap', 'fixholes', or 'fixshell'. Defaults to 'shrinkwrap' (without apostrophes)")
        parser.add_argument("--smoothing", type=float, help="Sets the smoothing of the shrinkwrap function. It is advised to keep this at its default unless the input mesh has a blocky surface, since this lower the accuracy of the process.")
        parser.add_argument("--edgelength", type=float, help="Sets the target edge length of the shrinkwrap function. Defaults to 1 mm. ")
        parser.add_argument("--keepopen", action="store_true", help="If stated, keeps rhino open after the process is done. Without this flag, rhino is closed automatically.")
        parser.print_help()
        return

    # Launch rhino if not launched already
    if "Rhino.exe" not in sys.executable:
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", type=str, default=os.getcwd(), help="Path to the input file or folder, defaults to current folder if not given")
        parser.add_argument("--output", type=str, default=os.getcwd(), help="Output folder, defaults to current folder if not given. Needs to be a folder directory, not a file")
        parser.add_argument("--preprocessing", default="shrinkwrap", help="Type of preprocessing, either 'shrinkwrap', 'fixholes', or 'fixshell'. Defaults to 'shrinkwrap' (without apostrophes)")
        parser.add_argument(
            "--smoothing", type=float, default=0, help="Sets the smoothing of the shrinkwrap function. It is advised to keep this at its default unless the input mesh has a blocky surface, since this lower the accuracy of the process."
        )
        parser.add_argument("--edgelength", type=float, default=1, help="Sets the target edge length of the shrinkwrap function. Defaults to 1 mm. ")
        parser.add_argument("--keepopen", action="store_true", help="If stated, keeps rhino open after the process is done. Without this flag, rhino is closed automatically.")
        args, unknown = parser.parse_known_args()

        # Set environment variable for any args

        os.environ["INPUT_PATH"] = os.path.abspath(args.input)
        if not args.output:
            os.environ["OUTPUT_PATH"] = os.path.abspath(args.input).split(".")[0]
        else:
            os.environ["OUTPUT_PATH"] = args.output
        os.environ["PREPROCESS_TYPE"] = args.preprocessing
        os.environ["LENGTH"] = str(args.edgelength)
        os.environ["SMOOTH"] = str(args.smoothing)
        if args.keepopen:
            os.environ["KEEP"] = "True"
        else:
            os.environ["KEEP"] = "False"

        # Launch Rhino and run script
        scriptToRun = os.path.abspath(__file__)
        rhinoExePath = "C:\\Program Files\\Rhino 8\\System\\Rhino.exe"
        print("Launching Rhino...")
        command = f'"{rhinoExePath}" /nosplash /runscript="_-RunPythonScript ({scriptToRun})"'
        os.system(f'"{command}"')

        return

    # Retrieve args from environment variables
    inputPath = os.environ.get("INPUT_PATH")
    outputPath = os.environ.get("OUTPUT_PATH")
    preProcess = os.environ.get("PREPROCESS_TYPE")
    edgeLen = float(os.environ.get("LENGTH"))
    smooth = float(os.environ.get("SMOOTH"))
    keepOpen = os.environ.get("KEEP") == "True"

    # Execute main part of code
    import tools

    print(inputPath)
    if len(inputPath.split(".")) == 2:
        print("Single file mode")
        orgMesh = tools.importFile(inputPath)
        filename = os.path.splitext(os.path.basename(inputPath))[0]
        filetype = os.path.splitext(os.path.basename(inputPath))[1][1:]
        resultsPath = os.path.join(outputPath, "results")
        os.makedirs(resultsPath, exist_ok=True)
        preprocessedMesh = tools.PreProcessing(orgMesh, resultsPath, filename, saveOutput=True, preProcessing=preProcess, outputType=filetype, resolution=edgeLen, smoothing=smooth)
        print("Saved mesh at: ", outputPath)
    elif len(inputPath.split(".")) == 1:
        print("Batch mode")
        dir_list = os.listdir(inputPath)
        resultsPath = os.path.join(outputPath, "results")
        os.makedirs(resultsPath, exist_ok=True)
        for i, dir in enumerate(dir_list):
            path = f"{inputPath}\{dir}"
            mesh = tools.importFile(f"{inputPath}\{dir}")
            filename = dir[:-4] + "_Pre-processed"
            filetype = os.path.splitext(os.path.basename(path))[1][1:]
            preprocessedMesh = tools.PreProcessing(mesh, resultsPath, filename, saveOutput=True, preProcessing=preProcess, outputType=filetype, resolution=edgeLen, smoothing=smooth)
    else:
        print("Error in input path given, check for extra dots")

    print("Process complete! Opening results folder")
    if keepOpen == False:
        import rhinoscriptsyntax as rs  # type: ignore

        rs.Command(f"_-Exit No")
    os.startfile(resultsPath)


if __name__ == "__main__":
    main()
