@echo off
set "SOURCE=C:\ENOVA_VENDING"
set "DEST=C:\ENOVA_BACKUP"

:: Kreiraj datum YYYY-MM-DD
for /f %%i in ('powershell -command "Get-Date -Format yyyy-MM-dd"') do set DATUM=%%i

:: Naziv verzije sa oznakom Funkcionalna
set "FOLDERNAME=V_%DATUM%_Funkcionalna"

:: Kreiraj folder
mkdir "%DEST%\%FOLDERNAME%"

:: Kopiraj sve fajlove
xcopy "%SOURCE%\*" "%DEST%\%FOLDERNAME%\" /E /I /H /Y

echo ------------------------------------------
echo Backup završen: %DEST%\%FOLDERNAME%
pause
