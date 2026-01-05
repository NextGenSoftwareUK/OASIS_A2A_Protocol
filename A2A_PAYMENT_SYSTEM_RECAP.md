# Agent-to-Agent Payment System Recap
**Date:** January 2026  
**Status:** ✅ Ready for Demo with Solana Wallets

---

## Executive Summary

The OASIS API now supports **agent-to-agent (A2A) payments** using **Solana wallets**. The system enables autonomous agents to:
1. ✅ Create and authenticate avatars
2. ✅ Generate Solana wallets
3. ✅ Fund wallets with devnet SOL
4. ✅ Send payments between agents
5. ✅ Track transactions on Solana blockchain

---

## Current System Architecture

### Key Components

#### 1. **Avatar Management**
- **Registration:** `POST /api/avatar/register`
- **Authentication:** `POST /api/avatar/authenticate` → Returns JWT token
- **Avatar Types:** `User`, `System`, `Agent`, etc.

#### 2. **Wallet Management**
- **Create Wallet:** `POST /api/wallet/avatar/{avatarId}/create-wallet`
- **Provider Type:** `SolanaOASIS` (ProviderType = 3)
- **Get Wallets:** `GET /api/wallet/avatar/{avatarId}/wallets?providerType=SolanaOASIS`

#### 3. **Solana Payment Endpoint**
- **Endpoint:** `POST /api/solana/send`
- **Authorization:** Required (Bearer token)
- **Request Structure:**
  ```json
  {
    "fromAccount": {
      "publicKey": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
    },
    "toAccount": {
      "publicKey": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    },
    "amount": 1000000000,  // Amount in lamports (1 SOL = 1,000,000,000 lamports)
    "memoText": "Payment for service",
    "lampposts": 5000  // Transaction fee in lamports
  }
  ```

#### 4. **Generic Wallet Payment Endpoint** (Alternative)
- **Endpoint:** `POST /api/wallet/send_token`
- **Uses:** `IWalletTransactionRequest` interface
- **Note:** Currently has deserialization issues, use `/api/solana/send` instead

---

## API Endpoints Reference

### Avatar Endpoints

#### Register Avatar
```http
POST /api/avatar/register
Content-Type: application/json

{
  "firstName": "Agent",
  "lastName": "A",
  "email": "agenta@example.com",
  "username": "agenta",
  "password": "SecurePassword123!",
  "confirmPassword": "SecurePassword123!",
  "avatarType": "Agent",
  "acceptTerms": true
}
```

#### Authenticate Avatar
```http
POST /api/avatar/authenticate
Content-Type: application/json

{
  "username": "agenta",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "result": {
    "id": "f489231f-73c8-4642-9fc9-11efeb9698fa",
    "username": "agenta",
    "email": "agenta@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "..."
  },
  "isError": false,
  "message": "Authentication successful"
}
```

### Wallet Endpoints

#### Create Solana Wallet
```http
POST /api/wallet/avatar/{avatarId}/create-wallet
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My Solana Wallet",
  "description": "Main Solana wallet for transactions",
  "walletProviderType": 3,  // SolanaOASIS
  "generateKeyPair": true,
  "isDefaultWallet": false
}
```

**Response:**
```json
{
  "result": {
    "walletId": "f0af4ad7-cf80-4bff-8a00-acff7d1ff861",
    "name": "My Solana Wallet",
    "providerType": 3,
    "walletAddress": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "publicKey": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "isDefaultWallet": false
  },
  "isError": false,
  "isSaved": true,
  "message": "Wallet created successfully"
}
```

#### Get Wallets for Avatar
```http
GET /api/wallet/avatar/{avatarId}/wallets?providerType=SolanaOASIS
Authorization: Bearer {token}
```

### Solana Payment Endpoint

#### Send Solana Payment
```http
POST /api/solana/send
Authorization: Bearer {token}
Content-Type: application/json

{
  "fromAccount": {
    "publicKey": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
  },
  "toAccount": {
    "publicKey": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
  },
  "amount": 1000000000,  // 1 SOL in lamports
  "memoText": "Payment for service",
  "lampposts": 5000
}
```

**Response:**
```json
{
  "result": {
    "transactionHash": "5j7s8K9mN2pQ4rT6vW8xY0zA1bC3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5z"
  },
  "isError": false,
  "message": "Transaction sent successfully"
}
```

---

## Provider Types

| Provider | Value | Description |
|----------|-------|-------------|
| `SolanaOASIS` | 3 | Solana blockchain provider |
| `EthereumOASIS` | 4 | Ethereum blockchain provider |
| `MongoDBOASIS` | 1 | MongoDB storage provider |

---

## Solana Amount Conversion

- **1 SOL = 1,000,000,000 lamports**
- **Example:** To send 0.1 SOL, use `100000000` lamports
- **Example:** To send 1 SOL, use `1000000000` lamports

---

## Complete A2A Payment Flow

### Step-by-Step Process

1. **Create Agent A Avatar**
   ```bash
   POST /api/avatar/register
   # Returns: avatar_id_a
   ```

2. **Authenticate Agent A**
   ```bash
   POST /api/avatar/authenticate
   # Returns: token_a
   ```

3. **Create Solana Wallet for Agent A**
   ```bash
   POST /api/wallet/avatar/{avatar_id_a}/create-wallet
   Authorization: Bearer {token_a}
   # Returns: wallet_address_a
   ```

4. **Create Agent B Avatar**
   ```bash
   POST /api/avatar/register
   # Returns: avatar_id_b
   ```

5. **Authenticate Agent B**
   ```bash
   POST /api/avatar/authenticate
   # Returns: token_b
   ```

6. **Create Solana Wallet for Agent B**
   ```bash
   POST /api/wallet/avatar/{avatar_id_b}/create-wallet
   Authorization: Bearer {token_b}
   # Returns: wallet_address_b
   ```

7. **Fund Agent A Wallet** (from admin wallet or faucet)
   ```bash
   POST /api/solana/send
   Authorization: Bearer {admin_token}
   {
     "fromAccount": {"publicKey": "{admin_wallet}"},
     "toAccount": {"publicKey": "{wallet_address_a}"},
     "amount": 2000000000,  // 2 SOL
     "memoText": "Initial funding for Agent A"
   }
   ```

8. **Agent A Pays Agent B**
   ```bash
   POST /api/solana/send
   Authorization: Bearer {token_a}
   {
     "fromAccount": {"publicKey": "{wallet_address_a}"},
     "toAccount": {"publicKey": "{wallet_address_b}"},
     "amount": 1000000000,  // 1 SOL
     "memoText": "Payment for service"
   }
   ```

9. **Verify Transaction**
   - Check transaction hash on Solana Explorer
   - Query wallet balances

---

## Recent Updates

### Avatar & Wallet Generation Updates
Based on your recent updates:
- ✅ Improved Solana wallet generation
- ✅ Enhanced avatar creation process
- ✅ Better error handling and validation

### Known Issues & Solutions

#### Issue 1: Generic Wallet Endpoint Deserialization
- **Problem:** `/api/wallet/send_token` has interface deserialization issues
- **Solution:** Use `/api/solana/send` endpoint directly

#### Issue 2: Authorization
- **Status:** ✅ Fixed (from previous work)
- **Note:** All endpoints require valid JWT token in `Authorization: Bearer {token}` header

#### Issue 3: Email Verification
- **Configuration:** Can be bypassed in `OASIS_DNA.json`
- **Setting:** `"DoesAvatarNeedToBeVerifiedBeforeLogin": false`

---

## Testing Checklist

- [ ] Create two agent avatars
- [ ] Authenticate both agents
- [ ] Create Solana wallets for both agents
- [ ] Fund Agent A wallet with devnet SOL
- [ ] Send payment from Agent A to Agent B
- [ ] Verify transaction on Solana Explorer
- [ ] Check wallet balances

---

## Next Steps

1. **Run Demo Script:** Use the provided Python demo script to test the full flow
2. **Verify Transactions:** Check transactions on Solana Explorer (devnet)
3. **Monitor Logs:** Check API logs for any errors
4. **Extend Functionality:** Add karma updates, transaction history, etc.

---

## Resources

- **API Base URL:** `http://localhost:5003` (local) or `http://api.oasisweb4.com/` (production)
- **Solana Explorer:** https://explorer.solana.com/?cluster=devnet
- **Documentation:** See `AVATAR_AND_WALLET_CREATION_GUIDE.md`

---

## Demo Script

See `A2A/demo/a2a_solana_payment_demo.py` for a complete working demo.




