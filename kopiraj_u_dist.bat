@echo off
echo 📦 Kopiranje fajlova u dist...

REM Definiši izvor i destinaciju
set SRC=C:\ENOVA_VENDING_5
set DST=C:\ENOVA_VENDING_5\dist

REM Kreiraj folder dist ako ne postoji
if not exist "%DST%" (
    mkdir "%DST%"
)

REM Kopiraj JSON fajlove
copy "%SRC%\artikli.json" "%DST%\" /Y
copy "%SRC%\poruke.json" "%DST%\" /Y
if exist "%SRC%\log.txt" copy "%SRC%\log.txt" "%DST%\" /Y

REM Kopiraj folderske strukture
xcopy "%SRC%\templates" "%DST%\templates" /E /I /Y
xcopy "%SRC%\static" "%DST%\static" /E /I /Y

echo ✅ Gotovo! Svi fajlovi su kopirani u dist.
pause
