# OpenSERV API Specification Document

**Date:** January 5, 2026  
**Status:** ✅ **Specification Complete**  
**Brief:** Brief 2 - OpenSERV API Research & Bridge Design

---

## Executive Summary

This document provides the complete API specification for OpenSERV integration, including API contracts, request/response schemas, error codes, and integration patterns. This specification serves as the contract between the C# bridge service and the OpenSERV platform.

---

## 1. API Base Information

### 1.1 Base URLs

| Environment | Base URL |
|------------|----------|
| Production | `https://api.openserv.ai` |
| Staging | `https://staging-api.openserv.ai` (if available) |
| Local Agent | `http://localhost:7378` |

### 1.2 API Version

- **Current Version:** v1
- **Version Header:** `X-API-Version: 1.0`
- **Version in Path:** `/api/v1/...`

### 1.3 Content Types

- **Request:** `application/json`
- **Response:** `application/json`
- **Character Encoding:** UTF-8

---

## 2. Authentication

### 2.1 API Key Authentication

All API requests require authentication using a Bearer token in the Authorization header.

**Header Format:**
```
Authorization: Bearer {OPENSERV_API_KEY}
```

**Example:**
```
Authorization: Bearer sk_live_abc123xyz789
```

### 2.2 Webhook Signature Verification

Webhook requests from OpenSERV include a signature for verification.

**Header Format:**
```
X-OpenSERV-Signature: sha256={signature}
```

**Verification Algorithm:**
1. Extract signature from header: `sha256={signature}`
2. Compute HMAC-SHA256 of request body using webhook secret
3. Compare signatures using constant-time comparison

---

## 3. API Endpoints

### 3.1 Agent Management

#### 3.1.1 Register Agent

**Endpoint:** `POST /api/v1/agents/register`

**Description:** Register a new agent with OpenSERV platform.

**Request Headers:**
```
Authorization: Bearer {api_key}
Content-Type: application/json
```

**Request Body:**
```json
{
  "agent_id": "string (required, unique)",
  "name": "string (required)",
  "description": "string (optional)",
  "endpoint": "string (required, HTTPS URL)",
  "capabilities": ["string"] (required, array of capability names),
  "metadata": {
    "key": "value"
  } (optional, key-value pairs)
}
```

**Request Schema:**
```typescript
interface RegisterAgentRequest {
  agent_id: string;
  name: string;
  description?: string;
  endpoint: string; // Must be HTTPS URL
  capabilities: string[];
  metadata?: Record<string, any>;
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "agent_id": "string",
  "status": "registered",
  "webhook_url": "https://api.openserv.ai/webhooks/{agent_id}",
  "registered_at": "2026-01-05T10:00:00Z"
}
```

**Response Schema:**
```typescript
interface RegisterAgentResponse {
  success: boolean;
  agent_id: string;
  status: "registered" | "pending" | "error";
  webhook_url: string;
  registered_at: string; // ISO 8601
}
```

**Error Responses:**

| Status Code | Error Code | Description |
|------------|------------|-------------|
| 400 | INVALID_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Invalid or missing API key |
| 409 | AGENT_EXISTS | Agent ID already registered |
| 429 | RATE_LIMIT | Rate limit exceeded |
| 500 | SERVER_ERROR | OpenSERV server error |

**Example Request:**
```bash
curl -X POST https://api.openserv.ai/api/v1/agents/register \
  -H "Authorization: Bearer sk_live_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent-001",
    "name": "My AI Agent",
    "description": "An AI agent for data analysis",
    "endpoint": "https://abc123.ngrok.io",
    "capabilities": ["nlp", "data-analysis", "reporting"],
    "metadata": {
      "version": "1.0.0",
      "author": "OASIS Team"
    }
  }'
```

**Example Response:**
```json
{
  "success": true,
  "agent_id": "my-agent-001",
  "status": "registered",
  "webhook_url": "https://api.openserv.ai/webhooks/my-agent-001",
  "registered_at": "2026-01-05T10:00:00Z"
}
```

---

#### 3.1.2 Get Agent Status

**Endpoint:** `GET /api/v1/agents/{agent_id}/status`

**Description:** Get the current status of a registered agent.

**Path Parameters:**
- `agent_id` (string, required): The unique identifier of the agent

**Request Headers:**
```
Authorization: Bearer {api_key}
```

**Response (200 OK):**
```json
{
  "agent_id": "string",
  "status": "online|offline|error",
  "last_seen": "2026-01-05T10:00:00Z",
  "endpoint": "https://abc123.ngrok.io",
  "capabilities": ["nlp", "data-analysis"],
  "health_check": {
    "status": "healthy|unhealthy",
    "response_time_ms": 123
  }
}
```

**Error Responses:**

| Status Code | Error Code | Description |
|------------|------------|-------------|
| 401 | UNAUTHORIZED | Invalid or missing API key |
| 404 | AGENT_NOT_FOUND | Agent not found |
| 429 | RATE_LIMIT | Rate limit exceeded |
| 500 | SERVER_ERROR | OpenSERV server error |

---

#### 3.1.3 Update Agent

**Endpoint:** `PUT /api/v1/agents/{agent_id}`

**Description:** Update agent information.

**Path Parameters:**
- `agent_id` (string, required): The unique identifier of the agent

**Request Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "endpoint": "string (optional, HTTPS URL)",
  "capabilities": ["string"] (optional),
  "metadata": {
    "key": "value"
  } (optional)
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "agent_id": "string",
  "status": "updated",
  "updated_at": "2026-01-05T10:00:00Z"
}
```

---

#### 3.1.4 List Agents

**Endpoint:** `GET /api/v1/agents`

**Description:** List all registered agents for the API key.

**Query Parameters:**
- `status` (string, optional): Filter by status (`online`, `offline`, `error`)
- `limit` (integer, optional): Maximum number of results (default: 50, max: 100)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
{
  "agents": [
    {
      "agent_id": "string",
      "name": "string",
      "status": "online|offline|error",
      "endpoint": "string",
      "capabilities": ["string"]
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

---

### 3.2 Workflow Execution

#### 3.2.1 Execute Workflow

**Endpoint:** `POST /api/v1/workflows/execute`

**Description:** Execute a workflow via an OpenSERV agent.

**Request Body:**
```json
{
  "workflow_id": "string (required)",
  "agent_id": "string (required)",
  "input": {
    "key": "value"
  } (required, workflow-specific input),
  "context": {
    "key": "value"
  } (optional, additional context),
  "async": false (optional, default: false)
}
```

**Request Schema:**
```typescript
interface ExecuteWorkflowRequest {
  workflow_id: string;
  agent_id: string;
  input: Record<string, any>;
  context?: Record<string, any>;
  async?: boolean; // If true, returns workflow_execution_id for polling
}
```

**Response (200 OK) - Synchronous:**
```json
{
  "workflow_id": "string",
  "workflow_execution_id": "string",
  "status": "completed",
  "result": {
    "key": "value"
  },
  "execution_time_ms": 1234,
  "completed_at": "2026-01-05T10:00:00Z"
}
```

**Response (202 Accepted) - Asynchronous:**
```json
{
  "workflow_id": "string",
  "workflow_execution_id": "string",
  "status": "running",
  "estimated_completion": "2026-01-05T10:05:00Z",
  "started_at": "2026-01-05T10:00:00Z"
}
```

**Response Schema:**
```typescript
interface ExecuteWorkflowResponse {
  workflow_id: string;
  workflow_execution_id: string;
  status: "running" | "completed" | "failed" | "cancelled";
  result?: Record<string, any>;
  execution_time_ms?: number;
  error_message?: string;
  estimated_completion?: string; // ISO 8601
  started_at?: string; // ISO 8601
  completed_at?: string; // ISO 8601
}
```

**Error Responses:**

| Status Code | Error Code | Description |
|------------|------------|-------------|
| 400 | INVALID_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Invalid or missing API key |
| 404 | AGENT_NOT_FOUND | Agent not found |
| 404 | WORKFLOW_NOT_FOUND | Workflow not found |
| 408 | WORKFLOW_TIMEOUT | Workflow execution timeout |
| 429 | RATE_LIMIT | Rate limit exceeded |
| 500 | SERVER_ERROR | OpenSERV server error |
| 503 | AGENT_OFFLINE | Agent endpoint not reachable |

**Example Request:**
```bash
curl -X POST https://api.openserv.ai/api/v1/workflows/execute \
  -H "Authorization: Bearer sk_live_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "nlp-analysis",
    "agent_id": "my-agent-001",
    "input": {
      "text": "Analyze this data and provide insights",
      "data": {
        "sales": [100, 200, 300],
        "period": "Q1 2026"
      }
    },
    "context": {
      "user_id": "user-123",
      "request_id": "req-456"
    },
    "async": false
  }'
```

**Example Response (Synchronous):**
```json
{
  "workflow_id": "nlp-analysis",
  "workflow_execution_id": "exec-789",
  "status": "completed",
  "result": {
    "insights": "Sales increased by 200% over the period",
    "confidence": 0.95,
    "recommendations": ["Continue current strategy", "Monitor Q2 performance"]
  },
  "execution_time_ms": 2345,
  "completed_at": "2026-01-05T10:00:02Z"
}
```

---

#### 3.2.2 Get Workflow Status

**Endpoint:** `GET /api/v1/workflows/{workflow_execution_id}/status`

**Description:** Get the status of an asynchronous workflow execution.

**Path Parameters:**
- `workflow_execution_id` (string, required): The workflow execution identifier

**Response (200 OK):**
```json
{
  "workflow_execution_id": "string",
  "workflow_id": "string",
  "status": "running|completed|failed|cancelled",
  "progress": 75, // Percentage (0-100)
  "result": {
    "key": "value"
  }, // Only present if status is "completed"
  "error_message": "string", // Only present if status is "failed"
  "estimated_completion": "2026-01-05T10:05:00Z",
  "started_at": "2026-01-05T10:00:00Z",
  "completed_at": "2026-01-05T10:05:00Z" // Only present if completed
}
```

**Error Responses:**

| Status Code | Error Code | Description |
|------------|------------|-------------|
| 401 | UNAUTHORIZED | Invalid or missing API key |
| 404 | EXECUTION_NOT_FOUND | Workflow execution not found |
| 429 | RATE_LIMIT | Rate limit exceeded |
| 500 | SERVER_ERROR | OpenSERV server error |

---

#### 3.2.3 Cancel Workflow

**Endpoint:** `POST /api/v1/workflows/{workflow_execution_id}/cancel`

**Description:** Cancel a running workflow execution.

**Path Parameters:**
- `workflow_execution_id` (string, required): The workflow execution identifier

**Response (200 OK):**
```json
{
  "workflow_execution_id": "string",
  "status": "cancelled",
  "cancelled_at": "2026-01-05T10:00:00Z"
}
```

---

### 3.3 Webhooks

#### 3.3.1 Webhook Events

OpenSERV sends webhooks to registered webhook URLs for the following events:

| Event Type | Description | Payload |
|-----------|-------------|---------|
| `workflow_request` | New workflow request for agent | Workflow request data |
| `workflow_complete` | Workflow execution completed | Workflow result |
| `workflow_failed` | Workflow execution failed | Error details |
| `agent_status_change` | Agent status changed | Status information |
| `error_notification` | Error occurred | Error details |

#### 3.3.2 Webhook Payload

**Headers:**
```
X-OpenSERV-Signature: sha256={signature}
X-OpenSERV-Event: {event_type}
X-OpenSERV-Timestamp: {unix_timestamp}
Content-Type: application/json
```

**Body:**
```json
{
  "event": "workflow_request|workflow_complete|workflow_failed|agent_status_change|error_notification",
  "timestamp": "2026-01-05T10:00:00Z",
  "data": {
    "workflow_id": "string",
    "workflow_execution_id": "string",
    "agent_id": "string",
    "result": {}, // For workflow_complete
    "error": {}, // For workflow_failed or error_notification
    "status": "string" // For agent_status_change
  }
}
```

**Webhook Signature Verification:**

1. Extract signature from `X-OpenSERV-Signature` header
2. Format: `sha256={signature}`
3. Compute HMAC-SHA256 of request body using webhook secret
4. Compare signatures using constant-time comparison

**Example Webhook Handler (C#):**
```csharp
[HttpPost("webhooks/openserv")]
public async Task<IActionResult> HandleWebhook(
    [FromHeader(Name = "X-OpenSERV-Signature")] string signature,
    [FromHeader(Name = "X-OpenSERV-Event")] string eventType,
    [FromBody] OpenServWebhookPayload payload)
{
    // Verify signature
    var requestBody = await Request.Body.ReadAsStringAsync();
    var secret = _configuration["OpenServ:WebhookSecret"];
    
    if (!_openServBridgeService.VerifyWebhookSignature(requestBody, signature, secret))
    {
        return Unauthorized("Invalid webhook signature");
    }
    
    // Process webhook based on event type
    switch (eventType)
    {
        case "workflow_complete":
            await HandleWorkflowComplete(payload);
            break;
        case "workflow_failed":
            await HandleWorkflowFailed(payload);
            break;
        // ... other event types
    }
    
    return Ok();
}
```

---

## 4. Error Handling

### 4.1 Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "key": "value"
    },
    "timestamp": "2026-01-05T10:00:00Z",
    "request_id": "req-123-456"
  }
}
```

### 4.2 Error Codes

| Error Code | HTTP Status | Description |
|-----------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `AGENT_NOT_FOUND` | 404 | Agent not found |
| `WORKFLOW_NOT_FOUND` | 404 | Workflow not found |
| `EXECUTION_NOT_FOUND` | 404 | Workflow execution not found |
| `AGENT_EXISTS` | 409 | Agent ID already registered |
| `WORKFLOW_TIMEOUT` | 408 | Workflow execution timeout |
| `RATE_LIMIT` | 429 | Rate limit exceeded |
| `AGENT_OFFLINE` | 503 | Agent endpoint not reachable |
| `SERVER_ERROR` | 500 | OpenSERV server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### 4.3 Retry Logic

**Retryable Errors:**
- `429` (Rate Limit) - Retry with exponential backoff
- `500` (Server Error) - Retry with exponential backoff
- `503` (Service Unavailable) - Retry with exponential backoff
- `408` (Timeout) - Retry with exponential backoff (if appropriate)

**Non-Retryable Errors:**
- `400` (Bad Request) - Do not retry
- `401` (Unauthorized) - Do not retry
- `403` (Forbidden) - Do not retry
- `404` (Not Found) - Do not retry
- `409` (Conflict) - Do not retry

**Retry Strategy:**
- Maximum retries: 3
- Exponential backoff: `2^attempt` seconds + jitter
- Check `Retry-After` header if present

---

## 5. Rate Limiting

### 5.1 Rate Limits

| Endpoint Type | Limit |
|--------------|-------|
| Agent Registration | 10 requests/minute |
| Workflow Execution | 50 requests/minute |
| Status Queries | 100 requests/minute |
| Webhook Deliveries | 200 webhooks/minute |

### 5.2 Rate Limit Headers

Response headers include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641388800
Retry-After: 60
```

### 5.3 Handling Rate Limits

When rate limit is exceeded:
1. Return `429 Too Many Requests`
2. Include `Retry-After` header with seconds to wait
3. Client should implement exponential backoff
4. Client should respect `Retry-After` header

---

## 6. Data Models

### 6.1 Agent Model

```typescript
interface Agent {
  agent_id: string;
  name: string;
  description?: string;
  endpoint: string;
  capabilities: string[];
  status: "online" | "offline" | "error";
  metadata?: Record<string, any>;
  registered_at: string; // ISO 8601
  last_seen?: string; // ISO 8601
}
```

### 6.2 Workflow Model

```typescript
interface Workflow {
  workflow_id: string;
  name: string;
  description?: string;
  agent_id: string;
  input_schema: Record<string, any>; // JSON Schema
  output_schema: Record<string, any>; // JSON Schema
  created_at: string; // ISO 8601
}
```

### 6.3 Workflow Execution Model

```typescript
interface WorkflowExecution {
  workflow_execution_id: string;
  workflow_id: string;
  agent_id: string;
  status: "running" | "completed" | "failed" | "cancelled";
  progress?: number; // 0-100
  result?: Record<string, any>;
  error_message?: string;
  started_at: string; // ISO 8601
  completed_at?: string; // ISO 8601
  execution_time_ms?: number;
}
```

---

## 7. Integration Patterns

### 7.1 Synchronous Workflow Execution

```
Client → OpenSERV API → Agent → Response → Client
```

**Use Case:** Quick operations (< 30 seconds)

### 7.2 Asynchronous Workflow Execution

```
Client → OpenSERV API → Workflow Execution ID
Client ← Poll Status ← OpenSERV API
Client ← Webhook ← OpenSERV API (when complete)
```

**Use Case:** Long-running operations (> 30 seconds)

### 7.3 Webhook-Based Integration

```
Client → OpenSERV API → Workflow Execution ID
OpenSERV → Webhook → Client (when complete)
```

**Use Case:** Event-driven architecture

---

## 8. Security Best Practices

1. **API Key Security:**
   - Store API keys in secure configuration
   - Never commit keys to source control
   - Rotate keys periodically
   - Use different keys for dev/staging/production

2. **Webhook Security:**
   - Always verify webhook signatures
   - Use HTTPS for webhook endpoints
   - Implement idempotency for webhook processing
   - Log all webhook events

3. **Request Validation:**
   - Validate all input parameters
   - Sanitize user input
   - Prevent injection attacks
   - Enforce rate limits

4. **TLS/HTTPS:**
   - Always use HTTPS for API calls
   - Verify SSL certificates
   - Use TLS 1.2 or higher

---

## 9. Testing

### 9.1 Test Endpoints

If available, use staging environment:
- Base URL: `https://staging-api.openserv.ai`
- Test API keys provided separately

### 9.2 Mock Server

For development, consider using a mock server:
- Mock OpenSERV API responses
- Test error scenarios
- Test retry logic

### 9.3 Integration Tests

1. Register test agent
2. Execute test workflow
3. Verify results
4. Test error scenarios
5. Test webhook handling

---

## 10. References

- **OpenSERV Platform:** https://www.openserv.ai
- **OpenSERV Documentation:** https://docs.openserv.ai
- **OpenSERV API Research:** `/A2A/docs/OPENSERV_API_RESEARCH.md`
- **Bridge Service Design:** `/A2A/docs/OPENSERV_BRIDGE_DESIGN.md`
- **A2A Integration:** `/A2A/docs/A2A_OPENSERV_INTEGRATION.md`

---

## 11. Notes & Assumptions

### Assumptions:
1. OpenSERV provides REST API (verify with official docs)
2. API follows standard REST conventions
3. Authentication uses Bearer tokens
4. Webhooks use HMAC-SHA256 signatures
5. Rate limits are as specified (verify with OpenSERV)

### Notes:
- Some endpoint details are inferred from SDK patterns
- Actual API may differ - verify with OpenSERV documentation
- Error codes are examples - verify actual error codes
- Rate limits are estimates - verify with OpenSERV support

---

**Last Updated:** January 5, 2026  
**Status:** ✅ Specification Complete - Ready for Implementation

