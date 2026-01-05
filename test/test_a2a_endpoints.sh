#!/bin/bash

# A2A Protocol Endpoint Test Script
# Tests all A2A endpoints with proper authentication

BASE_URL="${BASE_URL:-http://localhost:5003}"
API_URL="${BASE_URL}/api/a2a"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== A2A Protocol Endpoint Tests ===${NC}\n"

# Check if JWT token is provided
if [ -z "$JWT_TOKEN" ]; then
    echo -e "${RED}Error: JWT_TOKEN environment variable is required${NC}"
    echo "Usage: JWT_TOKEN='your_token_here' ./test_a2a_endpoints.sh"
    exit 1
fi

# Test 1: Ping (Health Check)
echo -e "${GREEN}Test 1: Ping (Health Check)${NC}"
PING_RESPONSE=$(curl -s -X POST "${API_URL}/jsonrpc" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "ping",
    "id": "test-ping-1"
  }')
echo "Response: $PING_RESPONSE"
echo ""

# Test 2: Get All Agents
echo -e "${GREEN}Test 2: Get All Agents${NC}"
AGENTS_RESPONSE=$(curl -s -X GET "${API_URL}/agents")
echo "Response: $AGENTS_RESPONSE"
echo ""

# Test 3: Get Agent Card (if agent ID is provided)
if [ ! -z "$AGENT_ID" ]; then
    echo -e "${GREEN}Test 3: Get Agent Card${NC}"
    AGENT_CARD_RESPONSE=$(curl -s -X GET "${API_URL}/agent-card/${AGENT_ID}")
    echo "Response: $AGENT_CARD_RESPONSE"
    echo ""
fi

# Test 4: Get My Agent Card
echo -e "${GREEN}Test 4: Get My Agent Card${NC}"
MY_AGENT_CARD_RESPONSE=$(curl -s -X GET "${API_URL}/agent-card" \
  -H "Authorization: Bearer ${JWT_TOKEN}")
echo "Response: $MY_AGENT_CARD_RESPONSE"
echo ""

# Test 5: Register Capabilities
echo -e "${GREEN}Test 5: Register Capabilities${NC}"
REGISTER_CAPABILITIES_RESPONSE=$(curl -s -X POST "${API_URL}/agent/capabilities" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "services": ["data-analysis", "report-generation"],
    "pricing": {
      "data-analysis": 0.1,
      "report-generation": 0.05
    },
    "skills": ["Python", "Machine Learning", "Data Science"],
    "status": "Available",
    "max_concurrent_tasks": 3,
    "description": "Data analysis and reporting agent"
  }')
echo "Response: $REGISTER_CAPABILITIES_RESPONSE"
echo ""

# Test 6: Capability Query
if [ ! -z "$TARGET_AGENT_ID" ]; then
    echo -e "${GREEN}Test 6: Capability Query${NC}"
    CAPABILITY_QUERY_RESPONSE=$(curl -s -X POST "${API_URL}/jsonrpc" \
      -H "Authorization: Bearer ${JWT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"capability_query\",
        \"params\": {
          \"to_agent_id\": \"${TARGET_AGENT_ID}\"
        },
        \"id\": \"test-capability-query-1\"
      }")
    echo "Response: $CAPABILITY_QUERY_RESPONSE"
    echo ""
fi

# Test 7: Service Request
if [ ! -z "$TARGET_AGENT_ID" ]; then
    echo -e "${GREEN}Test 7: Service Request${NC}"
    SERVICE_REQUEST_RESPONSE=$(curl -s -X POST "${API_URL}/jsonrpc" \
      -H "Authorization: Bearer ${JWT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"service_request\",
        \"params\": {
          \"to_agent_id\": \"${TARGET_AGENT_ID}\",
          \"service\": \"data-analysis\",
          \"parameters\": {
            \"dataset\": \"sales_data.csv\",
            \"analysis_type\": \"trend\"
          }
        },
        \"id\": \"test-service-request-1\"
      }")
    echo "Response: $SERVICE_REQUEST_RESPONSE"
    echo ""
fi

# Test 8: Get Pending Messages
echo -e "${GREEN}Test 8: Get Pending Messages${NC}"
MESSAGES_RESPONSE=$(curl -s -X GET "${API_URL}/messages" \
  -H "Authorization: Bearer ${JWT_TOKEN}")
echo "Response: $MESSAGES_RESPONSE"
echo ""

# Test 9: Find Agents by Service
echo -e "${GREEN}Test 9: Find Agents by Service${NC}"
AGENTS_BY_SERVICE_RESPONSE=$(curl -s -X GET "${API_URL}/agents/by-service/data-analysis")
echo "Response: $AGENTS_BY_SERVICE_RESPONSE"
echo ""

echo -e "${GREEN}=== Tests Complete ===${NC}"

