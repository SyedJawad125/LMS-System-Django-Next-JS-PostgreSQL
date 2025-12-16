@echo off
REM ============================================
REM OPTIMIZED DOCKER BUILD SCRIPT FOR WINDOWS
REM ============================================

setlocal enabledelayedexpansion

if "%1"=="build" goto BUILD
if "%1"=="up" goto UP
if "%1"=="rebuild" goto REBUILD
if "%1"=="rebuild-full" goto REBUILD_FULL
if "%1"=="down" goto DOWN
if "%1"=="logs" goto LOGS
if "%1"=="shell" goto SHELL
if "%1"=="migrate" goto MIGRATE
if "%1"=="clean" goto CLEAN
goto HELP

:BUILD
echo ============================================
echo BUILDING DOCKER IMAGES WITH BUILDKIT
echo ============================================
echo WARNING: First build will take 45-60 minutes
echo Subsequent builds will be MUCH faster (2-5 minutes)
echo.
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build
echo.
echo SUCCESS: Build complete!
goto END

:UP
echo ============================================
echo STARTING SERVICES
echo ============================================
docker-compose up -d
echo.
echo SUCCESS: Services started!
echo.
echo Access your services:
echo   - Django API: http://localhost:8000
echo   - RabbitMQ Management: http://localhost:15672
echo   - Adminer (DB): http://localhost:8080
goto END

:REBUILD
echo ============================================
echo REBUILDING AND RESTARTING SERVICES
echo ============================================
echo This uses cached layers - only rebuilds changed code
docker-compose up -d --build
echo.
echo SUCCESS: Rebuild complete!
goto END

:REBUILD_FULL
echo ============================================
echo FULL REBUILD (NO CACHE)
echo ============================================
echo WARNING: This will take 45-60 minutes
set /p confirm="Are you sure? (yes/no): "
if /i "%confirm%"=="yes" (
    set DOCKER_BUILDKIT=1
    set COMPOSE_DOCKER_CLI_BUILD=1
    docker-compose build --no-cache
    echo.
    echo SUCCESS: Full rebuild complete!
) else (
    echo Cancelled
)
goto END

:DOWN
echo ============================================
echo STOPPING SERVICES
echo ============================================
docker-compose down
echo.
echo SUCCESS: Services stopped!
goto END

:LOGS
echo ============================================
echo VIEWING LOGS
echo ============================================
if "%2"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %2
)
goto END

:SHELL
echo ============================================
echo OPENING DJANGO SHELL
echo ============================================
docker-compose exec web python manage.py shell
goto END

:MIGRATE
echo ============================================
echo RUNNING MIGRATIONS
echo ============================================
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
echo.
echo SUCCESS: Migrations complete!
goto END

:CLEAN
echo ============================================
echo CLEANING UP DOCKER RESOURCES
echo ============================================
echo This will remove stopped containers, unused networks, and dangling images
docker system prune -f
echo.
echo SUCCESS: Cleanup complete!
goto END

:HELP
echo ============================================
echo DOCKER BUILD HELPER SCRIPT (Windows)
echo ============================================
echo Usage: build.bat [command]
echo.
echo Commands:
echo   build          - Build Docker images (first time: 45-60 min, then: 2-5 min)
echo   up             - Start all services
echo   rebuild        - Quick rebuild after code changes (30 sec)
echo   rebuild-full   - Full rebuild with no cache (45-60 min)
echo   down           - Stop all services
echo   logs [service] - View logs (optional: specify service like 'web' or 'worker')
echo   shell          - Open Django shell
echo   migrate        - Run database migrations
echo   clean          - Clean up Docker resources
echo.
echo Examples:
echo   build.bat build           # First time setup
echo   build.bat up              # Start services
echo   build.bat rebuild         # Quick rebuild
echo   build.bat logs web        # View web service logs
echo   build.bat down            # Stop everything
goto END

:END
endlocal
