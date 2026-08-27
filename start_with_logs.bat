@echo off
echo ==========================================
echo Starting FPL AI Assistant with Persistent Logs
echo ==========================================
echo.
echo Logs are being appended to:
echo  - backend_output.log
echo  - frontend_output.log
echo.

echo ======================================================== >> backend_output.log
echo Starting Backend at %date% %time% >> backend_output.log
echo ======================================================== >> backend_output.log

cd backend
start "FPL Backend" cmd /k "echo Backend is running and logging to backend_output.log... && python main.py >> ..\backend_output.log 2>&1"
cd ..

echo ======================================================== >> frontend_output.log
echo Starting Frontend at %date% %time% >> frontend_output.log
echo ======================================================== >> frontend_output.log

cd frontend
start "FPL Frontend" cmd /k "echo Frontend is running and logging to frontend_output.log... && npm run dev >> ..\frontend_output.log 2>&1"
cd ..

echo Both servers have been started in new windows.
echo Keep those windows open to keep the servers running.
echo If you run into a problem, check backend_output.log and frontend_output.log!
echo.
pause
