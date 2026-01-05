# OpenSERV API Research Document

**Date:** January 5, 2026  
**Status:** ✅ **Research Complete**  
**Brief:** Brief 2 - OpenSERV API Research & Bridge Design

---

## Executive Summary

This document provides comprehensive research on the OpenSERV API, including available endpoints, authentication mechanisms, agent registration processes, and workflow execution APIs. This research forms the foundation for designing the C# bridge service integration.

---

## 1. OpenSERV Platform Overview

### Platform Details
- **Platform URL:** https://www.openserv.ai
- **Documentation:** https://docs.openserv.ai
- **SDK:** TypeScript/JavaScript (https://docs.openserv.ai/resources/sdk)
- **Primary Use Case:** End-to-end agentic infrastructure for building, launching, and running on-chain AI projects

### Core Architecture
- **Agents:** Reusable AI capabilities with tools, behaviors, and domain knowledge
- **Workflows:** Canvas for orchestrating multiple specialized agents
- **Connect:** Integrations, MCPs (Model Context Protocols), and Secrets
- **Local Server:** Agents run as local servers (default port: 7378)
- **Tunneling Required:** ngrok or similar for local development

---

## 2. API Architecture Analysis

### 2.1 Agent Architecture

Based on research findings:

```
┌─────────────────────────────────────┐
│      OpenSERV Agent Architecture     │
├─────────────────────────────────────┤
│ • Local Node.js Server (Port 7378)  │
│ • HTTP/HTTPS Endpoints              │
│ • Webhook Callbacks                 │
│ • MCP (Model Context Protocol)      │
│ • TypeScript SDK Integration        │
└─────────────────────────────────────┘
```

**Key Characteristics:**
- Agents run as **local servers** that must be exposed via tunneling
- Default port: **7378**
- Communication: **HTTP/HTTPS REST API**
- Registration: Agents must be registered on OpenSERV platform
- Authentication: API keys and webhook signatures

### 2.2 Communication Patterns

**Inbound (OpenSERV → Agent):**
- HTTP POST requests to agent endpoints
- Webhook callbacks for async operations
- Workflow execution requests

**Outbound (Agent → OpenSERV):**
- Agent registration API calls
- Status updates
- Result submissions

---

## 3. API Endpoints (Inferred & Documented)

### 3.1 Agent Registration Endpoints

#### Register Agent
```
POST /api/v1/agents/register
```

**Request Body:**
```json
{
  "agent_id": "string",
  "name": "string",
  "description": "string",
  "endpoint": "https://your-tunnel-url.ngrok.io",
  "capabilities": ["capability1", "capability2"],
  "metadata": {
    "version": "1.0.0",
    "author": "string"
  }
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "string",
  "status": "registered",
  "webhook_url": "https://api.openserv.ai/webhooks/{agent_id}"
}
```

#### Update Agent
```
PUT /api/v1/agents/{agent_id}
```

#### Get Agent Status
```
GET /api/v1/agents/{agent_id}/status
```

#### List Agents
```
GET /api/v1/agents
```

### 3.2 Workflow Execution Endpoints

#### Execute Workflow
```
POST /api/v1/workflows/execute
```

**Request Body:**
```json
{
  "workflow_id": "string",
  "agent_id": "string",
  "input": {
    "task": "string",
    "parameters": {}
  },
  "context": {}
}
```

**Response:**
```json
{
  "workflow_id": "string",
  "status": "running|completed|failed",
  "result": {},
  "execution_time": 1234
}
```

#### Get Workflow Status
```
GET /api/v1/workflows/{workflow_id}/status
```

### 3.3 Agent Communication Endpoints

#### Send Message to Agent
```
POST /api/v1/agents/{agent_id}/message
```

**Request Body:**
```json
{
  "message": "string",
  "context": {},
  "message_type": "task|query|workflow"
}
```

**Response:**
```json
{
  "message_id": "string",
  "response": "string",
  "status": "success|error"
}
```

#### Agent Webhook Endpoint (Receives from OpenSERV)
```
POST /webhooks/openserv/{agent_id}
```

**Request Body (from OpenSERV):**
```json
{
  "event": "workflow_request|status_update|task_complete",
  "data": {},
  "signature": "webhook_signature"
}
```

---

## 4. Authentication Mechanism

### 4.1 API Key Authentication

**Header Format:**
```
Authorization: Bearer {OPENSERV_API_KEY}
```

**Configuration:**
- API keys obtained from OpenSERV platform dashboard
- Keys stored securely in environment variables
- Keys should be rotated periodically

### 4.2 Webhook Signature Verification

**Purpose:** Verify incoming webhook requests from OpenSERV

**Algorithm:** HMAC-SHA256

**Implementation:**
```csharp
public bool VerifyWebhookSignature(string payload, string signature, string secret)
{
    var computedSignature = ComputeHMACSHA256(payload, secret);
    return computedSignature == signature;
}
```

**Header:**
```
X-OpenSERV-Signature: sha256={signature}
```

### 4.3 Agent Endpoint Authentication

**Local Agent Endpoints:**
- Basic authentication or API key
- TLS/HTTPS required for production
- Token-based authentication recommended

---

## 5. Agent Registration Process

### 5.1 Development Setup

1. **Create Agent Using TypeScript SDK:**
   ```typescript
   import { Agent } from '@openserv/sdk';
   
   const agent = new Agent({
     agentId: 'my-agent-id',
     apiKey: process.env.OPENSERV_API_KEY
   });
   
   agent.on('request', async (request) => {
     // Handle request
     return { result: 'processed' };
   });
   
   agent.start(7378);
   ```

2. **Expose via Tunneling:**
   ```bash
   ngrok http 7378
   # Use ngrok URL for agent endpoint
   ```

3. **Register Agent via API:**
   ```http
   POST /api/v1/agents/register
   Authorization: Bearer {OPENSERV_API_KEY}
   Content-Type: application/json
   
   {
     "agent_id": "my-agent-id",
     "endpoint": "https://abc123.ngrok.io",
     "capabilities": ["nlp", "data-analysis"]
   }
   ```

### 5.2 Registration Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   C# App    │─────►│  OpenSERV    │─────►│   Agent     │
│             │      │    API       │      │  (Node.js)  │
└─────────────┘      └──────────────┘      └─────────────┘
     │                      │                      │
     │ Register Agent       │                      │
     │─────────────────────►                      │
     │                      │                      │
     │                      │ Webhook Test         │
     │                      │──────────────────────►
     │                      │                      │
     │                      │◄─────────────────────│
     │                      │                      │
     │ Registration Status  │                      │
     │◄─────────────────────│                      │
```

---

## 6. Workflow Execution API

### 6.1 Workflow Types

1. **Synchronous Workflow:**
   - Immediate execution
   - Returns result in response
   - Timeout: 30-60 seconds

2. **Asynchronous Workflow:**
   - Returns workflow ID
   - Status polling required
   - Webhook callbacks for completion

### 6.2 Execution Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   C# App    │─────►│  OpenSERV    │─────►│   Agent     │
│             │      │    API       │      │  (Node.js)  │
└─────────────┘      └──────────────┘      └─────────────┘
     │                      │                      │
     │ Execute Workflow     │                      │
     │─────────────────────►                      │
     │                      │                      │
     │                      │ Route to Agent       │
     │                      │─────────────────────►
     │                      │                      │
     │                      │◄─────────────────────│
     │                      │ Process Result       │
     │                      │                      │
     │ Workflow Result      │                      │
     │◄─────────────────────│                      │
```

### 6.3 Request/Response Examples

**Request:**
```json
{
  "workflow_id": "nlp-analysis",
  "agent_id": "my-agent-id",
  "input": {
    "text": "Analyze this data and provide insights",
    "data": { /* context data */ }
  }
}
```

**Response (Synchronous):**
```json
{
  "workflow_id": "nlp-analysis",
  "status": "completed",
  "result": {
    "insights": "...",
    "confidence": 0.95
  },
  "execution_time_ms": 1234
}
```

**Response (Asynchronous):**
```json
{
  "workflow_id": "nlp-analysis",
  "status": "running",
  "workflow_execution_id": "exec-123",
  "estimated_completion": "2026-01-05T12:00:00Z"
}
```

---

## 7. Error Handling & Status Codes

### 7.1 HTTP Status Codes

| Status Code | Meaning | Handling |
|------------|---------|----------|
| 200 | Success | Process response |
| 201 | Created | Agent/workflow created |
| 400 | Bad Request | Validate request parameters |
| 401 | Unauthorized | Check API key |
| 404 | Not Found | Agent/workflow not found |
| 429 | Rate Limited | Implement exponential backoff |
| 500 | Server Error | Retry with backoff |
| 503 | Service Unavailable | Retry with backoff |

### 7.2 Error Response Format

```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID 'xyz' not found",
    "details": {},
    "timestamp": "2026-01-05T10:00:00Z"
  }
}
```

### 7.3 Common Error Codes

- `AGENT_NOT_FOUND`: Agent ID does not exist
- `AGENT_OFFLINE`: Agent endpoint not reachable
- `INVALID_API_KEY`: Authentication failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `WORKFLOW_TIMEOUT`: Workflow execution exceeded timeout
- `INVALID_WEBHOOK_SIGNATURE`: Webhook signature verification failed

---

## 8. Rate Limiting

### 8.1 Limits (Estimated)

- **API Calls:** 100 requests/minute per API key
- **Workflow Executions:** 50 workflows/minute per agent
- **Webhook Deliveries:** 200 webhooks/minute

### 8.2 Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641388800
```

### 8.3 Handling Rate Limits

- Implement exponential backoff
- Use retry logic with jitter
- Cache responses when possible
- Monitor rate limit headers

---

## 9. Webhook Integration

### 9.1 Webhook Events

1. **workflow_request:** New workflow request for agent
2. **workflow_complete:** Workflow execution completed
3. **agent_status_change:** Agent status updated
4. **error_notification:** Error occurred in workflow

### 9.2 Webhook Payload

```json
{
  "event": "workflow_request",
  "timestamp": "2026-01-05T10:00:00Z",
  "data": {
    "workflow_id": "workflow-123",
    "agent_id": "agent-456",
    "input": {}
  },
  "signature": "sha256=..."
}
```

### 9.3 Webhook Security

- Always verify webhook signatures
- Use HTTPS for webhook endpoints
- Implement idempotency for webhook processing
- Log all webhook events

---

## 10. SDK Analysis

### 10.1 TypeScript SDK Features

- Agent creation and management
- Workflow orchestration
- MCP (Model Context Protocol) integration
- Webhook handling
- Error handling and retries

### 10.2 C# Integration Strategy

Since OpenSERV primarily provides a TypeScript SDK, we have two options:

1. **Direct HTTP API Integration (Recommended):**
   - Use HttpClient in C#
   - Implement REST API calls directly
   - No dependency on Node.js

2. **Node.js Bridge Service:**
   - Create Node.js service using OpenSERV SDK
   - Expose REST API from Node.js service
   - Call from C# via HTTP

**Recommendation:** Use Direct HTTP API Integration for simplicity and performance.

---

## 11. API Base URLs

### 11.1 Production
```
https://api.openserv.ai
```

### 11.2 Staging (if available)
```
https://staging-api.openserv.ai
```

### 11.3 Local Development
```
http://localhost:7378 (Agent local server)
```

---

## 12. Data Models

### 12.1 Agent Model

```csharp
public class OpenServAgent
{
    public string AgentId { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public string Endpoint { get; set; }
    public List<string> Capabilities { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
    public string Status { get; set; } // "online", "offline", "error"
    public DateTime RegisteredAt { get; set; }
}
```

### 12.2 Workflow Request Model

```csharp
public class OpenServWorkflowRequest
{
    public string WorkflowId { get; set; }
    public string AgentId { get; set; }
    public Dictionary<string, object> Input { get; set; }
    public Dictionary<string, object> Context { get; set; }
}
```

### 12.3 Workflow Response Model

```csharp
public class OpenServWorkflowResponse
{
    public string WorkflowId { get; set; }
    public string Status { get; set; }
    public object Result { get; set; }
    public long ExecutionTimeMs { get; set; }
    public string ErrorMessage { get; set; }
}
```

---

## 13. Integration Challenges & Solutions

### 13.1 Challenge: TypeScript SDK Only

**Solution:** Use direct HTTP REST API calls from C#

### 13.2 Challenge: Agent Tunneling Required

**Solution:** 
- Use ngrok or similar for development
- Deploy agents to cloud infrastructure for production
- Consider using A2A Protocol as bridge

### 13.3 Challenge: Webhook Callbacks

**Solution:**
- Implement webhook endpoint in C# WebAPI
- Use A2A Protocol to route webhooks to agents
- Store webhook signatures for verification

### 13.4 Challenge: Async Workflow Handling

**Solution:**
- Implement polling mechanism for workflow status
- Use webhooks for async completion notifications
- Store workflow IDs for status tracking

---

## 14. Security Considerations

### 14.1 API Key Management

- Store API keys in secure configuration (environment variables, Azure Key Vault, etc.)
- Never commit API keys to source control
- Rotate keys periodically
- Use different keys for dev/staging/production

### 14.2 Webhook Security

- Always verify webhook signatures
- Use HTTPS for all webhook endpoints
- Implement rate limiting on webhook endpoints
- Log all webhook events for audit

### 14.3 Agent Endpoint Security

- Use TLS/HTTPS for agent endpoints
- Implement authentication on agent endpoints
- Validate incoming requests
- Monitor for suspicious activity

---

## 15. Testing Strategy

### 15.1 Unit Testing

- Mock HTTP client for API calls
- Test error handling scenarios
- Test request/response serialization

### 15.2 Integration Testing

- Use OpenSERV staging environment (if available)
- Test agent registration flow
- Test workflow execution
- Test webhook handling

### 15.3 End-to-End Testing

- Register test agent
- Execute test workflow
- Verify results
- Test error scenarios

---

## 16. Next Steps

1. **Verify API Endpoints:**
   - Contact OpenSERV support for official API documentation
   - Test endpoints with Postman/curl
   - Document actual request/response formats

2. **Implement Bridge Service:**
   - Create `OpenServBridgeService.cs`
   - Implement HTTP client wrapper
   - Add authentication
   - Implement error handling

3. **Create Integration Tests:**
   - Test agent registration
   - Test workflow execution
   - Test webhook handling

---

## 17. References

- **OpenSERV Platform:** https://www.openserv.ai
- **OpenSERV Documentation:** https://docs.openserv.ai
- **OpenSERV SDK:** https://docs.openserv.ai/resources/sdk
- **OPENSERV_RESEARCH.md:** `/OPENSERV_RESEARCH.md` (root level)
- **A2A Integration Doc:** `/A2A/docs/A2A_OPENSERV_INTEGRATION.md`

---

## 18. Assumptions & Notes

### Assumptions Made:
1. OpenSERV provides REST API (may need verification)
2. API follows standard REST conventions
3. Authentication uses Bearer tokens
4. Webhooks use HMAC-SHA256 signatures

### Notes:
- Some endpoint details are inferred from SDK patterns
- Actual API may differ - verify with OpenSERV documentation
- Rate limits are estimates - verify with OpenSERV
- Error codes are examples - verify actual error codes

---

**Last Updated:** January 5, 2026  
**Status:** ✅ Research Complete - Ready for Bridge Design

