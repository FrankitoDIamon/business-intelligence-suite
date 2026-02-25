@echo off
REM Activar entorno virtual si tienes uno
REM call .\venv\Scripts\activate

REM Verificar PyInstaller
pip show pyinstaller >nul 2>&1
IF ERRORLEVEL 1 (
    echo PyInstaller no encontrado, instalando...
    pip install pyinstaller
) ELSE (
    echo PyInstaller ya esta instalado.
)

REM Crear el ejecutable
python -m PyInstaller ^
--onefile ^
--windowed ^
--icon=icono.png ^
--add-data "database;database" ^
--add-data "png;png" ^
--add-data "respaldos;respaldos" ^
FPventas.py

pause

