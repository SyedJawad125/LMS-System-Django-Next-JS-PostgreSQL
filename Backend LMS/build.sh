#!/bin/bash

# ============================================
# OPTIMIZED DOCKER BUILD SCRIPT
# ============================================
# This script helps you build and manage your Docker containers efficiently

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main script
case "$1" in
    "build")
        print_header "BUILDING DOCKER IMAGES WITH BUILDKIT"
        print_warning "First build will take 45-60 minutes (downloading ML models)"
        print_warning "Subsequent builds will be MUCH faster (2-5 minutes)"
        echo ""
        DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build
        print_success "Build complete!"
        ;;
        
    "up")
        print_header "STARTING SERVICES"
        docker-compose up -d
        print_success "Services started!"
        echo ""
        print_warning "Access your services:"
        echo "  - Django API: http://localhost:8000"
        echo "  - RabbitMQ Management: http://localhost:15672"
        echo "  - Adminer (DB): http://localhost:8080"
        ;;
        
    "rebuild")
        print_header "REBUILDING AND RESTARTING SERVICES"
        print_warning "This uses cached layers - only rebuilds changed code"
        docker-compose up -d --build
        print_success "Rebuild complete!"
        ;;
        
    "rebuild-full")
        print_header "FULL REBUILD (NO CACHE)"
        print_warning "This will take 45-60 minutes - only use if requirements-base.txt changed"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build --no-cache
            print_success "Full rebuild complete!"
        else
            print_error "Cancelled"
        fi
        ;;
        
    "down")
        print_header "STOPPING SERVICES"
        docker-compose down
        print_success "Services stopped!"
        ;;
        
    "logs")
        print_header "VIEWING LOGS"
        if [ -z "$2" ]; then
            docker-compose logs -f
        else
            docker-compose logs -f "$2"
        fi
        ;;
        
    "shell")
        print_header "OPENING DJANGO SHELL"
        docker-compose exec web python manage.py shell
        ;;
        
    "migrate")
        print_header "RUNNING MIGRATIONS"
        docker-compose exec web python manage.py makemigrations
        docker-compose exec web python manage.py migrate
        print_success "Migrations complete!"
        ;;
        
    "clean")
        print_header "CLEANING UP DOCKER RESOURCES"
        print_warning "This will remove stopped containers, unused networks, and dangling images"
        docker system prune -f
        print_success "Cleanup complete!"
        ;;
        
    *)
        print_header "DOCKER BUILD HELPER SCRIPT"
        echo "Usage: ./build.sh [command]"
        echo ""
        echo "Commands:"
        echo "  build          - Build Docker images (first time: 45-60 min, then: 2-5 min)"
        echo "  up             - Start all services"
        echo "  rebuild        - Quick rebuild after code changes (30 sec)"
        echo "  rebuild-full   - Full rebuild with no cache (45-60 min)"
        echo "  down           - Stop all services"
        echo "  logs [service] - View logs (optional: specify service like 'web' or 'worker')"
        echo "  shell          - Open Django shell"
        echo "  migrate        - Run database migrations"
        echo "  clean          - Clean up Docker resources"
        echo ""
        echo "Examples:"
        echo "  ./build.sh build           # First time setup"
        echo "  ./build.sh up              # Start services"
        echo "  ./build.sh rebuild         # Quick rebuild"
        echo "  ./build.sh logs web        # View web service logs"
        echo "  ./build.sh down            # Stop everything"
        ;;
esac
