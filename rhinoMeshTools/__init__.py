# rhinoMeshProcessingTools/__init__.py

import sys
import inspect


def _running_inside_rhino():
    # Rhino adds these modules to sys.modules when it runs Python scripts
    return "rhinoscriptsyntax" in sys.modules or "Rhino" in sys.modules


def _auto_start():
    from .run import checkAndRun
    from .importHelper import importPackages

    # Optional: make this path dynamic or read from env/config if you want
    rhino_path = r"C:\Program Files\Rhino 8\System\Rhino.exe"
    script = inspect.stack()[-1].filename
    checkAndRun(rhino_path, script)
    importPackages()


def _running_in_cli():
    return any("mesh" in arg.lower() for arg in sys.argv)


# Don't launch Rhino again if we're already inside it
if not _running_inside_rhino() and not _running_in_cli():
    _auto_start()

from .tools import importFile, fullPipeline, fullPipelineBatch, heatmap, PreProcessing, chamferDistance, deleteNonsense, meshDistanceCalculator, stl2cad, exportMesh

__all__ = ["fullPipeline", "deleteNonsense", "PreProcessing", "stl2cad", "meshDistanceCalculator", "chamferDistance", "importFile", "exportMesh"]
