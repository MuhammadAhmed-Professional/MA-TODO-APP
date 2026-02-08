#!/bin/bash

# Phase 2 Frontend Deployment Script for Vercel
# This script helps deploy the Next.js frontend to Vercel with all required environment variables

set -e  # Exit on error

echo "🚀 Phase 2 Frontend - Vercel Deployment Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend API URL (already deployed)
BACKEND_URL="https://backend-production-9a40.up.railway.app"

# Generated secrets
BETTER_AUTH_SECRET="9TNI5WqJgVWRDvg8J5053/yEH7dnnLUNliT3x7CI0Qw="

echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo "   Backend API: $BACKEND_URL"
echo "   Better Auth Secret: Generated (32 bytes)"
echo ""

# Check if logged in to Vercel
echo -e "${BLUE}🔐 Step 1: Checking Vercel authentication...${NC}"
if ! vercel whoami &>/dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Vercel${NC}"
    echo "Please run: vercel login"
    echo "Then run this script again."
    exit 1
fi

echo -e "${GREEN}✅ Logged in to Vercel${NC}"
VERCEL_USER=$(vercel whoami 2>/dev/null)
echo "   User: $VERCEL_USER"
echo ""

# Set environment variables
echo -e "${BLUE}🔧 Step 2: Setting environment variables...${NC}"

# Function to set env variable
set_env_var() {
    local var_name=$1
    local var_value=$2
    local environments=$3  # production, preview, development (comma-separated)

    echo "   Setting $var_name..."

    # Remove existing variable if it exists
    vercel env rm "$var_name" production --yes &>/dev/null || true
    vercel env rm "$var_name" preview --yes &>/dev/null || true
    vercel env rm "$var_name" development --yes &>/dev/null || true

    # Add new variable
    echo "$var_value" | vercel env add "$var_name" production --yes &>/dev/null
    echo "$var_value" | vercel env add "$var_name" preview --yes &>/dev/null
    echo "$var_value" | vercel env add "$var_name" development --yes &>/dev/null

    echo -e "   ${GREEN}✅ $var_name set${NC}"
}

# Set all environment variables
set_env_var "NEXT_PUBLIC_API_URL" "$BACKEND_URL" "production,preview,development"
set_env_var "BETTER_AUTH_SECRET" "$BETTER_AUTH_SECRET" "production,preview,development"
set_env_var "NEXT_PUBLIC_ENVIRONMENT" "production" "production,preview,development"
set_env_var "NEXT_PUBLIC_APP_NAME" "Phase II Todo" "production,preview,development"

echo ""
echo -e "${GREEN}✅ All environment variables configured${NC}"
echo ""

# Deploy to production
echo -e "${BLUE}🚀 Step 3: Deploying to Vercel (Production)...${NC}"
echo ""

vercel --prod --yes

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Visit your deployment URL (shown above)"
echo "2. Test signup/login functionality"
echo "3. Create, edit, and delete tasks"
echo "4. Verify API integration"
echo ""
echo -e "${BLUE}🔍 To view deployment details:${NC}"
echo "   vercel ls"
echo ""
echo -e "${BLUE}📊 To view deployment logs:${NC}"
echo "   vercel logs"
echo ""
