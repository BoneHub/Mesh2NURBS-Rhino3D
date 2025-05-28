@echo off
setlocal enabledelayedexpansion

echo Installing the package...
pip install .

:: Get Python version
for /f %%i in ('python -c "import sys; print(f'Python{sys.version_info.major}{sys.version_info.minor}')"') do set "PYVERSION=%%i"

:: Get base user directory
for /f "delims=" %%i in ('python -m site --user-base') do set "PYUSERBASE=%%i"

:: Construct full Scripts path
set "SCRIPTS_DIR=%PYUSERBASE%\%PYVERSION%\Scripts"

echo.
echo Checking if %SCRIPTS_DIR% is in PATH...
echo.

:: Check if SCRIPTS_DIR is in PATH
echo %PATH% | find /I "%SCRIPTS_DIR%" >nul
if errorlevel 1 (
    echo WARNING: Your PATH does not include the Scripts directory.
    echo.
    echo You need to add the following to your PATH for the package to work as expected:
    echo     %SCRIPTS_DIR%
    echo.

    choice /M "Do you want to add this to your user PATH now?"
    if errorlevel 2 (
        echo PATH not set correctly, package might not be usable as expected.
    ) else (
        :: Read existing user PATH
        for /f "tokens=2*" %%A in ('reg query HKCU\Environment /v PATH 2^>nul') do set "OLD_PATH=%%B"

        :: Avoid duplicate
        echo !OLD_PATH! | find /I "%SCRIPTS_DIR%" >nul
        if errorlevel 1 (
            setx PATH "!OLD_PATH!;%SCRIPTS_DIR%"
            echo Added %SCRIPTS_DIR% to your user PATH.
            echo Please restart your terminal for changes to take effect.
        ) else (
            echo It's already in your user PATH.
        )
    )
) else (
    echo PATH is correctly set.
    echo Package is ready to use!
)

echo.
choice /M "Do you want to open the README file or close the terminal?"

if %errorlevel%==1 (
    start README.md
) else (
    echo.
)