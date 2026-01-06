# Test Guide: Agent NFT Minting (Fully Automated)

**Purpose:** Fully automated test for agent NFT minting - no manual setup required!

---

## Prerequisites

1. **OASIS API Running**
   ```bash
   cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI
   dotnet run --urls http://localhost:5003
   ```

2. **Python Environment**
   ```bash
   python3 --version  # Should be 3.9+
   pip install requests  # If not already installed
   ```

That's it! No manual agent creation or token management needed.

---

## Run the Test (Fully Automated)

Simply run:

```bash
cd A2A/test
python3 test_agent_nft_minting.py
```

The script will automatically:
1. ✅ Create an agent avatar
2. ✅ Authenticate as the agent
3. ✅ Register agent capabilities
4. ✅ Check karma score
5. ✅ Mint reputation NFT
6. ✅ Mint service certificate NFT
7. ✅ Award karma for service completion

---

## Expected Output

```
======================================================================
  Step 1: Check Agent Status
======================================================================
✅ Agent authentication verified

======================================================================
  Step 2: Check Current Karma
======================================================================
✅ Current karma: 0 points

======================================================================
  Step 3: Mint Reputation NFT
======================================================================
✅ Reputation NFT minted successfully!
   📦 Transaction Hash: abc123...
   🔗 View on blockchain: https://solscan.io/tx/abc123...

======================================================================
  Step 4: Mint Service Certificate NFT
======================================================================
✅ Service certificate NFT minted for 'data-analysis'!
   📦 Transaction Hash: def456...
   🔗 View on blockchain: https://solscan.io/tx/def456...

======================================================================
  Step 5: Award Karma for Service Completion
======================================================================
✅ Awarded 10 karma for completing 'data-analysis'

======================================================================
  Test Summary
======================================================================
✅ Completed NFT minting test flow
...
```

---

## Troubleshooting

### Error: Agent Creation Failed

**Problem:** Cannot create agent avatar.

**Possible causes:**
- OASIS API not running
- Database/provider not configured
- Email validation required

**Solution:**
- Make sure OASIS API is running on the correct port
- Check API logs for detailed error messages
- If email verification is required, the script will still work (agent created, just not verified)

### Error: Authentication Failed

**Problem:** Cannot authenticate as agent.

**Possible causes:**
- Agent was just created and needs a moment
- Email verification required
- Password/username mismatch

**Solution:**
- Wait a few seconds and try again
- Check if email verification is required in OASIS config
- The script will retry authentication automatically

### Error: NFT minting fails

**Possible causes:**
1. **Solana provider not configured**
   - Check OASIS DNA configuration
   - Ensure Solana provider is activated

2. **Insufficient balance**
   - Need SOL for gas fees
   - Check wallet balance

3. **NFT provider not available**
   - Verify NFTManager is properly initialized
   - Check provider configuration

### Error: "Failed to get karma"

**Problem:** Karma endpoint might require agent ID.

**Solution:**
- This is expected if agent ID isn't in the request
- The endpoint should use authenticated agent automatically

---

## Manual Testing (Alternative)

If the script doesn't work, test endpoints manually:

### 1. Check Karma

```bash
curl -X GET http://localhost:5003/api/a2a/karma \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### 2. Mint Reputation NFT

```bash
curl -X POST "http://localhost:5003/api/a2a/nft/reputation?reputationScore=100" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Mint Service Certificate

```bash
curl -X POST http://localhost:5003/api/a2a/nft/service-certificate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceName": "data-analysis",
    "description": "Certificate for data analysis service"
  }'
```

---

## What to Look For

After successful minting:

1. **Check Response**
   - Should include transaction hash
   - NFT metadata in response

2. **Verify on Blockchain**
   - Use Solscan.io with transaction hash
   - Verify NFT was minted

3. **Check Agent's NFTs**
   - Query agent's NFT collection
   - Verify new NFTs appear

---

## Next Steps

After successful test:

1. **View NFTs** - Check blockchain explorer
2. **Test Karma** - Verify karma increased
3. **Test Tasks** - Try delegating tasks
4. **Integration** - Integrate into your application

---

**Need Help?** Check `TROUBLESHOOTING_GUIDE.md` for more details.

