@echo off
REM Docker Build and Run Script for Weight Planner (Windows)

echo =========================================
echo Weight Planner - Docker Build Script
echo =========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found
    echo Please create .env file from .env.docker template:
    echo   copy .env.docker .env
    echo   notepad .env  ^(Edit with your credentials^)
    exit /b 1
)

echo [OK] Checking environment variables...

REM Build Docker image
echo.
echo =========================================
echo Building Docker image...
echo =========================================
docker build -t weight-planner:latest .

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Docker build failed
    exit /b 1
)

echo.
echo [OK] Docker image built successfully!

REM Start container
echo.
echo =========================================
echo Starting container with docker-compose...
echo =========================================
docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to start container
    exit /b 1
)

echo.
echo [OK] Container started successfully!
echo.
echo =========================================
echo Application is running!
echo =========================================
echo.
echo Access the app at: http://localhost:8501
echo.
echo Useful commands:
echo   View logs:    docker-compose logs -f
echo   Stop:         docker-compose down
echo   Restart:      docker-compose restart
echo   Shell access: docker exec -it weight-planner-app bash
echo.

pause
