@echo off
echo Starting Kogniq Local Development Environment...
docker compose up -d
if %errorlevel% neq 0 (
    echo Failed to start containers. Please ensure Docker is running.
    exit /b %errorlevel%
)
echo Containers started successfully.
