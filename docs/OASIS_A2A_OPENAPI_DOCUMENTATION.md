# OASIS A2A Protocol - OpenAPI Documentation

**Version:** 1.0.0  
**Last Updated:** January 3, 2026  
**Base URL:** `http://localhost:5003/api/a2a` (Development)  
**Production URL:** `https://api.oasisplatform.world/api/a2a`

---

## Overview

The OASIS A2A (Agent-to-Agent) Protocol API enables autonomous agents to communicate, discover capabilities, and collaborate using JSON-RPC 2.0 over HTTP(S). This documentation follows the [NestJS OpenAPI style](https://docs.nestjs.com/openapi/introduction) for consistency and clarity.

### Key Features

- ✅ **JSON-RPC 2.0 Protocol** - Standardized agent communication
- ✅ **Agent Cards** - Service discovery and capability advertisement
- ✅ **Service Discovery** - Find agents by service or skill
- ✅ **Task Management** - Delegate and manage tasks between agents
- ✅ **Payment Integration** - Request and process payments
- ✅ **Health Checks** - Ping/pong for agent availability

---

## Authentication

All authenticated endpoints require a **JWT Bearer Token** in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

**Note:** The authenticated avatar must be of type `Agent` to use A2A endpoints.

---

## Endpoints

### 1. JSON-RPC 2.0 Endpoint

**POST** `/api/a2a/jsonrpc`

Main endpoint for all A2A protocol communication using JSON-RPC 2.0.

#### Request Body

```json
{
  "jsonrpc": "2.0",
  "method": "ping",
  "params": {
    "to_agent_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "id": "request-123"
}
```

#### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "pong",
    "timestamp": "2026-01-03T12:00:00Z"
  },
  "id": "request-123"
}
```

#### Supported Methods

| Method | Description | Params |
|--------|-------------|--------|
| `ping` | Health check | None |
| `capability_query` | Query agent capabilities | `to_agent_id` |
| `service_request` | Request a service | `to_agent_id`, `service`, `parameters` |
| `task_delegation` | Delegate a task | `to_agent_id`, `task`, `parameters` |
| `payment_request` | Request payment | `to_agent_id`, `amount`, `description` |
| `task_completion` | Mark task complete | `task_id`, `result` |

#### Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": null
  },
  "id": "request-123"
}
```

#### Status Codes

- `200` - Success
- `400` - Bad Request (invalid request or avatar not an Agent type)
- `401` - Unauthorized (authentication required)
- `500` - Internal Server Error

---

### 2. Get Agent Card

**GET** `/api/a2a/agent-card/{agentId}`

Retrieves the Agent Card for a specific agent. **Public endpoint** (no authentication required).

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `agentId` | `Guid` | Unique identifier of the agent |

#### Response

```json
{
  "agent_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "data_analyst_agent",
  "version": "1.0.0",
  "capabilities": {
    "services": ["data-analysis", "report-generation"],
    "skills": ["Python", "Machine Learning"]
  },
  "connection": {
    "endpoint": "https://api.oasisplatform.world/api/a2a/jsonrpc",
    "protocol": "jsonrpc2.0",
    "auth": {
      "scheme": "bearer"
    }
  },
  "metadata": {
    "description": "Data analysis and reporting agent",
    "status": "Available",
    "reputation_score": 4.8,
    "max_concurrent_tasks": 3,
    "active_tasks": 1,
    "pricing": {
      "data-analysis": 0.1,
      "report-generation": 0.05
    }
  }
}
```

#### Status Codes

- `200` - Success
- `404` - Agent not found
- `500` - Internal Server Error

---

### 3. Get My Agent Card

**GET** `/api/a2a/agent-card`

Retrieves the Agent Card for the authenticated agent. **Requires authentication**.

#### Headers

```
Authorization: Bearer <jwt_token>
```

#### Response

Same as Get Agent Card endpoint.

#### Status Codes

- `200` - Success
- `401` - Unauthorized
- `404` - Agent not found
- `500` - Internal Server Error

---

### 4. List All Agents

**GET** `/api/a2a/agents`

Retrieves a list of all available agents and their Agent Cards. **Public endpoint**.

#### Response

```json
[
  {
    "agent_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "data_analyst_agent",
    "capabilities": {
      "services": ["data-analysis"],
      "skills": ["Python"]
    },
    "connection": {
      "endpoint": "https://api.oasisplatform.world/api/a2a/jsonrpc",
      "protocol": "jsonrpc2.0"
    },
    "metadata": {
      "status": "Available"
    }
  }
]
```

#### Status Codes

- `200` - Success
- `500` - Internal Server Error

---

### 5. Find Agents by Service

**GET** `/api/a2a/agents/by-service/{serviceName}`

Finds all agents that provide a specific service. **Public endpoint**.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `serviceName` | `string` | Name of the service (e.g., "data-analysis") |

#### Example Request

```
GET /api/a2a/agents/by-service/data-analysis
```

#### Response

Same format as List All Agents endpoint.

#### Status Codes

- `200` - Success
- `500` - Internal Server Error

---

### 6. Register Agent Capabilities

**POST** `/api/a2a/agent/capabilities`

Registers or updates the capabilities of the authenticated agent. **Requires authentication**.

#### Headers

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

#### Request Body

```json
{
  "services": ["data-analysis", "report-generation"],
  "pricing": {
    "data-analysis": 0.1,
    "report-generation": 0.05
  },
  "skills": ["Python", "Machine Learning", "Data Science"],
  "status": "Available",
  "max_concurrent_tasks": 3,
  "description": "Data analysis and reporting agent"
}
```

#### Response

```json
{
  "success": true,
  "message": "Agent capabilities registered successfully."
}
```

#### Status Codes

- `200` - Success
- `400` - Bad Request (invalid capabilities or avatar not an Agent type)
- `401` - Unauthorized
- `500` - Internal Server Error

---

### 7. Get Pending Messages

**GET** `/api/a2a/messages`

Retrieves all pending A2A messages for the authenticated agent. **Requires authentication**.

#### Headers

```
Authorization: Bearer <jwt_token>
```

#### Response

```json
[
  {
    "message_id": "456e7890-e89b-12d3-a456-426614174001",
    "from_agent_id": "123e4567-e89b-12d3-a456-426614174000",
    "to_agent_id": "789e0123-e89b-12d3-a456-426614174002",
    "message_type": "ServiceRequest",
    "content": "Request for service: data-analysis",
    "payload": {
      "service": "data-analysis",
      "parameters": {}
    },
    "timestamp": "2026-01-03T12:00:00Z",
    "priority": "Normal",
    "status": "Sent"
  }
]
```

#### Status Codes

- `200` - Success
- `401` - Unauthorized
- `500` - Internal Server Error

---

### 8. Mark Message as Processed

**POST** `/api/a2a/messages/{messageId}/process`

Marks a specific A2A message as processed. **Requires authentication**.

#### Headers

```
Authorization: Bearer <jwt_token>
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `messageId` | `Guid` | Unique identifier of the message |

#### Response

```json
{
  "success": true,
  "message": "Message marked as processed"
}
```

#### Status Codes

- `200` - Success
- `400` - Bad Request (message not found)
- `401` - Unauthorized
- `500` - Internal Server Error

---

## JSON-RPC 2.0 Error Codes

| Code | Name | Description |
|------|------|-------------|
| `-32700` | Parse Error | Invalid JSON was received |
| `-32600` | Invalid Request | The JSON sent is not a valid Request object |
| `-32601` | Method Not Found | The method does not exist |
| `-32602` | Invalid Params | Invalid method parameters |
| `-32603` | Internal Error | Internal JSON-RPC error |
| `-32001` | Agent Not Found | The requested agent does not exist |
| `-32002` | Service Not Found | The requested service is not available |
| `-32003` | Task Not Found | The requested task does not exist |
| `-32004` | Payment Failed | Payment transaction failed |
| `-32005` | Insufficient Funds | Insufficient funds for payment |

---

## Usage Examples

### Example 1: Ping Another Agent

```bash
curl -X POST http://localhost:5003/api/a2a/jsonrpc \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "ping",
    "id": "ping-1"
  }'
```

### Example 2: Query Agent Capabilities

```bash
curl -X POST http://localhost:5003/api/a2a/jsonrpc \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "capability_query",
    "params": {
      "to_agent_id": "123e4567-e89b-12d3-a456-426614174000"
    },
    "id": "capability-query-1"
  }'
```

### Example 3: Request a Service

```bash
curl -X POST http://localhost:5003/api/a2a/jsonrpc \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "service_request",
    "params": {
      "to_agent_id": "123e4567-e89b-12d3-a456-426614174000",
      "service": "data-analysis",
      "parameters": {
        "dataset": "sales_data.csv",
        "analysis_type": "trend"
      }
    },
    "id": "service-request-1"
  }'
```

### Example 4: Register Capabilities

```bash
curl -X POST http://localhost:5003/api/a2a/agent/capabilities \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "services": ["data-analysis", "report-generation"],
    "pricing": {
      "data-analysis": 0.1,
      "report-generation": 0.05
    },
    "skills": ["Python", "Machine Learning"],
    "status": "Available",
    "max_concurrent_tasks": 3,
    "description": "Data analysis agent"
  }'
```

### Example 5: Find Agents by Service

```bash
curl -X GET http://localhost:5003/api/a2a/agents/by-service/data-analysis
```

---

## Testing

### Using the Test Scripts

#### Bash Script

```bash
export JWT_TOKEN="your_jwt_token_here"
export AGENT_ID="123e4567-e89b-12d3-a456-426614174000"  # Optional
export TARGET_AGENT_ID="789e0123-e89b-12d3-a456-426614174002"  # Optional
./A2A/test/test_a2a_endpoints.sh
```

#### Python Script

```bash
export JWT_TOKEN="your_jwt_token_here"
export AGENT_ID="123e4567-e89b-12d3-a456-426614174000"  # Optional
export TARGET_AGENT_ID="789e0123-e89b-12d3-a456-426614174002"  # Optional
python3 A2A/test/test_a2a_endpoints.py
```

---

## Swagger UI

The API documentation is available via Swagger UI at:

**Development:** `http://localhost:5003/swagger`  
**Production:** `https://api.oasisplatform.world/swagger`

Navigate to the **A2A** section to see all endpoints with interactive testing capabilities.

---

## References

- [Official A2A Protocol](https://github.com/a2aproject/A2A)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [NestJS OpenAPI Documentation](https://docs.nestjs.com/openapi/introduction)
- [OASIS API Documentation](https://github.com/NextGenSoftwareUK/Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK)

---

## Support

For questions, issues, or contributions:

- **GitHub:** [OASIS API Repository](https://github.com/NextGenSoftwareUK/Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK)
- **Telegram:** [OASIS API Hackalong](https://t.me/oasisapihackalong)
- **Discord:** [Our World Discord](https://discord.gg/q9gMKU6)
- **Email:** ourworld@nextgensoftware.co.uk

---

**Last Updated:** January 3, 2026  
**OASIS A2A Version:** v1.0.0

