@echo off
echo Resetting Kogniq Local Development Environment...
echo WARNING: This will destroy all local data in containers.
choice /M "Are you sure you want to continue?"
if errorlevel 2 goto :EOF
docker compose down -v
echo Containers and volumes removed. Run start-dev to initialize again.
