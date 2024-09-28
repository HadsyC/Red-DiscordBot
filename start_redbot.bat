@echo off
call .venv\Scripts\activate
python -O -m redbot Turingmaschine

IF %ERRORLEVEL% == 1 GOTO RESTART_RED
IF %ERRORLEVEL% == 26 GOTO RESTART_RED
EXIT /B %ERRORLEVEL%

:RESTART_RED
ECHO Restarting Red...
GOTO RED