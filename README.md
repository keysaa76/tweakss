# LEVSCLOADES — Fast Dashboard Build

This version keeps the same dashboard design but improves startup responsiveness:
- Dashboard renders before hardware/PowerShell detection completes.
- System detection runs in a background thread.
- System information uses one PowerShell process instead of several.
- No periodic PowerShell polling on the UI thread.
- Fixed page title call for scan pages.

For the fastest EXE startup, this build uses PyInstaller `--onedir`. A `--onefile` build is possible but normally has extra startup overhead because the bundled files must be unpacked at launch.

Run:
python -m pip install -r requirements.txt
python main.py
