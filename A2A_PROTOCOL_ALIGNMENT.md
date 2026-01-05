# A2A Protocol Alignment Documentation
**Date:** January 3, 2026  
**Status:** 📋 **ALIGNMENT ANALYSIS** - Comparing OASIS Implementation with Official A2A Protocol

---

## Official A2A Protocol Overview

Based on the [official A2A Protocol repository](https://github.com/a2aproject/A2A), the Agent2Agent (A2A) Protocol is:

> **An open protocol enabling communication and interoperability between opaque agentic applications.**

### Key Characteristics

- **Standardized Communication:** JSON-RPC 2.0 over HTTP(S)
- **Agent Discovery:** Via "Agent Cards" detailing capabilities and connection info
- **Flexible Interaction:** Supports synchronous request/response, streaming (SSE), and asynchronous push notifications
- **Rich Data Exchange:** Handles text, files, and structured JSON data
- **Enterprise-Ready:** Designed with security, authentication, and observability in mind

### Official A2A Protocol Goals

1. **Break Down Silos:** Connect agents across different ecosystems
2. **Enable Complex Collaboration:** Allow specialized agents to work together
3. **Promote Open Standards:** Community-driven approach to agent communication
4. **Preserve Opacity:** Allow agents to collaborate without sharing internal state/memory/tools

---

## OASIS A2A Implementation vs. Official Protocol

### ✅ What We've Implemented (Aligned)

#### 1. Agent Identity & Type
**Official A2A:** Agents are identified via Agent Cards with unique identifiers  
**OASIS Implementation:** ✅ Agents have unique avatar IDs (`AvatarType.Agent`)

**Status:** ✅ **ALIGNED** - Our agent avatars serve as unique identifiers

#### 2. Agent Capabilities
**Official A2A:** Agent Cards detail capabilities and connection info  
**OASIS Implementation:** ✅ `IAgentCapabilities` interface with:
- Services (what agents can do)
- Skills (agent capabilities)
- Status (availability)
- Pricing (service costs)
- Reputation score

**Status:** ✅ **ALIGNED** - Our capabilities system matches Agent Card concept

#### 3. Agent Discovery
**Official A2A:** Agents can discover each other's capabilities  
**OASIS Implementation:** ✅ `AgentManager.FindAgentsByServiceAsync()` and `FindAgentsBySkillAsync()`

**Status:** ✅ **ALIGNED** - Service discovery implemented

#### 4. Agent Communication
**Official A2A:** JSON-RPC 2.0 over HTTP(S) for agent-to-agent communication  
**OASIS Implementation:** ✅ `A2AManager` with message protocol:
- `IA2AMessage` interface
- Message types (ServiceRequest, PaymentRequest, TaskDelegation, etc.)
- Message routing and delivery

**Status:** ⚠️ **PARTIALLY ALIGNED** - We have message protocol but not JSON-RPC 2.0 format yet

#### 5. Payment Integration
**Official A2A:** Supports payment requests and confirmations  
**OASIS Implementation:** ✅ `A2AManager.SendPaymentRequestAsync()` integrated with Solana payments

**Status:** ✅ **ALIGNED** - Payment requests implemented

---

### ❌ What's Missing (Not Yet Implemented)

#### 1. JSON-RPC 2.0 Format
**Official A2A:** Uses JSON-RPC 2.0 specification for all messages  
**OASIS Implementation:** ❌ Currently uses custom message format

**Required:** Implement JSON-RPC 2.0 message format:
```json
{
  "jsonrpc": "2.0",
  "method": "service_request",
  "params": {
    "service": "data-analysis",
    "parameters": {...}
  },
  "id": "unique-request-id"
}
```

#### 2. Agent Cards
**Official A2A:** Formal Agent Card specification with:
- Agent identifier
- Capabilities
- Connection info (endpoint URL)
- Authorization schemes
- Optional credentials

**OASIS Implementation:** ❌ No formal Agent Card structure

**Required:** Create `IAgentCard` interface matching official spec

#### 3. HTTP(S) Transport
**Official A2A:** JSON-RPC 2.0 over HTTP(S)  
**OASIS Implementation:** ❌ Currently uses internal messaging (not HTTP endpoints)

**Required:** Add HTTP endpoints for A2A protocol:
- `POST /a2a/jsonrpc` - JSON-RPC 2.0 endpoint
- `GET /a2a/agent-card/{agentId}` - Agent Card endpoint

#### 4. Streaming Support (SSE)
**Official A2A:** Supports Server-Sent Events (SSE) for streaming  
**OASIS Implementation:** ❌ No streaming support

**Required:** Add SSE support for long-running tasks

#### 5. Push Notifications
**Official A2A:** Asynchronous push notifications  
**OASIS Implementation:** ❌ No push notification mechanism

**Required:** Implement WebSocket or HTTP push for async notifications

#### 6. File Exchange
**Official A2A:** Handles file transfers  
**OASIS Implementation:** ❌ No file exchange in A2A messages

**Required:** Add file attachment support to A2A messages

---

## Alignment Roadmap

### Phase 1: Core Protocol Alignment ✅ (Current)
- [x] Agent type and identity
- [x] Agent capabilities
- [x] Service discovery
- [x] Basic message protocol
- [x] Payment integration

### Phase 2: Protocol Standardization 🔄 (Next)
- [ ] Implement JSON-RPC 2.0 format
- [ ] Create Agent Card structure
- [ ] Add HTTP(S) endpoints
- [ ] Standardize message format

### Phase 3: Advanced Features 📋 (Future)
- [ ] SSE streaming support
- [ ] Push notifications
- [ ] File exchange
- [ ] Enhanced security/auth

---

## Official A2A Protocol Specification

### Agent Card Structure (Based on Official Spec)

```json
{
  "agent_id": "unique-agent-identifier",
  "name": "Agent Name",
  "version": "1.0.0",
  "capabilities": {
    "services": ["service1", "service2"],
    "skills": ["skill1", "skill2"]
  },
  "connection": {
    "endpoint": "https://agent.example.com/a2a/jsonrpc",
    "protocol": "jsonrpc2.0",
    "auth": {
      "scheme": "bearer",
      "credentials": "optional"
    }
  },
  "metadata": {
    "description": "Agent description",
    "pricing": {...},
    "status": "available"
  }
}
```

### JSON-RPC 2.0 Message Format

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "service_request",
  "params": {
    "service": "data-analysis",
    "parameters": {
      "dataset": "sales_data.csv",
      "analysis_type": "trend"
    }
  },
  "id": "request-123"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "task_id": "task-456",
    "status": "accepted"
  },
  "id": "request-123"
}
```

---

## OASIS Implementation Details

### Current Message Format

```csharp
public class A2AMessage : IA2AMessage
{
    public Guid MessageId { get; set; }
    public Guid FromAgentId { get; set; }
    public Guid ToAgentId { get; set; }
    public A2AMessageType MessageType { get; set; }
    public string Content { get; set; }
    public Dictionary<string, object> Payload { get; set; }
    public DateTime Timestamp { get; set; }
    // ... other properties
}
```

### Conversion to JSON-RPC 2.0 Format Needed

```csharp
public class A2AJsonRpcMessage
{
    [JsonProperty("jsonrpc")]
    public string JsonRpc { get; set; } = "2.0";
    
    [JsonProperty("method")]
    public string Method { get; set; }  // e.g., "service_request", "payment_request"
    
    [JsonProperty("params")]
    public Dictionary<string, object> Params { get; set; }
    
    [JsonProperty("id")]
    public string Id { get; set; }
    
    [JsonProperty("result")]
    public object Result { get; set; }  // For responses
    
    [JsonProperty("error")]
    public A2AJsonRpcError Error { get; set; }  // For errors
}
```

---

## Recommendations

### Immediate Actions

1. **Create Agent Card Interface**
   - Match official A2A Agent Card structure
   - Include connection info and capabilities

2. **Implement JSON-RPC 2.0 Format**
   - Convert current `A2AMessage` to JSON-RPC 2.0 format
   - Add JSON-RPC 2.0 serialization/deserialization

3. **Add HTTP Endpoints**
   - `POST /api/a2a/jsonrpc` - Main JSON-RPC 2.0 endpoint
   - `GET /api/a2a/agent-card/{agentId}` - Agent Card endpoint
   - `GET /api/a2a/agents` - List available agents

4. **Update Message Types**
   - Map our message types to JSON-RPC 2.0 methods
   - Ensure compatibility with official protocol

### Future Enhancements

1. **Streaming Support**
   - Implement SSE for long-running tasks
   - Add streaming task updates

2. **Push Notifications**
   - WebSocket support for real-time updates
   - HTTP push for async notifications

3. **File Exchange**
   - Add file attachment support
   - Integrate with OASIS file storage

4. **Security Enhancements**
   - OAuth/Bearer token support
   - End-to-end encryption
   - Agent authentication

---

## Official A2A Resources

- **GitHub Repository:** https://github.com/a2aproject/A2A
- **Documentation:** https://a2a-protocol.org/
- **Specification:** https://github.com/a2aproject/A2A/tree/main/specification
- **SDKs Available:**
  - Python: `pip install a2a-sdk`
  - Go: `go get github.com/a2aproject/a2a-go`
  - JavaScript: `npm install @a2a-js/sdk`
  - Java: Maven package
  - .NET: `dotnet add package A2A`

---

## Conclusion

### Current Status

✅ **Foundation Implemented:**
- Agent type and identity
- Agent capabilities
- Service discovery
- Basic message protocol
- Payment integration

⚠️ **Needs Alignment:**
- JSON-RPC 2.0 format
- Agent Cards
- HTTP(S) endpoints
- Standardized message format

### Next Steps

1. **Short-term:** Implement JSON-RPC 2.0 format and Agent Cards
2. **Medium-term:** Add HTTP endpoints and streaming support
3. **Long-term:** Full protocol compliance with official A2A spec

**Goal:** Achieve full compatibility with the official A2A Protocol while maintaining OASIS-specific features (Solana payments, Karma integration, etc.)

---

**Last Updated:** January 3, 2026  
**Protocol Version:** A2A v0.3.0 (Official)  
**OASIS Implementation:** v1.0.0 (Foundation)



