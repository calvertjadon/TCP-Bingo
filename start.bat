set REQUIRED_VERSION=3.9.0

FOR /F "tokens=*" %%g IN ('python --version') do (SET PY_VER=%%g)
if NOT "%PY_VER%" == "Python %REQUIRED_VERSION%" goto :ALERT

start cmd /K python run_server.py
start cmd /K python run_client.py
start cmd /K python run_client.py

goto :END

:ALERT
echo "Python version %REQUIRED_VERSION% is required to run"

:END