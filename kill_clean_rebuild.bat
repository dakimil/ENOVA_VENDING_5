@echo off
echo === ZATVARANJE PROCESA ===
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
taskkill /f /im flask.exe >nul 2>&1
taskkill /f /im vending_app.exe >nul 2>&1

echo === BRISANJE STARE EXE VERZIJE ===
cd /d C:\ENOVA_VENDING_5\dist
del vending_app.exe >nul 2>&1

echo === POVRATAK U GLAVNI FOLDER ===
cd /d C:\ENOVA_VENDING_5

echo === KREIRANJE NOVE EXE VERZIJE ===
python -m PyInstaller --onefile --windowed vending_app.py

echo.
echo ✅ GOTOVO. Novi vending_app.exe nalazi se u /dist folderu.
pause
