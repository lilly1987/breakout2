@echo off
REM Check if python is installed
python --version 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and add it to your PATH.
    pause
    exit /b
)

REM Check for pygame and install if not found
python -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo Installing pygame...
    python -m pip install pygame
)

REM Run the game
:TOP
python game.py
pause
goto :TOP