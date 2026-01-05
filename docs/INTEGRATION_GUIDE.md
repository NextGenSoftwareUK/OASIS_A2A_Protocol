# A2A Protocol Integration Guide

**Date:** January 5, 2026  
**Version:** 1.0.0

---

## Overview

This guide provides comprehensive instructions for integrating the A2A Protocol with SERV infrastructure and OpenSERV agents. The integration enables unified service discovery, agent communication, and workflow execution across multiple platforms.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [A2A-SERV Integration](#a2a-serv-integration)
- [A2A-OpenSERV Integration](#a2a-openserv-integration)
- [Unified Service Layer](#unified-service-layer)
- [API Endpoints](#api-endpoints)
- [Code Examples](#code-examples)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Components

1. **OASIS API** - Running and accessible
   - Default URL: `http://localhost:5003`
   - Must have A2A Protocol endpoints enabled

2. **SERV Infrastructure** - ONET Unified Architecture
   - Service registry must be initialized
   - UnifiedService registration available

3. **OpenSERV Platform** (Optional, for OpenSERV integration)
   - OpenSERV API endpoint
   - API key for authentication

### Development Tools

- .NET 8.0 SDK
- Python 3.9+ (for testing scripts)
- Postman or curl (for API testing)
- JWT token for authentication

---

## Architecture Overview

### Integration Layers

```
┌─────────────────────────────────────────────────────────────┐
│              Unified Agent Service Ecosystem                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  A2A Protocol│◄──►│  OpenSERV   │◄──►│ SERV/ONET    │ │
│  │              │    │              │    │              │ │
│  │ • Messaging  │    │ • AI Agents  │    │ • Registry   │ │
│  │ • Discovery  │    │ • Reasoning  │    │ • Discovery  │ │
│  │ • Payments   │    │ • Workflows  │    │ • Routing    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         ▲                    ▲                    ▲         │
│         │                    │                    │         │
│         └────────────────────┴────────────────────┘         │
│                    Unified Service Layer                    │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **A2A Protocol** - Agent-to-Agent communication (JSON-RPC 2.0)
2. **SERV Infrastructure** - Service registry and discovery (ONET)
3. **OpenSERV** - AI agent platform for workflow execution
4. **Unified Service Layer** - Abstraction for all service types

---

## A2A-SERV Integration

### Overview

A2A-SERV integration enables A2A agents to be registered and discovered via SERV infrastructure (ONET Unified Architecture).

### Registration Flow

1. **Register Agent Capabilities** (via A2A)
   ```http
   POST /api/a2a/agent/capabilities
   Authorization: Bearer {token}
   Content-Type: application/json
   
   {
     "services": ["data-analysis", "report-generation"],
     "skills": ["Python", "Machine Learning"],
     "status": "Available",
     "description": "Data analysis agent"
   }
   ```

2. **Register as SERV Service** (automatic or manual)
   ```http
   POST /api/a2a/agent/register-service
   Authorization: Bearer {token}
   ```

3. **Auto-Registration** - Agents automatically register with SERV when capabilities are registered

### Discovery Flow

1. **Discover All Agents via SERV**
   ```http
   GET /api/a2a/agents/discover-serv
   ```

2. **Discover Agents by Service**
   ```http
   GET /api/a2a/agents/discover-serv?service=data-analysis
   ```

### Code Example: Register and Discover

```python
import requests

BASE_URL = "http://localhost:5003"
API_URL = f"{BASE_URL}/api/a2a"
JWT_TOKEN = "your_jwt_token"

# 1. Register capabilities
capabilities = {
    "services": ["data-analysis"],
    "skills": ["Python"],
    "status": "Available"
}

response = requests.post(
    f"{API_URL}/agent/capabilities",
    headers={"Authorization": f"Bearer {JWT_TOKEN}"},
    json=capabilities
)

# 2. Register as SERV service
response = requests.post(
    f"{API_URL}/agent/register-service",
    headers={"Authorization": f"Bearer {JWT_TOKEN}"}
)

# 3. Discover agents
response = requests.get(f"{API_URL}/agents/discover-serv?service=data-analysis")
agents = response.json()
```

---

## A2A-OpenSERV Integration

### Overview

A2A-OpenSERV integration enables OpenSERV AI agents to be registered as A2A agents and execute workflows through the A2A Protocol.

### Registration Flow

1. **Register OpenSERV Agent**
   ```http
   POST /api/a2a/openserv/register
   Content-Type: application/json
   
   {
     "openServAgentId": "agent-123",
     "openServEndpoint": "https://api.openserv.ai/agents/agent-123",
     "capabilities": ["data-analysis", "nlp"],
     "apiKey": "sk-..."
   }
   ```

2. **Automatic A2A Registration** - Creates avatar and registers capabilities

3. **SERV Registration** - Optionally registers with SERV infrastructure

### Workflow Execution Flow

1. **Execute Workflow**
   ```http
   POST /api/a2a/workflow/execute
   Authorization: Bearer {token}
   Content-Type: application/json
   
   {
     "toAgentId": "agent-uuid",
     "workflowRequest": "Analyze data and generate report",
     "workflowParameters": {
       "data_source": "sales_data.csv"
     }
   }
   ```

2. **A2A Message Routing** - Request sent via A2A Protocol

3. **OpenSERV Execution** - Workflow executed by OpenSERV agent

4. **Response Routing** - Result sent back via A2A Protocol

### Code Example: Register and Execute Workflow

```python
import requests

BASE_URL = "http://localhost:5003"
API_URL = f"{BASE_URL}/api/a2a"
JWT_TOKEN = "your_jwt_token"

# 1. Register OpenSERV agent
openserv_registration = {
    "openServAgentId": "nlp-agent",
    "openServEndpoint": "https://api.openserv.ai/agents/nlp-agent",
    "capabilities": ["nlp", "text-analysis"],
    "apiKey": "sk-..."
}

response = requests.post(
    f"{API_URL}/openserv/register",
    json=openserv_registration
)
agent_id = response.json().get("agentId")

# 2. Execute workflow
workflow_request = {
    "toAgentId": agent_id,
    "workflowRequest": "Analyze this text and extract key topics",
    "workflowParameters": {
        "text": "Sample text to analyze..."
    }
}

response = requests.post(
    f"{API_URL}/workflow/execute",
    headers={"Authorization": f"Bearer {JWT_TOKEN}"},
    json=workflow_request
)

result = response.json()
```

---

## Unified Service Layer

### Overview

The Unified Service Layer provides a common interface for all agent service types (A2A, OpenSERV, SERV) through the `UnifiedAgentServiceManager`.

### Key Features

- **Service Registration** - Register services from any platform
- **Service Discovery** - Discover services across all platforms
- **Service Routing** - Intelligent routing based on capabilities
- **Health Monitoring** - Automatic health checks and removal
- **Load Balancing** - Distribute requests across services

### Usage Example

```csharp
// Register unified service
var service = new UnifiedAgentService
{
    ServiceId = agentId.ToString(),
    ServiceName = "Data Analysis Agent",
    ServiceType = "A2A_Agent",
    Capabilities = new List<string> { "data-analysis" },
    Endpoint = "/api/a2a/agent-card/" + agentId,
    Protocol = "A2A_JSON-RPC_2.0"
};

await UnifiedAgentServiceManager.Instance.RegisterServiceAsync(service);

// Discover services
var services = await UnifiedAgentServiceManager.Instance
    .DiscoverServicesAsync("data-analysis");

// Execute service
var result = await UnifiedAgentServiceManager.Instance
    .ExecuteServiceAsync(serviceId, parameters);
```

---

## API Endpoints

### A2A-SERV Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/a2a/agent/register-service` | Register agent as SERV service |
| GET | `/api/a2a/agents/discover-serv` | Discover agents via SERV |
| GET | `/api/a2a/agents/discover-serv?service={name}` | Discover agents by service |

### A2A-OpenSERV Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/a2a/openserv/register` | Register OpenSERV agent |
| POST | `/api/a2a/workflow/execute` | Execute AI workflow |

### Authentication

Most endpoints require JWT token authentication:

```http
Authorization: Bearer {jwt_token}
```

---

## Code Examples

### Complete Integration Example

See the demo scripts for complete examples:

- **SERV Discovery Demo**: `A2A/demo/a2a_serv_discovery_demo.py`
- **OpenSERV Workflow Demo**: `A2A/demo/a2a_openserv_workflow_demo.py`

### C# Integration Example

```csharp
// Register A2A agent as SERV service
var capabilities = new AgentCapabilities
{
    Services = new List<string> { "data-analysis" },
    Skills = new List<string> { "Python" },
    Status = AgentStatus.Available
};

await AgentManager.Instance
    .RegisterAgentCapabilitiesAsync(agentId, capabilities);

await A2AManager.Instance
    .RegisterAgentAsServiceAsync(agentId, capabilities);

// Discover agents via SERV
var agents = await A2AManager.Instance
    .DiscoverAgentsViaSERVAsync("data-analysis");

// Register OpenSERV agent
await A2AManager.Instance.RegisterOpenServAgentAsync(
    "openserv-agent-1",
    "https://api.openserv.ai/agents/agent-1",
    new List<string> { "nlp", "text-analysis" },
    "sk-..."
);

// Execute workflow
var result = await A2AManager.Instance.ExecuteAIWorkflowAsync(
    fromAgentId,
    toAgentId,
    "Analyze text and extract key topics",
    new Dictionary<string, object> { { "text", "..." } }
);
```

---

## Testing

### Running Integration Tests

1. **SERV Integration Tests**
   ```bash
   cd A2A/test
   export JWT_TOKEN="your_token"
   export AGENT_ID="agent_uuid"
   python test_a2a_serv_integration.py
   ```

2. **OpenSERV Integration Tests**
   ```bash
   cd A2A/test
   export JWT_TOKEN="your_token"
   export OPENSERV_ENDPOINT="https://api.openserv.ai/agents/test"
   python test_a2a_openserv_integration.py
   ```

3. **Run Demo Scripts**
   ```bash
   cd A2A/demo
   python a2a_serv_discovery_demo.py
   python a2a_openserv_workflow_demo.py
   ```

### Test Coverage

- ✅ Service registration
- ✅ Service discovery
- ✅ OpenSERV agent registration
- ✅ Workflow execution
- ✅ Error handling
- ✅ Authentication/authorization

---

## Troubleshooting

### Common Issues

1. **Agent not discoverable via SERV**
   - Verify agent capabilities are registered
   - Check SERV infrastructure is running
   - Ensure agent is registered as SERV service

2. **OpenSERV workflow execution fails**
   - Verify OpenSERV endpoint is accessible
   - Check API key is valid
   - Ensure agent is registered as OpenSERV agent

3. **Authentication errors**
   - Verify JWT token is valid and not expired
   - Check avatar is of type Agent
   - Ensure token has required permissions

4. **Service registration fails**
   - Check SERV infrastructure availability
   - Verify service ID is unique
   - Review error logs for details

For more detailed troubleshooting, see [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md).

---

## Next Steps

1. **Explore Demo Scripts** - Run the demo scripts to see integration in action
2. **Review API Documentation** - See [OASIS_A2A_OPENAPI_DOCUMENTATION.md](OASIS_A2A_OPENAPI_DOCUMENTATION.md)
3. **Read Integration Plan** - See [A2A_OPENSERV_INTEGRATION.md](A2A_OPENSERV_INTEGRATION.md)
4. **Test Your Integration** - Use the test scripts to verify your setup

---

## References

- **A2A Protocol**: https://github.com/a2aproject/A2A
- **OpenSERV Platform**: https://www.openserv.ai
- **OpenSERV Documentation**: https://docs.openserv.ai
- **OASIS Documentation**: `Docs/ONET_DOCUMENTATION.md`

---

**Last Updated:** January 5, 2026  
**Version:** 1.0.0

