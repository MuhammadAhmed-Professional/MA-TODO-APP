#!/bin/bash
# Complete Flow Test Script
# Tests authentication and task CRUD operations

echo "======================================"
echo "Phase II Todo App - Complete Flow Test"
echo "======================================"
echo ""

# URLs
BACKEND_URL="https://tda-backend-production.up.railway.app"
AUTH_SERVER_URL="https://auth-server-production-8251.up.railway.app"
FRONTEND_URL="https://talal-s-tda.vercel.app"

# Test credentials
EMAIL="test@test.com"
PASSWORD="test1234"

echo "1. Testing Backend Health..."
BACKEND_HEALTH=$(curl -s "$BACKEND_URL/health")
echo "Backend: $BACKEND_HEALTH"
echo ""

echo "2. Testing Auth Server Health..."
AUTH_HEALTH=$(curl -s "$AUTH_SERVER_URL/health")
echo "Auth Server: $AUTH_HEALTH"
echo ""

echo "3. Attempting Signup..."
SIGNUP_RESPONSE=$(curl -s -X POST "$AUTH_SERVER_URL/api/auth/sign-up/email" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"name\":\"Test User\"}" \
  --max-time 10 2>&1)
echo "Signup Response: $SIGNUP_RESPONSE"
echo ""

echo "4. Attempting Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_SERVER_URL/api/auth/sign-in/email" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  -c cookies.txt \
  --max-time 10 2>&1)
echo "Login Response: $LOGIN_RESPONSE"
echo ""

# Extract token from cookies if available
if [ -f "cookies.txt" ]; then
    TOKEN=$(grep "better-auth.session_token" cookies.txt | awk '{print $7}')
    echo "Session Token: $TOKEN"
    echo ""

    if [ -n "$TOKEN" ]; then
        echo "5. Testing GET /api/tasks with token..."
        TASKS_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks" \
          -H "Authorization: Bearer $TOKEN" \
          --max-time 10 2>&1)
        echo "Tasks Response: $TASKS_RESPONSE"
        echo ""

        echo "6. Creating a test task..."
        CREATE_TASK=$(curl -s -X POST "$BACKEND_URL/api/tasks" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"title":"Test Task from Script","description":"Testing complete flow"}' \
          --max-time 10 2>&1)
        echo "Create Task Response: $CREATE_TASK"
        echo ""
    else
        echo "No token found in cookies - login may have failed"
    fi
else
    echo "No cookies file created - login definitely failed"
fi

echo "======================================"
echo "Test Complete!"
echo "======================================"
