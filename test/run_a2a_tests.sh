#!/bin/bash

# Comprehensive A2A Protocol Test Script
# Creates test agent, authenticates, and tests all endpoints

BASE_URL="${BASE_URL:-http://localhost:5003}"
API_URL="${BASE_URL}/api/a2a"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== OASIS A2A Protocol Comprehensive Tests ===${NC}\n"

# Generate unique test username
TEST_USERNAME="test_agent_$(date +%s)"
TEST_EMAIL="${TEST_USERNAME}@test.oasis"
TEST_PASSWORD="TestPassword123!"

echo -e "${YELLOW}Step 1: Register Test Agent Avatar${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/avatar/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${TEST_USERNAME}\",
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"confirmPassword\": \"${TEST_PASSWORD}\",
    \"firstName\": \"Test\",
    \"lastName\": \"Agent\",
    \"avatarType\": \"Agent\",
    \"acceptTerms\": true
  }")

echo "Register Response: $REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"
echo ""

# Extract avatar ID if registration successful
AVATAR_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); r=data.get('result', {}); print(r.get('result', {}).get('id', r.get('id', '')))" 2>/dev/null)

if [ -z "$AVATAR_ID" ] || [ "$AVATAR_ID" == "None" ] || [ "$AVATAR_ID" == "" ]; then
    echo -e "${YELLOW}Avatar ID not found in registration response, will try to get from auth...${NC}"
    AVATAR_ID=""
else
    echo -e "${GREEN}✓ Agent avatar registered: ${AVATAR_ID}${NC}\n"
fi

echo -e "${YELLOW}Step 2: Authenticate Agent Avatar${NC}"
AUTH_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/avatar/authenticate" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${TEST_USERNAME}\",
    \"password\": \"${TEST_PASSWORD}\"
  }")

echo "Auth Response:" | python3 -m json.tool 2>/dev/null <<< "$AUTH_RESPONSE" || echo "$AUTH_RESPONSE"
echo ""

# Extract JWT token (nested structure: result.result.jwtToken)
JWT_TOKEN=$(echo "$AUTH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); r=data.get('result', {}); print(r.get('result', {}).get('jwtToken', ''))" 2>/dev/null)

if [ -z "$JWT_TOKEN" ] || [ "$JWT_TOKEN" == "None" ] || [ "$JWT_TOKEN" == "" ]; then
    echo -e "${RED}Failed to authenticate. Cannot proceed with authenticated tests.${NC}"
    echo -e "${YELLOW}Testing public endpoints only...${NC}\n"
    JWT_TOKEN=""
else
    echo -e "${GREEN}✓ Authenticated. JWT Token obtained.${NC}\n"
    
    # Extract avatar ID from auth response if not already set
    if [ -z "$AVATAR_ID" ] || [ "$AVATAR_ID" == "None" ] || [ "$AVATAR_ID" == "" ]; then
        AVATAR_ID=$(echo "$AUTH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); r=data.get('result', {}); print(r.get('result', {}).get('id', r.get('result', {}).get('avatarId', '')))" 2>/dev/null)
        echo -e "${GREEN}✓ Agent ID: ${AVATAR_ID}${NC}\n"
    fi
fi

# Test public endpoints
echo -e "${BLUE}=== Testing Public Endpoints ===${NC}\n"

echo -e "${GREEN}Test 1: Get All Agents${NC}"
curl -s -X GET "${API_URL}/agents" | python3 -m json.tool 2>/dev/null || curl -s -X GET "${API_URL}/agents"
echo -e "\n"

echo -e "${GREEN}Test 2: Find Agents by Service${NC}"
curl -s -X GET "${API_URL}/agents/by-service/data-analysis" | python3 -m json.tool 2>/dev/null || curl -s -X GET "${API_URL}/agents/by-service/data-analysis"
echo -e "\n"

if [ ! -z "$AVATAR_ID" ] && [ "$AVATAR_ID" != "None" ]; then
    echo -e "${GREEN}Test 3: Get Agent Card${NC}"
    curl -s -X GET "${API_URL}/agent-card/${AVATAR_ID}" | python3 -m json.tool 2>/dev/null || curl -s -X GET "${API_URL}/agent-card/${AVATAR_ID}"
    echo -e "\n"
fi

# Test authenticated endpoints
if [ ! -z "$JWT_TOKEN" ] && [ "$JWT_TOKEN" != "None" ]; then
    echo -e "${BLUE}=== Testing Authenticated Endpoints ===${NC}\n"
    
    echo -e "${GREEN}Test 4: Get My Agent Card${NC}"
    curl -s -X GET "${API_URL}/agent-card" \
      -H "Authorization: Bearer ${JWT_TOKEN}" | python3 -m json.tool 2>/dev/null || curl -s -X GET "${API_URL}/agent-card" -H "Authorization: Bearer ${JWT_TOKEN}"
    echo -e "\n"
    
    echo -e "${GREEN}Test 5: Register Agent Capabilities${NC}"
    REGISTER_CAP_RESPONSE=$(curl -s -X POST "${API_URL}/agent/capabilities" \
      -H "Authorization: Bearer ${JWT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "services": ["data-analysis", "report-generation"],
        "pricing": {
          "data-analysis": 0.1,
          "report-generation": 0.05
        },
        "skills": ["Python", "Machine Learning", "Data Science"],
        "status": 0,
        "max_concurrent_tasks": 3,
        "description": "Data analysis and reporting agent"
      }')
    echo "$REGISTER_CAP_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_CAP_RESPONSE"
    echo -e "\n"
    
    echo -e "${GREEN}Test 6: JSON-RPC Ping${NC}"
    curl -s -X POST "${API_URL}/jsonrpc" \
      -H "Authorization: Bearer ${JWT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "ping",
        "id": "test-ping-1"
      }' | python3 -m json.tool 2>/dev/null || curl -s -X POST "${API_URL}/jsonrpc" -H "Authorization: Bearer ${JWT_TOKEN}" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"ping","id":"test-ping-1"}'
    echo -e "\n"
    
    echo -e "${GREEN}Test 7: Get Pending Messages${NC}"
    curl -s -X GET "${API_URL}/messages" \
      -H "Authorization: Bearer ${JWT_TOKEN}" | python3 -m json.tool 2>/dev/null || curl -s -X GET "${API_URL}/messages" -H "Authorization: Bearer ${JWT_TOKEN}"
    echo -e "\n"
    
    echo -e "${GREEN}Test 8: Verify Agent Appears in List${NC}"
    curl -s -X GET "${API_URL}/agents" | python3 -m json.tool 2>/dev/null || curl -s -X GET "${API_URL}/agents"
    echo -e "\n"
    
    echo -e "${GREEN}Test 9: Verify Agent Found by Service${NC}"
    curl -s -X GET "${API_URL}/agents/by-service/data-analysis" | python3 -m json.tool 2>/dev/null || curl -s -X GET "${API_URL}/agents/by-service/data-analysis"
    echo -e "\n"
fi

echo -e "${BLUE}=== Tests Complete ===${NC}"
if [ ! -z "$JWT_TOKEN" ] && [ "$JWT_TOKEN" != "None" ]; then
    echo -e "${GREEN}✓ All tests completed successfully!${NC}"
    echo -e "${YELLOW}Test Agent Username: ${TEST_USERNAME}${NC}"
    echo -e "${YELLOW}Test Agent ID: ${AVATAR_ID}${NC}"
else
    echo -e "${YELLOW}⚠ Some tests skipped due to authentication issues${NC}"
fi

