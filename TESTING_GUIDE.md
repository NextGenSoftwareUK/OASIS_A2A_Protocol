# A2A Protocol Testing Guide

**Date:** January 3, 2026  
**Status:** ✅ Ready for Testing

---

## Prerequisites

1. **API Running:** The OASIS API must be running on `http://localhost:5003`
2. **JWT Token:** You need a valid JWT token from an authenticated Agent avatar
3. **Agent Avatars:** At least one avatar must be registered as type `Agent`

---

## Quick Start

### 1. Get JWT Token

First, authenticate an Agent avatar:

```bash
curl -X POST http://localhost:5003/api/avatar/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "username": "agent_username",
    "password": "agent_password"
  }'
```

Save the `token` from the response.

### 2. Set Environment Variables

```bash
export JWT_TOKEN="your_jwt_token_here"
export AGENT_ID="123e4567-e89b-12d3-a456-426614174000"  # Optional
export TARGET_AGENT_ID="789e0123-e89b-12d3-a456-426614174002"  # Optional
```

### 3. Run Tests

#### Option A: Bash Script

```bash
cd A2A/test
./test_a2a_endpoints.sh
```

#### Option B: Python Script

```bash
cd A2A/test
python3 test_a2a_endpoints.py
```

---

## Manual Testing

### Test 1: Ping (Health Check)

```bash
curl -X POST http://localhost:5003/api/a2a/jsonrpc \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "ping",
    "id": "test-ping-1"
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "pong",
    "timestamp": "2026-01-03T12:00:00Z"
  },
  "id": "test-ping-1"
}
```

### Test 2: Get All Agents

```bash
curl -X GET http://localhost:5003/api/a2a/agents
```

**Expected Response:**
```json
[
  {
    "agent_id": "...",
    "name": "...",
    "capabilities": {...}
  }
]
```

### Test 3: Get Agent Card

```bash
curl -X GET http://localhost:5003/api/a2a/agent-card/${AGENT_ID}
```

### Test 4: Register Capabilities

```bash
curl -X POST http://localhost:5003/api/a2a/agent/capabilities \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "services": ["data-analysis"],
    "pricing": {
      "data-analysis": 0.1
    },
    "skills": ["Python"],
    "status": "Available",
    "max_concurrent_tasks": 3,
    "description": "Data analysis agent"
  }'
```

### Test 5: Capability Query

```bash
curl -X POST http://localhost:5003/api/a2a/jsonrpc \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"capability_query\",
    \"params\": {
      \"to_agent_id\": \"${TARGET_AGENT_ID}\"
    },
    \"id\": \"test-capability-query-1\"
  }"
```

### Test 6: Service Request

```bash
curl -X POST http://localhost:5003/api/a2a/jsonrpc \
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
  }"
```

### Test 7: Get Pending Messages

```bash
curl -X GET http://localhost:5003/api/a2a/messages \
  -H "Authorization: Bearer ${JWT_TOKEN}"
```

### Test 8: Find Agents by Service

```bash
curl -X GET http://localhost:5003/api/a2a/agents/by-service/data-analysis
```

---

## Swagger UI Testing

1. **Start the API:**
   ```bash
   cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI
   dotnet run --urls http://localhost:5003
   ```

2. **Open Swagger UI:**
   Navigate to: `http://localhost:5003/swagger`

3. **Authorize:**
   - Click the "Authorize" button
   - Enter: `Bearer <your_jwt_token>`
   - Click "Authorize"

4. **Test Endpoints:**
   - Navigate to the **A2A** section
   - Try each endpoint using the "Try it out" button
   - View request/response examples

---

## Common Issues

### Issue 1: "Authentication required"

**Solution:** Make sure you're including the JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

### Issue 2: "Avatar must be of type Agent"

**Solution:** The authenticated avatar must be registered as type `Agent`. Check the avatar's `AvatarType` field.

### Issue 3: "Agent not found"

**Solution:** Make sure the agent ID exists and the agent has registered capabilities.

### Issue 4: "Method not found"

**Solution:** Check that the JSON-RPC method name is correct (e.g., `ping`, `capability_query`, `service_request`).

---

## Test Checklist

- [ ] Ping endpoint works
- [ ] Get all agents returns list
- [ ] Get agent card returns valid card
- [ ] Register capabilities succeeds
- [ ] Capability query returns capabilities
- [ ] Service request creates message
- [ ] Get pending messages returns messages
- [ ] Find agents by service returns filtered list
- [ ] Mark message processed works
- [ ] Error handling works correctly

---

## Next Steps

1. ✅ Run all test scripts
2. ✅ Verify Swagger UI documentation
3. ✅ Test with multiple agents
4. ✅ Test error scenarios
5. ✅ Integration testing with payment demo

---

**Last Updated:** January 3, 2026

