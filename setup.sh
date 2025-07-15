#!/bin/bash

# Configuration management script for Haivler Backend

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Haivler Backend Configuration Setup${NC}"
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Display current configuration
echo ""
echo -e "${GREEN}Current Configuration:${NC}"
if [ -f .env ]; then
    echo "Database Port: $(grep '^DB_PORT=' .env 2>/dev/null | cut -d'=' -f2 || echo 'Not set (default: 3306)')"
    echo "Backend Port: $(grep '^BACKEND_PORT=' .env 2>/dev/null | cut -d'=' -f2 || echo 'Not set (default: 8000)')"
    echo "Nginx Port: $(grep '^NGINX_PORT=' .env 2>/dev/null | cut -d'=' -f2 || echo 'Not set (default: 8811)')"
fi

echo ""
echo -e "${GREEN}Available Commands:${NC}"
echo "1. Start services:     docker-compose up -d"
echo "2. Stop services:      docker-compose down"
echo "3. View logs:          docker-compose logs -f"
echo "4. Restart nginx:      docker-compose restart nginx"
echo ""
echo -e "${GREEN}Development URLs:${NC}"
echo "- API Documentation:   http://localhost:\${BACKEND_PORT:-8000}/docs"
echo "- Production API:      http://localhost:\${NGINX_PORT:-8811}"
echo "- Health Check:        http://localhost:\${NGINX_PORT:-8811}/health"
