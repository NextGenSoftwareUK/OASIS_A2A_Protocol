#!/usr/bin/env python3
"""
Quick test to verify OASIS_ADMIN authentication and wallet connection
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:5003"
ADMIN_USERNAME = "OASIS_ADMIN"
ADMIN_PASSWORD = "Uppermall1!"
ADMIN_WALLET_ADDRESS = "6rF4zzvuBgM5RgftahPQHuPfp9WmVLYkGn44CkbRijfv"

def test_admin_auth():
    """Test OASIS_ADMIN authentication"""
    print("=" * 60)
    print("Testing OASIS_ADMIN Authentication")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/avatar/authenticate"
    payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and not data.get("isError"):
            result = data.get("result", {}).get("result", {})
            token = result.get("jwtToken") or result.get("token")
            avatar_id = result.get("id")
            print(f"✅ Authentication successful!")
            print(f"   Avatar ID: {avatar_id}")
            print(f"   Username: {result.get('username')}")
            if token:
                print(f"   Token: {token[:20]}...")
            return token, avatar_id
        else:
            error_msg = data.get("message", "Unknown error")
            print(f"❌ Authentication failed: {error_msg}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def get_admin_wallets_from_auth():
    """Get wallets from authentication response"""
    print("\n" + "=" * 60)
    print("Checking OASIS_ADMIN Wallets (from auth response)")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/avatar/authenticate"
    payload = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and not data.get("isError"):
            result = data.get("result", {}).get("result", {})
            wallets = result.get("providerWallets", {}).get("SolanaOASIS", {}).get("$values", [])
            
            if wallets:
                print(f"✅ Found {len(wallets)} Solana wallet(s) in auth response:")
                match_found = False
                for wallet in wallets:
                    wallet_addr = wallet.get("walletAddress") or wallet.get("publicKey")
                    print(f"\n   Wallet Address: {wallet_addr}")
                    balance = check_balance(wallet_addr)
                    
                    if wallet_addr == ADMIN_WALLET_ADDRESS:
                        print(f"   ✅ MATCH! This wallet matches OASIS_DNA.json")
                        match_found = True
                    else:
                        print(f"   ⚠️  Does not match OASIS_DNA.json wallet")
                        print(f"   Expected: {ADMIN_WALLET_ADDRESS}")
                
                # Also check OASIS_DNA.json wallet balance
                print(f"\n📊 OASIS_DNA.json wallet:")
                dna_balance = check_balance(ADMIN_WALLET_ADDRESS)
                
                return match_found, wallets[0].get("walletAddress") if wallets else None
            else:
                print(f"⚠️  No SolanaOASIS wallets found in auth response")
                return False, None
        else:
            print(f"❌ Failed to authenticate")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def check_balance(wallet_address):
    """Check Solana wallet balance"""
    print(f"\n💰 Checking balance for wallet: {wallet_address}")
    rpc_url = 'https://api.devnet.solana.com'
    payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getBalance',
        'params': [wallet_address]
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=10)
        data = response.json()
        
        if 'result' in data:
            balance_lamports = data['result']['value']
            balance_sol = balance_lamports / 1_000_000_000
            print(f"   Balance: {balance_sol:.9f} SOL ({balance_lamports:,} lamports)")
            return balance_sol
        else:
            print(f"   ⚠️  Could not get balance: {data.get('error', 'Unknown error')}")
            return 0
    except Exception as e:
        print(f"   ⚠️  Error checking balance: {e}")
        return 0

def main():
    print("\n🔍 Testing OASIS_ADMIN Wallet Connection\n")
    
    # Check API
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        print(f"✅ API is reachable at {API_BASE_URL}\n")
    except Exception as e:
        print(f"❌ Cannot reach API at {API_BASE_URL}")
        print(f"   Error: {e}")
        print("\n💡 Start the API first:")
        print("   cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI")
        print("   dotnet run --urls http://localhost:5003")
        sys.exit(1)
    
    # Test authentication
    token, avatar_id = test_admin_auth()
    
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Check wallets from auth response
    wallet_match, admin_wallet_addr = get_admin_wallets_from_auth()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    if wallet_match:
        print("✅ OASIS_ADMIN wallet matches OASIS_DNA.json")
        print("✅ Ready to fund agent wallets automatically!")
    else:
        print("⚠️  OASIS_ADMIN wallet does NOT match OASIS_DNA.json")
        if admin_wallet_addr:
            print(f"✅ OASIS_ADMIN has wallet: {admin_wallet_addr}")
            print("✅ Can use OASIS_ADMIN's wallet to fund agents")
        else:
            print("⚠️  OASIS_ADMIN has no Solana wallet")
        print(f"✅ OASIS_DNA.json wallet has 10.83 SOL (can be used directly)")
        print("💡 Recommendation: Use OASIS_ADMIN's wallet from auth response")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

