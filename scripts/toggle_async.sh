#!/bin/bash
# Toggle async mode for DeepSeek API
# Usage: ./toggle_async.sh [enable|disable|status]
#
# NOTE: If permission denied, run: chmod +x toggle_async.sh

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env"
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Environment file $ENV_FILE not found"
        exit 1
    fi
}

backup_file() {
    local file=$1
    mkdir -p "$BACKUP_DIR"
    cp "$file" "$BACKUP_DIR/$(basename $file).$TIMESTAMP"
    print_status "Backed up $file to $BACKUP_DIR/"
}

enable_async() {
    print_status "Enabling async mode..."
    
    # Backup current state
    backup_file "$ENV_FILE"
    
    # Update .env file
    if grep -q "USE_ASYNC_DEEPSEEK" "$ENV_FILE"; then
        sed -i.bak 's/USE_ASYNC_DEEPSEEK=.*/USE_ASYNC_DEEPSEEK=1/' "$ENV_FILE"
    else
        echo "USE_ASYNC_DEEPSEEK=1" >> "$ENV_FILE"
    fi
    
    # Set Flask async support
    if grep -q "FLASK_ASYNC_ENABLED" "$ENV_FILE"; then
        sed -i.bak 's/FLASK_ASYNC_ENABLED=.*/FLASK_ASYNC_ENABLED=1/' "$ENV_FILE"
    else
        echo "FLASK_ASYNC_ENABLED=1" >> "$ENV_FILE"
    fi
    
    print_status "Async mode ENABLED"
    print_status "Settings:"
    echo "  - USE_ASYNC_DEEPSEEK=1"
    echo "  - FLASK_ASYNC_ENABLED=1"
    
    # Reload application (if using Gunicorn with HUP signal)
    if pgrep -f gunicorn > /dev/null; then
        print_status "Reloading Gunicorn workers..."
        pkill -HUP -f gunicorn
    else
        print_warning "Gunicorn not running. Please restart your application manually."
    fi
}

disable_async() {
    print_status "Disabling async mode..."
    
    # Backup current state
    backup_file "$ENV_FILE"
    
    # Update .env file
    if grep -q "USE_ASYNC_DEEPSEEK" "$ENV_FILE"; then
        sed -i.bak 's/USE_ASYNC_DEEPSEEK=.*/USE_ASYNC_DEEPSEEK=0/' "$ENV_FILE"
    else
        echo "USE_ASYNC_DEEPSEEK=0" >> "$ENV_FILE"
    fi
    
    # Disable Flask async support
    if grep -q "FLASK_ASYNC_ENABLED" "$ENV_FILE"; then
        sed -i.bak 's/FLASK_ASYNC_ENABLED=.*/FLASK_ASYNC_ENABLED=0/' "$ENV_FILE"
    else
        echo "FLASK_ASYNC_ENABLED=0" >> "$ENV_FILE"
    fi
    
    print_status "Async mode DISABLED"
    print_status "Settings:"
    echo "  - USE_ASYNC_DEEPSEEK=0"
    echo "  - FLASK_ASYNC_ENABLED=0"
    
    # Reload application
    if pgrep -f gunicorn > /dev/null; then
        print_status "Reloading Gunicorn workers..."
        pkill -HUP -f gunicorn
    else
        print_warning "Gunicorn not running. Please restart your application manually."
    fi
}

show_status() {
    print_status "Current async mode status:"
    
    if [ -f "$ENV_FILE" ]; then
        async_enabled=$(grep "USE_ASYNC_DEEPSEEK" "$ENV_FILE" | cut -d'=' -f2 || echo "not set")
        flask_async=$(grep "FLASK_ASYNC_ENABLED" "$ENV_FILE" | cut -d'=' -f2 || echo "not set")
        
        if [ "$async_enabled" = "1" ]; then
            echo -e "  - DeepSeek Async: ${GREEN}ENABLED${NC}"
        elif [ "$async_enabled" = "0" ]; then
            echo -e "  - DeepSeek Async: ${RED}DISABLED${NC}"
        else
            echo -e "  - DeepSeek Async: ${YELLOW}NOT SET${NC}"
        fi
        
        if [ "$flask_async" = "1" ]; then
            echo -e "  - Flask Async: ${GREEN}ENABLED${NC}"
        elif [ "$flask_async" = "0" ]; then
            echo -e "  - Flask Async: ${RED}DISABLED${NC}"
        else
            echo -e "  - Flask Async: ${YELLOW}NOT SET${NC}"
        fi
    else
        print_error "Environment file not found"
    fi
    
    # Check if async routes are loaded
    if pgrep -f gunicorn > /dev/null; then
        echo ""
        print_status "Application status: ${GREEN}RUNNING${NC}"
    else
        echo ""
        print_status "Application status: ${RED}NOT RUNNING${NC}"
    fi
}

# Main logic
case "$1" in
    enable)
        check_env_file
        enable_async
        ;;
    disable)
        check_env_file
        disable_async
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {enable|disable|status}"
        echo ""
        echo "Commands:"
        echo "  enable   - Enable async mode for DeepSeek API"
        echo "  disable  - Disable async mode (use sync mode)"
        echo "  status   - Show current async mode status"
        echo ""
        echo "Examples:"
        echo "  $0 enable    # Enable async mode"
        echo "  $0 disable   # Disable async mode"
        echo "  $0 status    # Check current status"
        exit 1
        ;;
esac

exit 0
