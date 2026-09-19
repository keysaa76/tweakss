@echo off
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
REM --onefile is convenient but slower to start because it extracts at launch.
REM Use --onedir for the fastest startup.
python -m PyInstaller --onedir --windowed --clean --name LEVSCLOADES main.py
if exist dist\LEVSCLOADES\LEVSCLOADES.exe echo Build finished: dist\LEVSCLOADES\LEVSCLOADES.exe
pause
