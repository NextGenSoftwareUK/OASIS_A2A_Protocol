# A2A Protocol Payment Integration

**Date:** January 5, 2026  
**Status:** ✅ **Integrated Payment Demo Ready**

---

## Overview

This integration combines the A2A Protocol with Solana payments to enable autonomous agents to:
1. **Discover** services via A2A Protocol
2. **Request** payments via A2A JSON-RPC messages
3. **Execute** payments via Solana blockchain
4. **Confirm** payments via A2A Protocol

---

## Integration Flow

```
┌─────────────┐                    ┌─────────────┐
│  Agent A    │                    │  Agent B    │
│ (Provider)  │                    │ (Consumer)  │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │ 1. Register Capabilities         │
       │    (A2A Protocol)                │
       ├──────────────────────────────────┤
       │                                  │
       │                                  │ 2. Discover Services
       │                                  │    (A2A Protocol)
       │                                  ├─────────────────────┐
       │                                  │                     │
       │                                  │ 3. Send Payment Request
       │                                  │    (A2A JSON-RPC)
       │                                  ├─────────────────────┤
       │                                  │                     │
       │ 4. Receive Payment Request       │                     │
       │    (A2A Messages)                │                     │
       │◄─────────────────────────────────┤                     │
       │                                  │                     │
       │                                  │ 5. Execute Payment
       │                                  │    (Solana)
       │                                  ├─────────────────────┤
       │                                  │                     │
       │ 6. Receive Payment               │                     │
       │    (Solana Transaction)          │                     │
       │◄─────────────────────────────────┤                     │
       │                                  │                     │
       │                                  │ 7. Send Confirmation
       │                                  │    (A2A Protocol)
       │                                  ├─────────────────────┘
       │                                  │
```

---

## Key Features

### ✅ A2A Protocol Integration

1. **Service Discovery**
   - Agents register capabilities via `/api/a2a/agent/capabilities`
   - Consumers discover providers via `/api/a2a/agents/by-service/{service}`
   - Agent Cards provide connection information

2. **Payment Requests**
   - Send payment requests via JSON-RPC 2.0: `payment_request` method
   - Messages queued in A2A message system
   - Agents can check pending messages via `/api/a2a/messages`

3. **Payment Confirmation**
   - Send payment confirmations via A2A Protocol
   - Link Solana transaction hash to A2A message
   - Track payment status in A2A message queue

### ✅ Solana Payment Integration

1. **Wallet Creation**
   - Create Solana wallets for agents
   - Store wallets with private keys securely
   - Link wallets to agent avatars

2. **Payment Execution**
   - Execute payments via `/api/solana/send`
   - Support for memo text (service description)
   - Transaction hash returned for confirmation

3. **Funding**
   - Admin wallet funds agent wallets
   - Automatic funding from OASIS_DNA.json wallet
   - Support for devnet faucet as fallback

---

## Demo Script

**File:** `A2A/demo/a2a_integrated_payment_demo.py`

### Usage

```bash
cd A2A/demo
python3 a2a_integrated_payment_demo.py
```

### What It Does

1. **Creates Agent A (Provider)**
   - Registers as Agent type avatar
   - Creates Solana wallet
   - Registers capabilities: `data-analysis`, `ai-processing`

2. **Creates Agent B (Consumer)**
   - Registers as Agent type avatar
   - Creates Solana wallet

3. **Service Discovery**
   - Agent B discovers Agent A via A2A Protocol
   - Retrieves Agent Card with capabilities

4. **Payment Flow**
   - Agent B sends payment request via A2A JSON-RPC
   - Agent A receives payment request in message queue
   - Agent B executes Solana payment
   - Payment confirmation sent via A2A Protocol

---

## API Endpoints Used

### A2A Protocol Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/a2a/agent/capabilities` | POST | Register agent capabilities |
| `/api/a2a/agents/by-service/{service}` | GET | Discover agents by service |
| `/api/a2a/agent-card/{agentId}` | GET | Get Agent Card |
| `/api/a2a/jsonrpc` | POST | Send A2A messages (payment_request) |
| `/api/a2a/messages` | GET | Get pending messages |

### Solana Payment Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/wallet/avatar/{id}/create-wallet` | POST | Create Solana wallet |
| `/api/solana/send` | POST | Execute Solana payment |

---

## Example Flow

### 1. Register Capabilities

```python
agent_a.register_capabilities(
    services=["data-analysis", "ai-processing"],
    skills=["Python", "Machine Learning"],
    pricing={"data-analysis": 0.1, "ai-processing": 0.15},
    description="AI service provider"
)
```

### 2. Discover Agents

```python
discovered_agents = agent_b.discover_agents_by_service("data-analysis")
# Returns list of agents providing "data-analysis" service
```

### 3. Send Payment Request (A2A)

```python
message_id = agent_b.send_a2a_payment_request(
    to_agent_id=agent_a.avatar_id,
    amount_sol=0.01,
    description="Data analysis service"
)
```

### 4. Execute Payment (Solana)

```python
tx_hash = agent_b.send_solana_payment(
    to_wallet_address=agent_a.wallet_address,
    amount_sol=0.01,
    memo_text="A2A Payment: Data analysis service"
)
```

### 5. Check Messages

```python
messages = agent_a.get_pending_messages()
# Returns list of pending A2A messages including payment requests
```

---

## Benefits of Integration

### ✅ **Decoupled Architecture**
- Service discovery separate from payment execution
- Agents can negotiate before payment
- Payment requests can be queued and processed asynchronously

### ✅ **Service Discovery**
- Agents can find each other by service type
- No need to hardcode agent addresses
- Dynamic agent marketplace

### ✅ **Payment Tracking**
- Payment requests tracked in A2A message system
- Transaction hashes linked to A2A messages
- Full audit trail of agent interactions

### ✅ **Protocol Compliance**
- Follows official A2A Protocol specification
- JSON-RPC 2.0 compliant
- Standardized message format

---

## Future Enhancements

1. **Payment Negotiation**
   - Agents negotiate price via A2A Protocol
   - Multi-step negotiation flow
   - Price discovery mechanisms

2. **Escrow Services**
   - Hold payments in escrow until service completion
   - Automatic release on service verification
   - Dispute resolution via A2A Protocol

3. **Reputation System**
   - Track payment history in A2A messages
   - Build reputation scores from transactions
   - Use reputation for service selection

4. **Multi-Agent Payments**
   - Split payments across multiple agents
   - Payment routing via A2A Protocol
   - Complex payment workflows

---

## Testing

### Run the Demo

```bash
# Make sure API is running
cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI
dotnet run --urls http://localhost:5003

# In another terminal, run the demo
cd A2A/demo
python3 a2a_integrated_payment_demo.py
```

### Expected Output

```
✅ Avatar registered: provider_1234567890
✅ Authenticated: provider_1234567890
✅ Wallet created: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
✅ Capabilities registered: data-analysis, ai-processing
✅ Found 1 agent(s) providing 'data-analysis'
✅ Payment request sent via A2A (Message ID: ...)
✅ Payment sent! Transaction: ...
✅ Payment confirmation sent via A2A
```

---

## Conclusion

The A2A Protocol payment integration provides a complete solution for:
- ✅ Agent service discovery
- ✅ Payment request management
- ✅ Solana payment execution
- ✅ Payment confirmation tracking

**Status:** Ready for production use! 🎉

---

**Last Updated:** January 5, 2026  
**Demo Script:** `A2A/demo/a2a_integrated_payment_demo.py`

