@echo off
setlocal EnableExtensions
rem Launcher inside the Windows package — relocates the packed conda env on first run.

set "ROOT=%~dp0"
set "ENV=%ROOT%env"
set "SRC=%ROOT%src"
set "LOG_DIR=%APPDATA%\FlatCAM"
set "LOG_FILE=%LOG_DIR%\launch.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
echo === %DATE% %TIME% FlatCAM launch ===>> "%LOG_FILE%"

set "PATH=%ENV%;%ENV%\Scripts;%ENV%\Library\bin;%PATH%"
set "CONDA_PREFIX=%ENV%"
if exist "%ENV%\Library\share\gdal" set "GDAL_DATA=%ENV%\Library\share\gdal"
if exist "%ENV%\share\gdal" set "GDAL_DATA=%ENV%\share\gdal"
if exist "%ENV%\Library\share\proj" set "PROJ_LIB=%ENV%\Library\share\proj"
if exist "%ENV%\share\proj" set "PROJ_LIB=%ENV%\share\proj"

if exist "%ENV%\Scripts\conda-unpack.exe" (
  "%ENV%\Scripts\conda-unpack.exe" >> "%LOG_FILE%" 2>&1
)

set "ENTRY="
if exist "%SRC%\flatcam.py" set "ENTRY=%SRC%\flatcam.py"
if exist "%SRC%\FlatCAM.py" set "ENTRY=%SRC%\FlatCAM.py"
if not defined ENTRY (
  echo FlatCAM entry script not found in %SRC%>> "%LOG_FILE%"
  echo FlatCAM entry script not found. See %LOG_FILE%
  exit /b 1
)

cd /d "%SRC%"
if exist "%ENV%\pythonw.exe" (
  start "" "%ENV%\pythonw.exe" "%ENTRY%" %*
) else (
  "%ENV%\python.exe" "%ENTRY%" %*
)
