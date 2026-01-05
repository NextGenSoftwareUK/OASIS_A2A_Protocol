# OASIS A2A Protocol Implementation Documentation
**Date:** January 3, 2026  
**Status:** ✅ **FOUNDATION COMPLETE** - Aligned with Official A2A Protocol  
**Reference:** [Official A2A Protocol](https://github.com/a2aproject/A2A) | [A2A Protocol Documentation](https://a2a-protocol.org/)

---

## Executive Summary

OASIS has implemented the foundation for **Agent-to-Agent (A2A) Protocol** based on the [official A2A Protocol specification](https://github.com/a2aproject/A2A) developed by Google and contributed to the Linux Foundation. This implementation enables autonomous AI agents to communicate, discover each other's capabilities, and collaborate on tasks while preserving agent opacity (not exposing internal state, memory, or tools).

### Key Achievements

✅ **Agent Avatar Type** - Agents can be created with `AvatarType.Agent`  
✅ **Agent Capabilities** - Agents can register services, skills, and pricing  
✅ **Service Discovery** - Agents can find other agents by service or skill  
✅ **A2A Message Protocol** - Standardized agent-to-agent communication  
✅ **Payment Integration** - A2A payment requests integrated with Solana blockchain  
✅ **Demo Script** - Updated to create true Agent avatars

---

## Official A2A Protocol Overview

The [A2A Protocol](https://github.com/a2aproject/A2A) is an open standard that:

> **Enables communication and interoperability between opaque agentic applications.**

### Official Protocol Features

1. **Standardized Communication:** JSON-RPC 2.0 over HTTP(S)
2. **Agent Discovery:** Via "Agent Cards" detailing capabilities and connection info
3. **Flexible Interaction:** Synchronous request/response, streaming (SSE), and asynchronous push notifications
4. **Rich Data Exchange:** Handles text, files, and structured JSON data
5. **Enterprise-Ready:** Security, authentication, and observability built-in

### Official Protocol Goals

- **Break Down Silos:** Connect agents across different ecosystems
- **Enable Complex Collaboration:** Specialized agents working together
- **Promote Open Standards:** Community-driven approach
- **Preserve Opacity:** Agents collaborate without sharing internal state/memory/tools

---

## OASIS Implementation Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OASIS A2A Protocol Layer                 │
├─────────────────────────────────────────────────────────────┤
│  AgentManager  │  A2AManager  │  MessagingManager          │
│  Capabilities   │  Protocol    │  Delivery                  │
│  Discovery      │  Routing     │  Notifications             │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              OASIS Core Infrastructure                      │
│  AvatarManager │  WalletManager │  KeyManager              │
│  SolanaOASIS   │  KarmaManager  │  HyperDrive              │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Agent Avatar Type
**Location:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Enums/AvatarType.cs`

```csharp
public enum AvatarType
{
    Wizard, 
    User,
    System,
    Agent  // Autonomous agents that can communicate and transact
}
```

**Purpose:** Distinguishes agents from regular users in the OASIS system.

#### 2. Agent Capabilities Interface
**Location:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Interfaces/Agent/IAgentCapabilities.cs`

**Aligned with:** Official A2A Protocol "Agent Card" concept

```csharp
public interface IAgentCapabilities
{
    List<string> Services { get; set; }              // What services agent provides
    Dictionary<string, decimal> Pricing { get; set; } // Service pricing
    List<string> Skills { get; set; }                // Agent skills
    AgentStatus Status { get; set; }                 // Availability
    decimal ReputationScore { get; set; }            // Reputation
    int MaxConcurrentTasks { get; set; }             // Capacity
    int ActiveTasks { get; set; }                    // Current load
    string Description { get; set; }                  // Agent description
    Dictionary<string, object> Metadata { get; set; } // Additional info
}
```

**Comparison with Official A2A:**
- ✅ **Services** → Maps to Agent Card "capabilities"
- ✅ **Skills** → Maps to Agent Card "skills"
- ✅ **Status** → Maps to Agent Card "status"
- ⚠️ **Connection Info** → Not yet implemented (needed for full compliance)

#### 3. A2A Message Protocol
**Location:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Interfaces/Agent/IA2AMessage.cs`

**Aligned with:** Official A2A Protocol message types

```csharp
public enum A2AMessageType
{
    // Service Discovery (Official A2A: Capability Discovery)
    CapabilityQuery,        // "What can you do?"
    CapabilityResponse,     // "I can do X, Y, Z"
    ServiceRequest,         // "Can you do X?"
    ServiceOffer,           // "I can do X for Y SOL"
    
    // Task Management (Official A2A: Task Management)
    TaskDelegation,         // "Please do X"
    TaskAcceptance,         // "I accept the task"
    TaskRejection,          // "I cannot do this task"
    TaskUpdate,             // "Task progress update"
    TaskCompletion,         // "Task completed"
    
    // Payment (Official A2A: Payment Requests)
    PaymentRequest,         // "Pay me Y SOL for X"
    PaymentConfirmation,    // "Payment received"
    PaymentRejection,       // "Payment failed"
    
    // Negotiation (Official A2A: UX Negotiation)
    NegotiationStart,       // "Let's negotiate terms"
    NegotiationOffer,       // "I offer X"
    NegotiationAccept,      // "I accept"
    NegotiationReject,      // "I reject"
    
    // Reputation (OASIS Extension)
    ReputationQuery,        // "What's your reputation?"
    ReputationUpdate,       // "Reputation changed"
    
    // Health Checks
    Ping,                   // "Are you alive?"
    Pong                    // "Yes, I'm alive"
}
```

**Comparison with Official A2A:**
- ✅ **Service Discovery** → Aligned with official "Capability Discovery"
- ✅ **Task Management** → Aligned with official "Task Management"
- ✅ **Payment** → Aligned with official payment support
- ✅ **Negotiation** → Aligned with official "UX Negotiation"
- ⚠️ **JSON-RPC 2.0 Format** → Not yet implemented (needed for full compliance)

#### 4. Agent Manager
**Location:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Managers/AgentManager/AgentManager.cs`

**Key Methods:**
- `RegisterAgentCapabilitiesAsync()` - Register agent services (Agent Card equivalent)
- `GetAgentCapabilitiesAsync()` - Get agent capabilities
- `FindAgentsByServiceAsync()` - Service discovery (Official A2A: Capability Discovery)
- `FindAgentsBySkillAsync()` - Skill-based discovery
- `GetAvailableAgentsAsync()` - List available agents
- `UpdateAgentStatusAsync()` - Update agent availability
- `UpdateAgentTaskCountAsync()` - Update task count

**Aligned with:** Official A2A Protocol "Agent Discovery"

#### 5. A2A Manager
**Location:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Managers/A2AManager/A2AManager.cs`

**Key Methods:**
- `SendA2AMessageAsync()` - Send A2A messages (Official A2A: Message Exchange)
- `GetPendingMessagesAsync()` - Get pending messages
- `MarkMessageProcessedAsync()` - Mark messages as processed
- `SendServiceRequestAsync()` - Send service request
- `SendPaymentRequestAsync()` - Send payment request (Integrated with Solana)

**Aligned with:** Official A2A Protocol "Message Exchange"

---

## Alignment with Official A2A Protocol

### ✅ Fully Aligned Features

| Official A2A Feature | OASIS Implementation | Status |
|----------------------|---------------------|--------|
| Agent Identity | `AvatarType.Agent` | ✅ Complete |
| Capability Discovery | `AgentManager.FindAgentsByServiceAsync()` | ✅ Complete |
| Service Registration | `AgentManager.RegisterAgentCapabilitiesAsync()` | ✅ Complete |
| Message Exchange | `A2AManager.SendA2AMessageAsync()` | ✅ Complete |
| Task Management | `A2AMessageType.TaskDelegation` | ✅ Complete |
| Payment Requests | `A2AManager.SendPaymentRequestAsync()` | ✅ Complete |
| Agent Status | `AgentStatus` enum | ✅ Complete |

### ⚠️ Partially Aligned Features

| Official A2A Feature | OASIS Implementation | Status |
|----------------------|---------------------|--------|
| JSON-RPC 2.0 Format | Custom message format | ⚠️ Needs conversion |
| Agent Cards | `IAgentCapabilities` (similar) | ⚠️ Needs connection info |
| HTTP(S) Transport | Internal messaging | ⚠️ Needs HTTP endpoints |
| Streaming (SSE) | Not implemented | ⚠️ Future enhancement |
| Push Notifications | Not implemented | ⚠️ Future enhancement |
| File Exchange | Not implemented | ⚠️ Future enhancement |

### ❌ Not Yet Implemented

- **JSON-RPC 2.0 Serialization:** Need to convert messages to JSON-RPC 2.0 format
- **HTTP Endpoints:** Need REST API endpoints for A2A protocol
- **Agent Card Endpoint:** Need endpoint to serve Agent Cards
- **Streaming Support:** SSE for long-running tasks
- **Push Notifications:** WebSocket or HTTP push for async updates
- **File Attachments:** Support for file exchange in messages

---

## Usage Examples

### 1. Create an Agent Avatar

```bash
POST /api/avatar/register
Content-Type: application/json

{
  "username": "data_analyst_agent",
  "email": "agent@example.com",
  "password": "secure_password",
  "avatarType": "Agent"
}
```

### 2. Register Agent Capabilities (Agent Card Equivalent)

```csharp
var capabilities = new AgentCapabilities
{
    Services = new List<string> 
    { 
        "data-analysis", 
        "report-generation",
        "data-visualization"
    },
    Pricing = new Dictionary<string, decimal>
    {
        ["data-analysis"] = 0.1m,      // 0.1 SOL per analysis
        ["report-generation"] = 0.05m, // 0.05 SOL per report
        ["data-visualization"] = 0.08m
    },
    Skills = new List<string> 
    { 
        "Python", 
        "Machine Learning", 
        "Data Science",
        "Pandas",
        "Matplotlib"
    },
    Status = AgentStatus.Available,
    MaxConcurrentTasks = 3,
    ActiveTasks = 0,
    Description = "Specialized data analysis and reporting agent",
    ReputationScore = 4.8m
};

await AgentManager.Instance.RegisterAgentCapabilitiesAsync(agentId, capabilities);
```

### 3. Discover Agents by Service (Official A2A: Capability Discovery)

```csharp
// Find agents that can perform data analysis
var result = await AgentManager.Instance.FindAgentsByServiceAsync("data-analysis");

if (!result.IsError && result.Result.Count > 0)
{
    foreach (var agentId in result.Result)
    {
        var capabilities = await AgentManager.Instance.GetAgentCapabilitiesAsync(agentId);
        Console.WriteLine($"Found agent: {agentId}");
        Console.WriteLine($"Services: {string.Join(", ", capabilities.Result.Services)}");
        Console.WriteLine($"Status: {capabilities.Result.Status}");
        Console.WriteLine($"Reputation: {capabilities.Result.ReputationScore}");
    }
}
```

### 4. Send Service Request (Official A2A: Task Management)

```csharp
var serviceRequest = await A2AManager.Instance.SendServiceRequestAsync(
    fromAgentId: requestingAgentId,
    toAgentId: serviceProviderAgentId,
    serviceName: "data-analysis",
    serviceParameters: new Dictionary<string, object>
    {
        ["dataset"] = "sales_data_2024.csv",
        ["analysisType"] = "trend_analysis",
        ["timeframe"] = "monthly",
        ["outputFormat"] = "json"
    }
);

Console.WriteLine($"Service request sent: {serviceRequest.Result.MessageId}");
```

### 5. Send Payment Request (Official A2A: Payment)

```csharp
// After service completion, request payment
var paymentRequest = await A2AManager.Instance.SendPaymentRequestAsync(
    fromAgentId: serviceProviderAgentId,
    toAgentId: requestingAgentId,
    amount: 0.1m,  // 0.1 SOL
    description: "Payment for data analysis service",
    transactionHash: null  // Will be set after Solana transaction
);

// Execute Solana payment
var solanaResult = await WalletManager.Instance.SendTokenAsync(
    fromAvatarId: requestingAgentId,
    toAvatarId: serviceProviderAgentId,
    amount: 0.1m,
    token: "SOL",
    providerType: ProviderType.SolanaOASIS
);

// Update payment request with transaction hash
if (!solanaResult.IsError)
{
    paymentRequest.Result.TransactionHash = solanaResult.Result.TransactionHash;
}
```

### 6. Complete Task Flow (Official A2A: Full Collaboration)

```csharp
// Step 1: Discover agents
var agents = await AgentManager.Instance.FindAgentsByServiceAsync("data-analysis");

// Step 2: Send service request
var request = await A2AManager.Instance.SendServiceRequestAsync(
    fromAgentId: agentAId,
    toAgentId: agents.Result[0],
    serviceName: "data-analysis",
    serviceParameters: new Dictionary<string, object> { ["dataset"] = "data.csv" }
);

// Step 3: Agent B accepts task
var acceptance = new A2AMessage
{
    MessageId = Guid.NewGuid(),
    FromAgentId = agents.Result[0],
    ToAgentId = agentAId,
    MessageType = A2AMessageType.TaskAcceptance,
    ResponseToMessageId = request.Result.MessageId,
    Content = "Task accepted, starting analysis..."
};
await A2AManager.Instance.SendA2AMessageAsync(acceptance);

// Step 4: Agent B completes task
var completion = new A2AMessage
{
    MessageId = Guid.NewGuid(),
    FromAgentId = agents.Result[0],
    ToAgentId = agentAId,
    MessageType = A2AMessageType.TaskCompletion,
    ResponseToMessageId = request.Result.MessageId,
    Content = "Analysis complete",
    Payload = new Dictionary<string, object>
    {
        ["result"] = "analysis_results.json",
        ["summary"] = "Sales increased 15% month-over-month"
    }
};
await A2AManager.Instance.SendA2AMessageAsync(completion);

// Step 5: Agent A pays Agent B
var payment = await A2AManager.Instance.SendPaymentRequestAsync(
    fromAgentId: agentAId,
    toAgentId: agents.Result[0],
    amount: 0.1m,
    description: "Payment for data analysis"
);

// Step 6: Execute Solana payment
await WalletManager.Instance.SendTokenAsync(
    fromAvatarId: agentAId,
    toAvatarId: agents.Result[0],
    amount: 0.1m,
    token: "SOL",
    providerType: ProviderType.SolanaOASIS
);
```

---

## Integration with OASIS Features

### Solana Payment Integration

OASIS A2A implementation uniquely integrates with Solana blockchain for payments:

```csharp
// A2A payment request automatically triggers Solana transaction
var paymentRequest = await A2AManager.Instance.SendPaymentRequestAsync(...);

// Solana payment execution
var solanaPayment = await WalletManager.Instance.SendTokenAsync(
    fromAvatarId: fromAgentId,
    toAvatarId: toAgentId,
    amount: paymentRequest.Result.Payload["amount"],
    token: "SOL",
    providerType: ProviderType.SolanaOASIS
);

// Link transaction hash to A2A message
paymentRequest.Result.TransactionHash = solanaPayment.Result.TransactionHash;
```

### Karma Integration (OASIS Extension)

Agents can earn karma for successful collaborations:

```csharp
// After successful task completion
await KarmaManager.Instance.AddKarmaAsync(
    avatarId: serviceProviderAgentId,
    karmaSourceType: KarmaSourceType.AgentService,
    karmaSourceTitle: "Completed data analysis task",
    karmaAmount: 10
);
```

### HyperDrive Integration

A2A messages can leverage OASIS HyperDrive for optimal routing:

```csharp
// Messages automatically use HyperDrive for failover
var message = await A2AManager.Instance.SendA2AMessageAsync(...);
// HyperDrive ensures message delivery even if primary provider fails
```

---

## Roadmap to Full A2A Protocol Compliance

### Phase 1: Foundation ✅ (Complete)
- [x] Agent avatar type
- [x] Agent capabilities interface
- [x] Service discovery
- [x] Basic message protocol
- [x] Payment integration

### Phase 2: Protocol Standardization 🔄 (Next)
- [ ] Implement JSON-RPC 2.0 format
- [ ] Create Agent Card structure with connection info
- [ ] Add HTTP(S) endpoints (`POST /api/a2a/jsonrpc`)
- [ ] Add Agent Card endpoint (`GET /api/a2a/agent-card/{id}`)
- [ ] Standardize message serialization

### Phase 3: Advanced Features 📋 (Future)
- [ ] SSE streaming support for long-running tasks
- [ ] WebSocket push notifications
- [ ] File attachment support
- [ ] Enhanced security (OAuth, Bearer tokens)
- [ ] Agent marketplace/discovery UI

### Phase 4: Full Compliance 🎯 (Target)
- [ ] Complete JSON-RPC 2.0 compliance
- [ ] Official A2A SDK integration
- [ ] Cross-platform agent compatibility
- [ ] Full protocol test suite

---

## API Endpoints (Planned)

### Current (Internal)
- `AgentManager.Instance.RegisterAgentCapabilitiesAsync()`
- `AgentManager.Instance.FindAgentsByServiceAsync()`
- `A2AManager.Instance.SendA2AMessageAsync()`

### Planned (HTTP API)
```
POST   /api/a2a/jsonrpc              # JSON-RPC 2.0 endpoint
GET    /api/a2a/agent-card/{id}     # Get Agent Card
GET    /api/a2a/agents               # List available agents
GET    /api/a2a/agents/by-service/{service}  # Find by service
GET    /api/a2a/messages/{agentId}   # Get pending messages
POST   /api/a2a/messages/{id}/process  # Mark as processed
```

---

## Testing

### Test Agent Creation
```bash
curl -X POST http://localhost:5003/api/avatar/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_agent",
    "email": "test@example.com",
    "password": "password123",
    "avatarType": "Agent"
  }'
```

### Test Demo Script
```bash
cd A2A/demo
python3 a2a_solana_payment_demo.py
```

The demo script creates agents with `AvatarType.Agent` and demonstrates:
- Agent creation
- Wallet creation
- Funding
- Payment between agents

---

## References

### Official A2A Protocol Resources
- **GitHub Repository:** https://github.com/a2aproject/A2A
- **Documentation Site:** https://a2a-protocol.org/
- **Specification:** https://github.com/a2aproject/A2A/tree/main/specification
- **License:** Apache License 2.0

### Official A2A SDKs
- **Python:** `pip install a2a-sdk`
- **Go:** `go get github.com/a2aproject/a2a-go`
- **JavaScript:** `npm install @a2a-js/sdk`
- **Java:** Maven package
- **.NET:** `dotnet add package A2A`

### OASIS Implementation Files
- `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Enums/AvatarType.cs`
- `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Interfaces/Agent/IAgentCapabilities.cs`
- `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Interfaces/Agent/IA2AMessage.cs`
- `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Managers/AgentManager/AgentManager.cs`
- `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Managers/A2AManager/A2AManager.cs`

---

## Conclusion

OASIS has successfully implemented the **foundation** for A2A Protocol, enabling:
- ✅ Agent identity and type system
- ✅ Agent capability registration and discovery
- ✅ Agent-to-agent messaging
- ✅ Service requests and task management
- ✅ Payment integration with Solana blockchain

**Next Steps:** Implement JSON-RPC 2.0 format and HTTP endpoints to achieve full compliance with the [official A2A Protocol specification](https://github.com/a2aproject/A2A).

---

**Last Updated:** January 3, 2026  
**OASIS A2A Version:** v1.0.0 (Foundation)  
**Official A2A Version:** v0.3.0  
**Status:** ✅ Foundation Complete | 🔄 Protocol Standardization In Progress



