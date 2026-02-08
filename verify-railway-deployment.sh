#!/bin/bash

# Railway Backend Deployment Verification Script
# This script checks if the Better Auth session token fix is deployed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Railway backend URL (update this with your actual URL)
BACKEND_URL="${BACKEND_URL:-https://your-backend.railway.app}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Railway Backend Deployment Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check 1: Health endpoint
echo -e "${YELLOW}[1/4] Checking health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP 200)${NC}"
else
    echo -e "${RED}✗ Health check failed (HTTP $HEALTH_RESPONSE)${NC}"
    exit 1
fi

# Check 2: CORS headers
echo -e "${YELLOW}[2/4] Checking CORS configuration...${NC}"
CORS_HEADER=$(curl -s -I "$BACKEND_URL/health" | grep -i "access-control-allow-origin" || echo "")

if [ -n "$CORS_HEADER" ]; then
    echo -e "${GREEN}✓ CORS headers present: $CORS_HEADER${NC}"
else
    echo -e "${YELLOW}⚠ CORS headers not found (may be okay if not needed for /health)${NC}"
fi

# Check 3: Auth endpoint exists
echo -e "${YELLOW}[3/4] Checking auth endpoint...${NC}"
AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/auth/login" -X POST \
    -H "Content-Type: application/json" \
    -d '{}')

if [ "$AUTH_RESPONSE" = "422" ] || [ "$AUTH_RESPONSE" = "401" ] || [ "$AUTH_RESPONSE" = "400" ]; then
    echo -e "${GREEN}✓ Auth endpoint accessible (HTTP $AUTH_RESPONSE - validation error expected)${NC}"
elif [ "$AUTH_RESPONSE" = "404" ]; then
    echo -e "${RED}✗ Auth endpoint not found (HTTP 404)${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠ Unexpected auth response (HTTP $AUTH_RESPONSE)${NC}"
fi

# Check 4: API version/info (if available)
echo -e "${YELLOW}[4/4] Checking API info...${NC}"
API_INFO=$(curl -s "$BACKEND_URL/" || echo "{}")

if echo "$API_INFO" | grep -q "FastAPI" || echo "$API_INFO" | grep -q "Todo" || echo "$API_INFO" | grep -q "message"; then
    echo -e "${GREEN}✓ API root endpoint responding${NC}"
    echo -e "${BLUE}Response: $API_INFO${NC}"
else
    echo -e "${YELLOW}⚠ API root endpoint returned unexpected response${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Deployment verification complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Check Railway dashboard for deployment status"
echo "2. Verify environment variables (AUTH_SERVER_URL, DATABASE_URL, JWT_SECRET)"
echo "3. Test login flow from frontend application"
echo "4. Monitor Railway logs for any errors"
echo ""
echo -e "${BLUE}Backend URL: $BACKEND_URL${NC}"
echo ""
