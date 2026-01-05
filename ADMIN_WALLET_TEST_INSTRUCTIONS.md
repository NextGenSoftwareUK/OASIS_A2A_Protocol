# Admin Wallet Connection Test

## Purpose
Test if the OASIS_ADMIN avatar is connected to the wallet address in OASIS_DNA.json

## Configuration
- **Admin Username:** `OASIS_ADMIN`
- **Admin Password:** `Uppermall1!`
- **Admin Wallet (from OASIS_DNA.json):** `6rF4zzvuBgM5RgftahPQHuPfp9WmVLYkGn44CkbRijfv`
- **Funding Amount:** `0.1 SOL` per agent

## Test Scripts

### 1. Quick Admin Wallet Test
```bash
cd /Users/maxgershfield/OASIS_CLEAN
python3 A2A/demo/test_admin_wallet.py
```

This will:
- ✅ Authenticate as OASIS_ADMIN
- ✅ Check if OASIS_ADMIN has any Solana wallets
- ✅ Verify if any wallet matches the OASIS_DNA.json address
- ✅ Report if automatic funding will work

### 2. Full A2A Payment Demo
```bash
cd /Users/maxgershfield/OASIS_CLEAN
python3 A2A/demo/a2a_solana_payment_demo.py
```

This will:
- ✅ Create two agent avatars
- ✅ Create Solana wallets for both
- ✅ Attempt to fund them with 0.1 SOL each from admin wallet
- ✅ Have Agent A pay Agent B
- ✅ Show all transaction details

## Prerequisites

1. **Start the OASIS API:**
   ```bash
   cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI
   dotnet run --urls http://localhost:5003
   ```

2. **Wait for API to be ready** (usually 10-30 seconds)

3. **Run the test script**

## Expected Results

### Scenario 1: Wallet is Connected ✅
If OASIS_ADMIN's wallet matches OASIS_DNA.json:
- Authentication will succeed
- Wallet will be found
- Automatic funding will work
- Demo will complete successfully

### Scenario 2: Wallet is NOT Connected ⚠️
If OASIS_ADMIN doesn't have the wallet from OASIS_DNA.json:
- Authentication will succeed
- No matching wallet will be found
- Script will fall back to manual funding instructions
- You may need to:
  - Create a Solana wallet for OASIS_ADMIN avatar
  - Link the OASIS_DNA.json wallet to OASIS_ADMIN
  - Or use a different funding method

## Alternative: Direct Wallet Usage

If OASIS_ADMIN authentication works but the wallet isn't linked, we can:
1. Create a Solana wallet for OASIS_ADMIN avatar
2. Import the OASIS_DNA.json wallet to OASIS_ADMIN
3. Or modify the script to use the wallet address directly (if API allows)

## Notes

- The admin wallet has **5.83 SOL** balance (checked via Solana RPC)
- Funding amount is set to **0.1 SOL** per agent (configurable)
- All transactions are on **Solana Devnet**
- Transaction hashes will be shown with Solana Explorer links




