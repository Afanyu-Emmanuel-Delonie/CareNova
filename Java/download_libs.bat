@echo off
setlocal enabledelayedexpansion

if not exist lib mkdir lib
cd lib

echo Downloading JUnit 5 libraries...

set "urls[0]=https://repo1.maven.org/maven2/org/junit/jupiter/junit-jupiter-api/5.9.2/junit-jupiter-api-5.9.2.jar"
set "urls[1]=https://repo1.maven.org/maven2/org/junit/jupiter/junit-jupiter-engine/5.9.2/junit-jupiter-engine-5.9.2.jar"
set "urls[2]=https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.9.2/junit-platform-console-standalone-1.9.2.jar"
set "urls[3]=https://repo1.maven.org/maven2/org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar"

for /l %%i in (0,1,3) do (
    for /f %%F in ("!urls[%%i]!") do (
        set "url=!urls[%%i]!"
        for %%A in (!url!) do set "filename=%%~nxA"
        if not exist "!filename!" (
            echo Downloading !filename!...
            powershell -Command "Invoke-WebRequest -Uri '!url!' -OutFile '!filename!'"
        ) else (
            echo !filename! already exists
        )
    )
)

echo Done!
cd ..
