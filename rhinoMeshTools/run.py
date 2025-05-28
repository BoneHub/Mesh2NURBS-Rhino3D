import os

def isInRhino():
    try:
        import Rhino # type: ignore
        return True
    except ImportError:
        return False

def executeScript(rhinoExePath, scriptToRun):
    command = f'"{rhinoExePath}" /nosplash /runscript="_-RunPythonScript ({scriptToRun})"'
    os.system(f'"{command}"')

def checkAndRun(rhinoPath, scriptToRun):
    if not isInRhino():
        executeScript(rhinoPath, scriptToRun)


