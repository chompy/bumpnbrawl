cd src/p3d

ECHO OFF
CLS
ECHO.
ECHO =============================================
ECHO BumpNBrawl Launcher
ECHO =============================================
ECHO.
ECHO Select A Character
ECHO.
ECHO 1) Chompy
ECHO 2) Renoki
ECHO 3) Colonel Hawk
ECHO.
SET /P M=Type a selection then press ENTER: 
IF %M%==1 python main.py chompy
IF %M%==2 python main.py renoki
IF %M%==3 python main.py hawk
pause
