# A2A Protocol Integration Troubleshooting Guide

**Date:** January 5, 2026  
**Version:** 1.0.0

---

## Overview

This guide helps diagnose and resolve common issues when integrating A2A Protocol with SERV infrastructure and OpenSERV agents.

---

## Table of Contents

- [General Troubleshooting](#general-troubleshooting)
- [A2A-SERV Integration Issues](#a2a-serv-integration-issues)
- [A2A-OpenSERV Integration Issues](#a2a-openserv-integration-issues)
- [Authentication Issues](#authentication-issues)
- [Service Discovery Issues](#service-discovery-issues)
- [Workflow Execution Issues](#workflow-execution-issues)
- [Error Codes Reference](#error-codes-reference)
- [Debugging Tips](#debugging-tips)

---

## General Troubleshooting

### Check API Availability

```bash
# Test API is running
curl http://localhost:5003/api/a2a/agents

# Expected: JSON response with agents list
```

### Verify Environment Variables

```bash
# Check required environment variables
echo $BASE_URL
echo $JWT_TOKEN
echo $AGENT_ID
```

### Check Logs

- **OASIS API Logs**: Check console output or log files
- **SERV Infrastructure Logs**: Check ONET Unified Architecture logs
- **OpenSERV Logs**: Check OpenSERV platform logs (if applicable)

---

## A2A-SERV Integration Issues

### Issue: Agent Not Discoverable via SERV

**Symptoms:**
- Agent registered but not appearing in SERV discovery
- `GET /api/a2a/agents/discover-serv` returns empty list

**Possible Causes:**

1. **Agent not registered as SERV service**
   ```bash
   # Verify registration
   curl -X POST http://localhost:5003/api/a2a/agent/register-service \
     -H "Authorization: Bearer $JWT_TOKEN"
   ```

2. **SERV infrastructure not initialized**
   - Check ONET Unified Architecture is running
   - Verify UnifiedService registry is available

3. **Service registration failed silently**
   - Check API logs for errors
   - Verify agent capabilities are registered first

**Solutions:**

```python
# Ensure proper registration flow
# 1. Register capabilities
capabilities = {
    "services": ["data-analysis"],
    "status": "Available"
}
requests.post(f"{API_URL}/agent/capabilities", 
              headers={"Authorization": f"Bearer {token}"},
              json=capabilities)

# 2. Register as SERV service
requests.post(f"{API_URL}/agent/register-service",
              headers={"Authorization": f"Bearer {token}"})

# 3. Wait a moment for registration
import time
time.sleep(2)

# 4. Verify discovery
response = requests.get(f"{API_URL}/agents/discover-serv")
agents = response.json()
```

### Issue: Service Registration Returns 400 Error

**Symptoms:**
- `POST /api/a2a/agent/register-service` returns 400 Bad Request

**Possible Causes:**

1. **Agent capabilities not registered**
   - Register capabilities first: `POST /api/a2a/agent/capabilities`

2. **Agent card not found**
   - Verify agent ID is correct
   - Check agent exists in system

**Solutions:**

```python
# Verify agent card exists
response = requests.get(f"{API_URL}/agent-card/{agent_id}")
if response.status_code != 200:
    print("Agent card not found - register capabilities first")
```

### Issue: Service Discovery Returns Wrong Agents

**Symptoms:**
- Service filter not working correctly
- Agents without requested service appear in results

**Possible Causes:**

1. **Service name mismatch (case-sensitive)**
   - Service names are case-sensitive
   - Verify exact service name

2. **Multiple service registrations**
   - Agent may be registered multiple times
   - Check for duplicate registrations

**Solutions:**

```python
# Use exact service name
response = requests.get(
    f"{API_URL}/agents/discover-serv",
    params={"service": "data-analysis"}  # Exact match required
)

# Verify service in agent capabilities
for agent in agents:
    services = agent.get("capabilities", {}).get("services", [])
    if "data-analysis" not in services:
        print(f"Agent {agent['agentId']} missing service")
```

---

## A2A-OpenSERV Integration Issues

### Issue: OpenSERV Agent Registration Fails

**Symptoms:**
- `POST /api/a2a/openserv/register` returns error
- Agent not created

**Possible Causes:**

1. **Missing required fields**
   - `openServAgentId` is required
   - `openServEndpoint` is required
   - `capabilities` list is required

2. **Invalid endpoint URL**
   - Endpoint must be valid HTTP/HTTPS URL
   - Check endpoint is accessible

3. **Avatar creation fails**
   - Username may already exist
   - Email validation fails

**Solutions:**

```python
# Verify required fields
payload = {
    "openServAgentId": "agent-123",  # Required
    "openServEndpoint": "https://api.openserv.ai/agents/agent-123",  # Required
    "capabilities": ["data-analysis"]  # Required, non-empty
}

# Use unique agent ID
import uuid
agent_id = f"agent-{uuid.uuid4().hex[:8]}"

# Test endpoint accessibility
response = requests.get(openserv_endpoint, timeout=5)
if response.status_code not in [200, 401, 403]:
    print("Warning: OpenSERV endpoint may not be accessible")
```

### Issue: Workflow Execution Fails

**Symptoms:**
- `POST /api/a2a/workflow/execute` returns error
- Workflow not executed

**Possible Causes:**

1. **OpenSERV endpoint not found**
   - Agent not registered as OpenSERV agent
   - Metadata missing `openserv_endpoint`

2. **OpenSERV API error**
   - Invalid API key
   - Endpoint not accessible
   - Workflow request format incorrect

3. **Authentication failure**
   - JWT token invalid or expired
   - Avatar not of type Agent

**Solutions:**

```python
# Verify agent is OpenSERV agent
response = requests.get(f"{API_URL}/agent-card/{agent_id}")
agent_card = response.json()
metadata = agent_card.get("metadata", {})

if "openserv_endpoint" not in metadata:
    print("Error: Agent is not an OpenSERV agent")
    print("Register agent with /api/a2a/openserv/register first")

# Test OpenSERV endpoint directly
openserv_endpoint = metadata.get("openserv_endpoint")
api_key = metadata.get("openserv_api_key")

headers = {}
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"

test_response = requests.post(
    openserv_endpoint,
    json={"test": "connection"},
    headers=headers,
    timeout=10
)
print(f"OpenSERV endpoint status: {test_response.status_code}")
```

### Issue: Workflow Returns Empty Result

**Symptoms:**
- Workflow execution succeeds but result is empty
- No response from OpenSERV agent

**Possible Causes:**

1. **OpenSERV agent not responding**
   - Check OpenSERV platform status
   - Verify agent is active

2. **Workflow timeout**
   - Workflow execution taking too long
   - Increase timeout if needed

**Solutions:**

```python
# Add timeout and error handling
try:
    response = requests.post(
        f"{API_URL}/workflow/execute",
        headers={"Authorization": f"Bearer {token}"},
        json=workflow_request,
        timeout=60  # Increase timeout for long-running workflows
    )
    if response.status_code == 200:
        result = response.json()
        if not result.get("result"):
            print("Warning: Workflow returned empty result")
except requests.Timeout:
    print("Error: Workflow execution timed out")
```

---

## Authentication Issues

### Issue: 401 Unauthorized Error

**Symptoms:**
- All requests return 401 Unauthorized
- JWT token not accepted

**Possible Causes:**

1. **Invalid or expired token**
   - Token may have expired
   - Token format incorrect

2. **Missing Authorization header**
   - Header not included in request
   - Header format incorrect

**Solutions:**

```python
# Verify token format
token = "Bearer " + jwt_token  # Correct format

# Test authentication
response = requests.get(
    f"{API_URL}/agent-card",
    headers={"Authorization": f"Bearer {jwt_token}"}
)

if response.status_code == 401:
    print("Token is invalid or expired")
    print("Re-authenticate to get new token")

# Re-authenticate
auth_response = requests.post(
    f"{BASE_URL}/api/avatar/authenticate",
    json={"username": username, "password": password}
)
new_token = auth_response.json()["result"]["token"]
```

### Issue: 400 Bad Request - "Avatar must be of type Agent"

**Symptoms:**
- Request fails with "Avatar must be of type Agent" error
- Avatar exists but wrong type

**Possible Causes:**

1. **Avatar type is User, not Agent**
   - Avatar created with wrong type
   - Cannot be changed after creation

**Solutions:**

```python
# Create new avatar with Agent type
register_payload = {
    "username": "agent_user",
    "email": "agent@example.com",
    "password": "password",
    "avatarType": "Agent"  # Must be "Agent" type
}

response = requests.post(
    f"{BASE_URL}/api/avatar/register",
    json=register_payload
)
```

---

## Service Discovery Issues

### Issue: No Agents Found

**Symptoms:**
- `GET /api/a2a/agents/discover-serv` returns empty list
- No agents discoverable

**Possible Causes:**

1. **No agents registered**
   - Agents not registered as SERV services
   - SERV infrastructure empty

2. **Service filter too restrictive**
   - Service name doesn't match any agents
   - Try without service filter

**Solutions:**

```python
# Try discovery without filter
response = requests.get(f"{API_URL}/agents/discover-serv")
all_agents = response.json()
print(f"Total agents: {len(all_agents)}")

# Check service names
for agent in all_agents:
    services = agent.get("capabilities", {}).get("services", [])
    print(f"Agent {agent['agentId']}: {services}")
```

### Issue: Agents Not Filtered Correctly

**Symptoms:**
- Service filter doesn't work
- Wrong agents returned

**Possible Causes:**

1. **Case sensitivity**
   - Service names are case-sensitive
   - Use exact match

2. **Partial matches**
   - Filter uses exact match, not substring
   - Verify exact service name

**Solutions:**

```python
# Use exact service name (case-sensitive)
response = requests.get(
    f"{API_URL}/agents/discover-serv",
    params={"service": "data-analysis"}  # Must match exactly
)

# Verify services in results
for agent in agents:
    services = agent.get("capabilities", {}).get("services", [])
    if "data-analysis" not in services:
        print(f"Warning: Agent {agent['agentId']} doesn't have service")
```

---

## Workflow Execution Issues

### Issue: Workflow Execution Timeout

**Symptoms:**
- Workflow execution hangs
- Request times out

**Possible Causes:**

1. **OpenSERV agent slow to respond**
   - Agent processing takes time
   - Network latency

2. **Default timeout too short**
   - Increase timeout value

**Solutions:**

```python
# Increase timeout for long-running workflows
response = requests.post(
    f"{API_URL}/workflow/execute",
    headers={"Authorization": f"Bearer {token}"},
    json=workflow_request,
    timeout=120  # 2 minutes timeout
)
```

### Issue: Workflow Returns Error

**Symptoms:**
- Workflow execution returns error
- OpenSERV agent rejects request

**Possible Causes:**

1. **Invalid workflow request format**
   - Check OpenSERV API documentation
   - Verify request structure

2. **Missing required parameters**
   - Add required parameters
   - Check OpenSERV agent requirements

**Solutions:**

```python
# Verify workflow request format
workflow_request = {
    "toAgentId": agent_id,
    "workflowRequest": "Clear, specific workflow description",
    "workflowParameters": {
        "required_param": "value"
    }
}

# Check error message
response = requests.post(...)
if response.status_code != 200:
    error_data = response.json()
    print(f"Error: {error_data.get('error')}")
```

---

## Error Codes Reference

| Status Code | Meaning | Solution |
|-------------|---------|----------|
| 200 | Success | - |
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Verify JWT token |
| 404 | Not Found | Check agent ID or endpoint |
| 500 | Internal Server Error | Check server logs |

### Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Authentication required" | Missing or invalid token | Re-authenticate |
| "Avatar must be of type Agent" | Wrong avatar type | Create Agent-type avatar |
| "Agent card not found" | Capabilities not registered | Register capabilities first |
| "OpenSERV endpoint not found" | Agent not OpenSERV agent | Register as OpenSERV agent |
| "Workflow execution failed" | OpenSERV API error | Check OpenSERV endpoint and API key |

---

## Debugging Tips

### Enable Verbose Logging

```python
import logging
import requests

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests.packages.urllib3").setLevel(logging.DEBUG)

# Log request/response
response = requests.post(...)
print(f"Request: {response.request.method} {response.request.url}")
print(f"Request Headers: {dict(response.request.headers)}")
print(f"Request Body: {response.request.body}")
print(f"Response Status: {response.status_code}")
print(f"Response Body: {response.text}")
```

### Test Components Individually

```python
# 1. Test authentication
auth_response = requests.post(f"{BASE_URL}/api/avatar/authenticate", ...)
print(f"Auth: {auth_response.status_code}")

# 2. Test capability registration
cap_response = requests.post(f"{API_URL}/agent/capabilities", ...)
print(f"Capabilities: {cap_response.status_code}")

# 3. Test SERV registration
serv_response = requests.post(f"{API_URL}/agent/register-service", ...)
print(f"SERV: {serv_response.status_code}")

# 4. Test discovery
discover_response = requests.get(f"{API_URL}/agents/discover-serv")
print(f"Discovery: {discover_response.status_code}")
```

### Check Agent State

```python
# Get agent card to check state
response = requests.get(f"{API_URL}/agent-card/{agent_id}")
agent_card = response.json()

print(f"Agent ID: {agent_card.get('agentId')}")
print(f"Services: {agent_card.get('capabilities', {}).get('services')}")
print(f"Metadata: {agent_card.get('metadata')}")
print(f"Connection: {agent_card.get('connection')}")
```

---

## Getting Help

If you continue to experience issues:

1. **Check Documentation**
   - [Integration Guide](INTEGRATION_GUIDE.md)
   - [API Documentation](OASIS_A2A_OPENAPI_DOCUMENTATION.md)
   - [Integration Plan](A2A_OPENSERV_INTEGRATION.md)

2. **Review Logs**
   - Check OASIS API logs
   - Check SERV infrastructure logs
   - Check OpenSERV platform logs

3. **Test with Demo Scripts**
   - Run `a2a_serv_discovery_demo.py`
   - Run `a2a_openserv_workflow_demo.py`
   - Compare with your implementation

4. **Verify Configuration**
   - Check all environment variables
   - Verify API endpoints
   - Confirm authentication credentials

---

**Last Updated:** January 5, 2026  
**Version:** 1.0.0

