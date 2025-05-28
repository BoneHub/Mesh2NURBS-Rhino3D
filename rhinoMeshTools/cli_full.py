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
import csv
import time

def main():

    # Show help without launching Rhino
    if "--help" in sys.argv or "-h" in sys.argv:
        parser = argparse.ArgumentParser(description="Launches Rhino and converts the given mesh file(s) to a CAD format. All options below are optional, the command works as long as the current working directory only contains mesh files")
        parser.add_argument("--input", type=str, help="Path to the input file or folder, defaults to current folder if not given")
        parser.add_argument("--output", type=str, help="Output folder, defaults to current folder if not given. Needs to alway be a folder, not a file")
        parser.add_argument("--nopreprocessing", action="store_true", help="Turns off preprocessing. If not stated, preprocessing is enabled.")
        parser.add_argument("--preprocessing", type=str, help="Type of preprocessing, either 'shrinkwrap', 'fixholes', or 'fixshell'. Defaults to 'shrinkwrap'. Does nothing if nopreprocessing is stated")
        parser.add_argument("--nosubd", action="store_true", help="Turns off subdivision. If not stated, subdivision is enabled.")
        parser.add_argument("--quadremeshlength", type=float, help="Sets the target edge length of the quad-remesh function in millimeters. Defaults to 2mm")
        parser.add_argument("--shrinkwraplength", type=float, help="Sets the target edge length of the shrinkwrap function in millimeters. Defaults to 1mm and does nothing if a different type of preprocessing is selected.")
        parser.add_argument("--filetype", type=str, help="File type of the output. Defaults to 'igs', but can also be 'iges', 'stp', or 'step'")
        parser.add_argument("--heatmap", action="store_true", help="Generates heatmap of the distances between input and output mesh and saves it in the specified output folder. If not stated, no heatmap will be created.")
        parser.add_argument("--savedistances", action="store_true", help="If stated, calculates chamfer and hausdorff distances between input and output mesh and stores them in a csv in the output folder. It is not recommended to turn this setting on if the input folder contains a lot of files, since it is rather slow.")
        parser.print_help()
        return
    
    # Launch rhino if not launched already
    if "Rhino.exe" not in sys.executable:
        

        parser = argparse.ArgumentParser()
        parser.add_argument("--input", type=str, default=os.getcwd(), help="Path to the input file or folder, defaults to current folder if not given, If folder is given, all files in that folder will be processed")
        parser.add_argument("--output", type=str, help="Output folder, defaults to current folder or input folder if not given. Needs to alway be a folder, not a file")
        parser.add_argument("--nopreprocessing", action="store_true", help="Turns off preprocessing. If not stated, preprocessing is enabled.")
        parser.add_argument("--preprocessing", default='shrinkwrap', help="Type of preprocessing, either 'shrinkwrap', 'fixholes', or 'fixshell'. Defaults to 'shrinkwrap'. Does nothing if nopreprocessing is stated")
        parser.add_argument("--nosubd", action="store_true", help="Turns off subdivision. If not stated, subdivision is enabled.")
        parser.add_argument("--quadremeshlength", type=float, default=2, help="Sets the target edge length of the quad-remesh function in millimeters. Defaults to 2mm")
        parser.add_argument("--shrinkwraplength", type=float, default=1, help="Sets the target edge length of the shrinkwrap function in millimeters. Defaults to 1mm and does nothing if a different type of preprocessing is selected.")
        parser.add_argument("--filetype", type=str, default='igs', help="File type of the output. Defaults to 'igs', but can also be 'iges', 'stp', or 'step'")
        parser.add_argument("--heatmap", action="store_true", help="Generates heatmap of the distances between input and output mesh and saves it in the specified output folder. If not stated, no heatmap will be created.")
        parser.add_argument("--savedistances", action="store_true", help="If stated, calculates chamfer and hausdorff distances between input and output mesh and stores them in a csv in the output folder. It is not recommended to turn this setting on if the input folder contains a lot of files, since it is rather slow.")
        args, unknown = parser.parse_known_args()

        # Set environment variable for any args
        os.environ["INPUT_PATH"] = args.input
        if not args.output:
            os.environ["OUTPUT_PATH"] = args.input.split('.')[0]
        else:
            os.environ["OUTPUT_PATH"] = args.output
        os.environ["PREPROCESS_TYPE"] = args.preprocessing
        os.environ["FILE_TYPE"] = args.filetype
        os.environ["QUAD_LENGTH"] = str(args.quadremeshlength)
        os.environ["SHRINK_LENGTH"] = str(args.shrinkwraplength)
        if args.nosubd:
            os.environ["SUBD"] = "False"
        else:
            os.environ["SUBD"] = "True"
        if args.heatmap:
            os.environ["HEAT"] = "True"
        else:
            os.environ["HEAT"] = "False"
        if args.nopreprocessing:
            os.environ["PREPROC_ON_OFF"] = "False"
        else:
            os.environ["PREPROC_ON_OFF"] = "True"
        if args.savedistances:
            os.environ["SAVEDIST"] = "True"
        else:
            os.environ["SAVEDIST"] = "False"

        # Debug prints
        print("Preprocessing:", os.environ.get("PREPROC_ON_OFF"))
        print("Heatmap:", os.environ.get("HEAT"))
        print("Subd:", os.environ.get("SUBD"))
        print("Distances:", os.environ.get("SAVEDIST"))
        print("QuadRemesh Length:", os.environ.get("QUAD_LENGTH"))
        print("ShrinkWrap Length:", os.environ.get("SHRINK_LENGTH"))
        print("Output folder:", os.environ.get("OUTPUT_PATH"))

        # Launch Rhino and run script
        scriptToRun = os.path.abspath(__file__)
        rhinoExePath = "C:\\Program Files\\Rhino 8\\System\\Rhino.exe"
        command = f'"{rhinoExePath}" /nosplash /runscript="_-RunPythonScript ({scriptToRun})"'
        print("Launching Rhino...")
        os.system(f'"{command}"')

        return
    
    # Retrieve args from environment variables
    inputPath = os.environ.get("INPUT_PATH")
    outputPath = os.environ.get("OUTPUT_PATH")
    preProcessType = os.environ.get("PREPROCESS_TYPE")
    filetype = os.environ.get("FILE_TYPE")
    quadLength = float(os.environ.get("QUAD_LENGTH"))
    shrinkLength = float(os.environ.get("SHRINK_LENGTH"))
    subd = os.environ.get("SUBD") == "True"
    heat = os.environ.get("HEAT") == "True"
    preProc = os.environ.get("PREPROC_ON_OFF") == "True"
    saveDist = os.environ.get("SAVEDIST") == "True"


    # Execute main part of code
    import tools

    if len(inputPath.split('.')) == 2:

        print("Single file mode")
        orgMesh = tools.importFile(inputPath)
        filename = os.path.splitext(os.path.basename(inputPath))[0]
        resultsPath = os.path.join(outputPath, "results")
        os.makedirs(resultsPath, exist_ok=True)
        cadFolder = os.path.join(resultsPath, "CADModels")
        os.makedirs(cadFolder, exist_ok=True)
        [org, shrink, cad] = tools.fullPipeline(orgMesh, inputPath, cadFolder, prep=preProcessType, preProcess=preProc, edgePreProcessing=shrinkLength, edgeConversion=quadLength, smoothing=0, heat=heat, subd=subd)
        if cad:
            tools.exportMesh(cad, cadFolder, filetype, filename)
        else:
            print("Could not convert, quadremesh failed")
        if heat:
            imageFolder = os.path.join(resultsPath, "heatmapImages")
            os.makedirs(imageFolder, exist_ok=True)
            heatPLYFolder = os.path.join(resultsPath, "heatmapModels")
            os.makedirs(heatPLYFolder, exist_ok=True)
            if preProc:
                tools.heatmap(shrink, cad, inputPath, imageFolder, heatPLYFolder, shrinkLength, filename=filename)
            else:
                tools.heatmap(org, cad, inputPath, imageFolder, heatPLYFolder, shrinkLength, filename=filename)

        if saveDist:
            csvFolder = os.path.join(resultsPath, "distances")
            os.makedirs(csvFolder, exist_ok=True)
            if preProc:
                distances = tools.chamferDistance(shrink, cad)
            else:
                distances = tools.chamferDistance(org, cad)
            csvTable = [["Filename", "Chamfer Distance", "Hausdorff Distance"]]
            csvTable.append([filename, distances[0], distances[1]])
            if saveDist:
                csv_output_path = os.path.join(csvFolder, "results.csv")
                with open(csv_output_path, mode="w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(csvTable)
        
        

    elif len(inputPath.split('.')) == 1:

        print("Batch mode")
        dir_list = os.listdir(inputPath)
        csvTable = [["Filename", "Chamfer Distance", "Hausdorff Distance"]]
        resultsPath = os.path.join(outputPath, "results")
        os.makedirs(resultsPath, exist_ok=True)
        cadFolder = os.path.join(resultsPath, "CADModels")
        os.makedirs(cadFolder, exist_ok=True)
        if heat:
            imageFolder = os.path.join(resultsPath, "heatmapImages")
            os.makedirs(imageFolder, exist_ok=True)
            heatPLYFolder = os.path.join(resultsPath, "heatmapModels")
            os.makedirs(heatPLYFolder, exist_ok=True)
        for i, dir in enumerate(dir_list):
            # Print info
            start = time.time()
            print(f"Current File: {i+1}/{len(dir_list)}")
            print("-------------------------------------")
            print("Trying to import")
            orgMesh = tools.importFile(f"{inputPath}\{dir}")
            print("Imported")
            filename = dir[:-4]
            [org, shrink, cad] = tools.fullPipeline(orgMesh, inputPath, cadFolder, prep=preProcessType, preProcess=preProc, edgePreProcessing=shrinkLength, edgeConversion=quadLength, smoothing=0, heat=heat, subd=subd) 
            if cad:
                tools.exportMesh(cad, cadFolder, filetype, filename)
                if heat:
                    if preProc:
                        tools.heatmap(shrink, cad, inputPath, imageFolder, heatPLYFolder, shrinkLength, filename=filename)
                    else:
                        tools.heatmap(org, cad, inputPath, imageFolder, heatPLYFolder, shrinkLength, filename=filename)
            else:
                print("Could not convert for some reason, skipping this file...")
            
            # Print info
            stop = time.time()
            print("-------------------------------------")
            progress = i/len(dir_list) * 100
            print(f"Progress: {progress:.2f}%")
            print(f"Previous iteration took: {(stop-start):.2f} seconds")


        # Distance saving
            if saveDist:
                if preProc:
                    distances = tools.chamferDistance(shrink, cad)
                else:
                    distances = tools.chamferDistance(org, cad)
                csvTable.append([filename, distances[0], distances[1]])
        if saveDist:
            csvFolder = os.path.join(resultsPath, "distances")
            os.makedirs(csvFolder, exist_ok=True)
            csv_output_path = os.path.join(csvFolder, "distances.csv")
            with open(csv_output_path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(csvTable)
            print("Saved distances at ", csvFolder)

        



    print("------------------")
    print("Process complete! Opening results folder")
    os.startfile(resultsPath)

if __name__ == "__main__":
    main()

