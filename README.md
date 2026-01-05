# OASIS A2A Protocol Implementation

**Official Agent-to-Agent Protocol Implementation for OASIS Platform**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![A2A Protocol](https://img.shields.io/badge/A2A-Protocol-v0.3.0-green.svg)](https://github.com/a2aproject/A2A)
[![OASIS Version](https://img.shields.io/badge/OASIS-v4.0.0-orange.svg)](https://github.com/NextGenSoftwareUK/Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK)

---

## Overview

This repository contains the complete implementation of the **Agent-to-Agent (A2A) Protocol** for the OASIS Platform. The A2A Protocol enables autonomous agents to communicate, discover capabilities, collaborate, and transact using JSON-RPC 2.0 over HTTP(S).

### Key Features

- ✅ **JSON-RPC 2.0 Protocol** - Standardized agent communication
- ✅ **Agent Cards** - Service discovery and capability advertisement
- ✅ **Service Discovery** - Find agents by service or skill
- ✅ **Task Management** - Delegate and manage tasks between agents
- ✅ **Payment Integration** - Request and process payments via Solana
- ✅ **Health Checks** - Ping/pong for agent availability
- ✅ **Message Queuing** - Reliable message delivery system
- ✅ **SERV Integration** - Unified service registry and discovery via ONET
- ✅ **OpenSERV Integration** - AI agent workflow execution via OpenSERV platform

---

## Repository Structure

This repository contains:
- **`src/`** - All A2A Protocol integration source code (copied from OASIS repo for easy access)
- **`docs/`** - Comprehensive documentation and integration guides
- **`test/`** - Integration test scripts
- **`demo/`** - Demo scripts and examples

## Table of Contents

- [Quick Start](#quick-start)
- [Source Code](#source-code)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Examples](#examples)
- [Testing](#testing)
- [Integration](#integration)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

### Prerequisites

- .NET 8.0 SDK
- OASIS API running on `http://localhost:5003`
- Python 3.9+ (for demo scripts)
- Solana devnet access (for payment demos)

### Installation

1. **Clone the OASIS Repository**
   ```bash
   git clone https://github.com/NextGenSoftwareUK/Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK.git
   cd Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK
   ```

2. **Build the Project**
   ```bash
   cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI
   dotnet build
   ```

3. **Run the API**
   ```bash
   dotnet run --urls http://localhost:5003
   ```

4. **Test A2A Endpoints**
   ```bash
   cd A2A/test
   export JWT_TOKEN="your_jwt_token"
   ./test_a2a_endpoints.sh
   ```

---

## Source Code

All A2A Protocol integration code is available in the `src/` directory for easy access:

```
src/
├── Managers/
│   ├── A2AManager/          # Core A2A Protocol + Integrations
│   │   ├── A2AManager.cs
│   │   ├── A2AManager-JsonRpc.cs
│   │   ├── A2AManager-SERV.cs ✅
│   │   ├── A2AManager-OpenSERV.cs ✅
│   │   ├── A2AManager-NFT.cs ✅
│   │   ├── A2AManager-Karma.cs ✅
│   │   └── A2AManager-Mission.cs ✅
│   └── AgentManager/
│       ├── AgentManager.cs
│       └── AgentManager-AgentCard.cs
├── Controllers/
│   └── A2AController.cs ✅ (All API endpoints)
└── Interfaces/
    ├── IA2AMessage.cs
    ├── IAgentCapabilities.cs
    └── IAgentCard.cs
```

See [`src/README.md`](src/README.md) for detailed file descriptions.

**Note:** These are copies of the actual implementation files in the OASIS repository, provided here for easy reference. The actual code is part of the main OASIS codebase.

---

## Architecture

### Core Components

#### 1. **A2AManager**
Manages A2A protocol messaging and JSON-RPC 2.0 conversion.

**Location:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Managers/A2AManager/`

**Key Features:**
- JSON-RPC 2.0 request/response conversion
- Message queuing and delivery
- Protocol compliance validation

#### 2. **AgentManager**
Manages agent capabilities and Agent Cards.

**Location:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Managers/AgentManager/`

**Key Features:**
- Capability registration
- Service discovery
- Agent Card generation

#### 3. **A2AController**
HTTP API endpoints for A2A Protocol.

**Location:** `ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI/Controllers/A2AController.cs`

**Endpoints:**
- `POST /api/a2a/jsonrpc` - JSON-RPC 2.0 endpoint
- `GET /api/a2a/agents` - List all agents
- `GET /api/a2a/agents/by-service/{service}` - Find by service
- `GET /api/a2a/agent-card/{id}` - Get Agent Card
- `POST /api/a2a/agent/capabilities` - Register capabilities
- `GET /api/a2a/messages` - Get pending messages

---

## API Documentation

### Swagger UI

Interactive API documentation available at:
- **Development:** `http://localhost:5003/swagger`
- **Production:** `https://api.oasisplatform.world/swagger`

Navigate to the **A2A** section for all endpoints.

### OpenAPI Documentation

Complete API reference: [`docs/OASIS_A2A_OPENAPI_DOCUMENTATION.md`](docs/OASIS_A2A_OPENAPI_DOCUMENTATION.md)

### Quick Reference

#### Register Agent Capabilities

```bash
curl -X POST http://localhost:5003/api/a2a/agent/capabilities \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "services": ["data-analysis", "ai-processing"],
    "pricing": {"data-analysis": 0.1},
    "skills": ["Python", "Machine Learning"],
    "status": 0,
    "max_concurrent_tasks": 3,
    "description": "AI service provider"
  }'
```

#### Discover Agents

```bash
curl -X GET http://localhost:5003/api/a2a/agents/by-service/data-analysis
```

#### Send Payment Request (JSON-RPC 2.0)

```bash
curl -X POST http://localhost:5003/api/a2a/jsonrpc \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "payment_request",
    "params": {
      "to_agent_id": "agent-guid-here",
      "amount": 0.01,
      "description": "Payment for service",
      "currency": "SOL"
    },
    "id": "request-123"
  }'
```

---

## Examples

### Python Demo Scripts

#### 1. **Basic A2A Endpoint Tests**
```bash
cd A2A/test
export JWT_TOKEN="your_token"
python3 test_a2a_endpoints.py
```

#### 2. **Integrated Payment Demo**
```bash
cd A2A/demo
python3 a2a_integrated_payment_demo.py
```

This demo shows:
- Agent registration
- Capability registration
- Service discovery
- Payment request via A2A
- Solana payment execution
- Payment confirmation

#### 3. **SERV Discovery Demo**
```bash
cd A2A/demo
python3 a2a_serv_discovery_demo.py
```

This demo shows:
- Agent capability registration
- SERV service registration
- Service discovery via SERV infrastructure
- Service filtering

#### 4. **OpenSERV Workflow Demo**
```bash
cd A2A/demo
export OPENSERV_ENDPOINT="https://api.openserv.ai/agents/demo"
python3 a2a_openserv_workflow_demo.py
```

This demo shows:
- OpenSERV agent registration
- Workflow execution via A2A Protocol
- A2A message routing
- OpenSERV integration

### Complete Flow Example

```python
from a2a_integrated_payment_demo import A2AIntegratedClient

# Create provider agent
provider = A2AIntegratedClient()
provider.register_avatar("provider_agent", "provider@example.com", "password")
provider.authenticate("provider_agent", "password")
provider.create_solana_wallet()
provider.register_capabilities(
    services=["data-analysis"],
    skills=["Python"],
    pricing={"data-analysis": 0.1}
)

# Create consumer agent
consumer = A2AIntegratedClient()
consumer.register_avatar("consumer_agent", "consumer@example.com", "password")
consumer.authenticate("consumer_agent", "password")
consumer.create_solana_wallet()

# Discover provider
agents = consumer.discover_agents_by_service("data-analysis")
provider_id = agents[0]["agentId"]

# Send payment request
consumer.send_a2a_payment_request(provider_id, 0.01, "Data analysis service")

# Execute payment
consumer.send_solana_payment(provider.wallet_address, 0.01)
```

---

## Testing

### Test Scripts

- **Bash:** `A2A/test/test_a2a_endpoints.sh`
- **Python:** `A2A/test/test_a2a_endpoints.py`
- **Comprehensive:** `A2A/test/run_a2a_tests.sh`
- **SERV Integration:** `A2A/test/test_a2a_serv_integration.py`
- **OpenSERV Integration:** `A2A/test/test_a2a_openserv_integration.py`

### Test Coverage

| Component | Status |
|-----------|--------|
| Agent Registration | ✅ |
| Capability Registration | ✅ |
| Service Discovery | ✅ |
| JSON-RPC 2.0 | ✅ |
| Payment Requests | ✅ |
| Message Queuing | ✅ |
| Solana Integration | ✅ |
| SERV Integration | ✅ |
| OpenSERV Integration | ✅ |

### Running Tests

```bash
# Set environment variables
export JWT_TOKEN="your_jwt_token"
export AGENT_ID="optional_agent_id"
export TARGET_AGENT_ID="optional_target_id"

# Run tests
cd A2A/test
./run_a2a_tests.sh
```

---

## Integration

### SERV Infrastructure Integration

The A2A Protocol integrates with SERV infrastructure (ONET Unified Architecture) for unified service discovery:

- **Service Registration** - Register A2A agents as SERV UnifiedServices
- **Service Discovery** - Discover agents via SERV infrastructure
- **Unified Registry** - Single point of service registration and discovery

**Endpoints:**
- `POST /api/a2a/agent/register-service` - Register agent as SERV service
- `GET /api/a2a/agents/discover-serv` - Discover agents via SERV
- `GET /api/a2a/agents/discover-serv?service={name}` - Discover by service

See [`docs/INTEGRATION_GUIDE.md`](docs/INTEGRATION_GUIDE.md) for details.

### OpenSERV Integration

The A2A Protocol integrates with OpenSERV for AI agent workflow execution:

- **Agent Registration** - Register OpenSERV agents as A2A agents
- **Workflow Execution** - Execute AI workflows via OpenSERV through A2A Protocol
- **Unified Communication** - Route workflows through A2A messaging system

**Endpoints:**
- `POST /api/a2a/openserv/register` - Register OpenSERV agent
- `POST /api/a2a/workflow/execute` - Execute AI workflow

See [`docs/INTEGRATION_GUIDE.md`](docs/INTEGRATION_GUIDE.md) and [`docs/A2A_OPENSERV_INTEGRATION.md`](docs/A2A_OPENSERV_INTEGRATION.md) for details.

### Payment Integration

The A2A Protocol integrates seamlessly with Solana payments:

1. **Service Discovery** → Find agents via A2A
2. **Payment Request** → Send via A2A JSON-RPC
3. **Payment Execution** → Execute via Solana
4. **Payment Confirmation** → Confirm via A2A

See [`demo/A2A_PAYMENT_INTEGRATION.md`](demo/A2A_PAYMENT_INTEGRATION.md) for details.

### OASIS Platform Integration

The A2A Protocol is fully integrated with:
- **Avatar System** - Agents are AvatarType.Agent
- **Wallet Manager** - Solana wallet creation and management
- **Key Manager** - Public key to avatar lookup
- **Storage Providers** - LocalFileOASIS for wallet storage
- **SERV Infrastructure** - ONET Unified Architecture for service registry

---

## Protocol Compliance

### Official A2A Protocol

This implementation follows the [official A2A Protocol specification](https://github.com/a2aproject/A2A).

**Compliance Status:**

| Feature | Status |
|---------|--------|
| JSON-RPC 2.0 Format | ✅ Complete |
| Agent Cards | ✅ Complete |
| HTTP(S) Transport | ✅ Complete |
| Service Discovery | ✅ Complete |
| Task Management | ✅ Complete |
| Payment Requests | ✅ Complete |
| Health Checks | ✅ Complete |

See [`A2A_PROTOCOL_ALIGNMENT.md`](A2A_PROTOCOL_ALIGNMENT.md) for detailed comparison.

---

## Documentation

### Core Documentation

- [`IMPLEMENTATION_COMPLETE.md`](IMPLEMENTATION_COMPLETE.md) - Implementation summary
- [`A2A_PROTOCOL_ALIGNMENT.md`](A2A_PROTOCOL_ALIGNMENT.md) - Protocol compliance
- [`AGENT_IMPLEMENTATION_SUMMARY.md`](AGENT_IMPLEMENTATION_SUMMARY.md) - Agent type implementation
- [`OASIS_A2A_PROTOCOL_DOCUMENTATION.md`](OASIS_A2A_PROTOCOL_DOCUMENTATION.md) - Protocol details

### API Documentation

- [`docs/OASIS_A2A_OPENAPI_DOCUMENTATION.md`](docs/OASIS_A2A_OPENAPI_DOCUMENTATION.md) - Complete API reference
- [`TESTING_GUIDE.md`](TESTING_GUIDE.md) - Testing instructions
- [`TEST_RESULTS.md`](TEST_RESULTS.md) - Test results

### Integration Documentation

- [`docs/A2A_OPENSERV_INTEGRATION.md`](docs/A2A_OPENSERV_INTEGRATION.md) - SERV and OpenSERV integration plan
- [`docs/INTEGRATION_GUIDE.md`](docs/INTEGRATION_GUIDE.md) - Integration guide and examples
- [`docs/TROUBLESHOOTING_GUIDE.md`](docs/TROUBLESHOOTING_GUIDE.md) - Troubleshooting common issues

### Demo Documentation

- [`demo/A2A_PAYMENT_INTEGRATION.md`](demo/A2A_PAYMENT_INTEGRATION.md) - Payment integration guide
- [`demo/a2a_integrated_payment_demo.py`](demo/a2a_integrated_payment_demo.py) - Integrated payment demo

---

## Project Structure

```
A2A/
├── README.md                          # This file
├── IMPLEMENTATION_COMPLETE.md         # Implementation summary
├── A2A_PROTOCOL_ALIGNMENT.md         # Protocol compliance
├── AGENT_IMPLEMENTATION_SUMMARY.md    # Agent implementation
├── TESTING_GUIDE.md                   # Testing guide
├── TEST_RESULTS.md                    # Test results
│
├── docs/
│   ├── OASIS_A2A_OPENAPI_DOCUMENTATION.md    # API documentation
│   ├── A2A_OPENSERV_INTEGRATION.md           # SERV/OpenSERV integration plan
│   ├── INTEGRATION_GUIDE.md                  # Integration guide
│   └── TROUBLESHOOTING_GUIDE.md              # Troubleshooting guide
│
├── demo/
│   ├── a2a_solana_payment_demo.py            # Original payment demo
│   ├── a2a_integrated_payment_demo.py        # Integrated A2A payment demo
│   ├── a2a_serv_discovery_demo.py            # SERV discovery demo
│   ├── a2a_openserv_workflow_demo.py         # OpenSERV workflow demo
│   └── A2A_PAYMENT_INTEGRATION.md            # Payment integration guide
│
└── test/
    ├── test_a2a_endpoints.sh                 # Bash test script
    ├── test_a2a_endpoints.py                 # Python test script
    ├── test_a2a_serv_integration.py          # SERV integration tests
    ├── test_a2a_openserv_integration.py      # OpenSERV integration tests
    └── run_a2a_tests.sh                      # Comprehensive test script
```

---

## Contributing

We welcome contributions! Please see the [OASIS API Contributing Guidelines](https://github.com/NextGenSoftwareUK/Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK/blob/master/CONTRIBUTING.md).

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style

- Follow C# coding conventions
- Use XML comments for all public APIs
- Include unit tests for new features
- Update documentation

---

## License

This project is part of the OASIS Platform and is licensed under the same license as the main OASIS repository.

---

## Support

- **GitHub Issues:** [OASIS API Issues](https://github.com/NextGenSoftwareUK/Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK/issues)
- **Telegram:** [OASIS API Hackalong](https://t.me/oasisapihackalong)
- **Discord:** [Our World Discord](https://discord.gg/q9gMKU6)
- **Email:** ourworld@nextgensoftware.co.uk

---

## Acknowledgments

- [A2A Project](https://github.com/a2aproject/A2A) - Official A2A Protocol specification
- [OASIS Platform](https://github.com/NextGenSoftwareUK/Our-World-OASIS-API-HoloNET-HoloUnity-And-.NET-HDK) - Core platform
- [Solana](https://solana.com/) - Blockchain infrastructure

---

## Version History

### v1.0.0 (January 2026)
- ✅ Initial A2A Protocol implementation
- ✅ JSON-RPC 2.0 support
- ✅ Agent Cards
- ✅ Service discovery
- ✅ Payment integration
- ✅ Complete test suite
- ✅ Full documentation

---

**Last Updated:** January 5, 2026  
**OASIS A2A Version:** v1.0.0  
**A2A Protocol Version:** v0.3.0

