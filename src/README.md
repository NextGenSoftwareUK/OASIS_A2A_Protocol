# A2A Protocol Source Code

This directory contains all the A2A Protocol integration code for easy access and reference.

## Structure

```
src/
├── Managers/
│   ├── A2AManager/          # Core A2A Protocol implementation
│   └── AgentManager/        # Agent capability management
├── Controllers/             # API endpoints
└── Interfaces/              # Interface definitions
```

## Files Overview

### A2AManager Files

1. **A2AManager.cs** - Base A2A Protocol implementation
2. **A2AManager-JsonRpc.cs** - JSON-RPC 2.0 protocol handling
3. **A2AManager-SERV.cs** - SERV infrastructure integration ✅ NEW
4. **A2AManager-OpenSERV.cs** - OpenSERV agent integration ✅ NEW
5. **A2AManager-NFT.cs** - NFTManager integration ✅ NEW
6. **A2AManager-Karma.cs** - KarmaManager integration ✅ NEW
7. **A2AManager-Mission.cs** - Mission/Task delegation ✅ NEW

### AgentManager Files

1. **AgentManager.cs** - Agent capability management
2. **AgentManager-AgentCard.cs** - Agent Card generation

### Controllers

1. **A2AController.cs** - All A2A API endpoints ✅ UPDATED

### Interfaces

1. **IA2AMessage.cs** - A2A message interface
2. **IAgentCapabilities.cs** - Agent capabilities interface
3. **IAgentCard.cs** - Agent Card interface

## Location in OASIS Repository

These files are part of the main OASIS repository. Their actual locations are:

- **Managers:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Managers/`
- **Controllers:** `ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI/Controllers/`
- **Interfaces:** `OASIS Architecture/NextGenSoftware.OASIS.API.Core/Interfaces/Agent/`

## Integration Status

- ✅ **SERV Integration** - Service registry and discovery
- ✅ **OpenSERV Integration** - AI agent workflow execution
- ✅ **NFT Integration** - Reputation NFTs and certificates
- ✅ **Karma Integration** - Reputation scoring
- ✅ **Mission/Task Integration** - Task delegation system

## Documentation

See the `docs/` directory for comprehensive documentation:
- `INTEGRATION_GUIDE.md` - Integration guide
- `INTEGRATION_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- `OASIS_INTEGRATION_ANALYSIS.md` - OASIS integration analysis
- `A2A_OPENSERV_INTEGRATION.md` - OpenSERV integration plan

## Usage

These files are copies of the actual implementation in the OASIS repository. They are provided here for:
- Easy reference and review
- Documentation purposes
- Understanding the integration structure

To use these in your project, you'll need to reference them from the OASIS repository structure.

