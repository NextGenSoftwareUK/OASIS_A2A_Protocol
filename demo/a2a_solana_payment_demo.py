#!/usr/bin/env python3
"""
Agent-to-Agent Solana Payment Demo

This script demonstrates the complete flow of agent-to-agent payments using Solana wallets:
1. Create two agent avatars
2. Authenticate both agents
3. Create Solana wallets for both agents
4. Fund Agent A wallet (from admin or faucet)
5. Agent A pays Agent B for a service
6. Verify the transaction

Requirements:
    pip install requests

Usage:
    python a2a_solana_payment_demo.py
"""

import requests
import json
import time
import sys
import subprocess
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:5003"
# API_BASE_URL = "http://api.oasisweb4.com/"  # Production URL

# Solana constants
SOLANA_PROVIDER_TYPE = 3  # SolanaOASIS
LAMPORTS_PER_SOL = 1_000_000_000  # 1 SOL = 1 billion lamports

# Admin wallet from OASIS_DNA.json (SolanaOASIS.PublicKey)
ADMIN_WALLET_ADDRESS = "6rF4zzvuBgM5RgftahPQHuPfp9WmVLYkGn44CkbRijfv"
ADMIN_USERNAME = "OASIS_ADMIN"  # Default admin username
ADMIN_PASSWORD = "Uppermall1!"  # OASIS_ADMIN password

# Funding amount per agent wallet (in SOL)
FUNDING_AMOUNT_SOL = 0.05  # 0.05 SOL per agent


class OASISClient:
    """Client for interacting with OASIS API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.avatar_id: Optional[str] = None
        self.username: Optional[str] = None
        self.wallet_address: Optional[str] = None
        
    def register_avatar(self, username: str, email: str, password: str, 
                       first_name: str = "Agent", last_name: str = "User",
                       avatar_type: str = "Agent") -> Dict[str, Any]:
        """Register a new avatar"""
        url = f"{self.base_url}/api/avatar/register"
        payload = {
            "title": f"{first_name} {last_name}",
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "username": username,
            "password": password,
            "confirmPassword": password,
            "avatarType": avatar_type,
            "acceptTerms": True
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Use curl via subprocess with --data-raw to avoid JSON escaping issues
        response = None
        status_code = 200
        try:
            payload_json = json.dumps(payload)
            # Use --data-raw which works better than -d for JSON
            # Note: Must use -X POST explicitly and Content-Type without charset
            curl_result = subprocess.run(
                ['curl', '-s', '-X', 'POST', url,
                 '-H', 'Content-Type: application/json',
                 '--data-raw', payload_json],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if curl_result.returncode == 0 and curl_result.stdout:
                data = json.loads(curl_result.stdout)
                # Check if there's an error in the response
                result_data = data.get("result", {})
                if data.get("status") == 400:
                    status_code = 400
                elif isinstance(result_data, dict) and result_data.get("isError"):
                    status_code = 400
                else:
                    status_code = 200
            else:
                raise Exception(f"Curl failed: {curl_result.stderr}")
        except Exception as e:
            # Fallback to requests if curl fails
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
                status_code = response.status_code
                data = response.json()
            except Exception as req_err:
                # Last resort - return error
                print(f"⚠️  Both curl and requests failed. Curl error: {e}, Requests error: {req_err}")
                return {"isError": True, "message": f"Registration failed: {e}"}
        
        # Check nested result structure
        result = data.get("result", {})
        is_error = result.get("isError", False) or data.get("isError", False)
        
        if status_code == 200 and not is_error:
            self.avatar_id = result.get("id") or result.get("result", {}).get("id")
            self.username = username
            print(f"✅ Avatar registered: {username} (ID: {self.avatar_id})")
            return data
        else:
            error_msg = result.get("message") or data.get("message", "Unknown error")
            print(f"❌ Registration failed: {error_msg}")
            if status_code == 400:
                errors = data.get("errors", {})
                if errors:
                    print(f"   Validation errors: {json.dumps(errors, indent=2)}")
            return data
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        url = f"{self.base_url}/api/avatar/authenticate"
        payload = {
            "username": username,
            "password": password
        }
        
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and not data.get("isError"):
            result = data.get("result", {}).get("result", {}) or data.get("result", {})
            self.token = result.get("jwtToken") or result.get("token")
            self.avatar_id = result.get("id")
            self.username = username
            print(f"✅ Authenticated: {username}")
            return True
        else:
            error_msg = data.get("message", "Unknown error")
            print(f"❌ Authentication failed: {error_msg}")
            return False
    
    def create_solana_wallet(self, name: str = "Solana Wallet", 
                            description: str = "Main Solana wallet") -> Dict[str, Any]:
        """Create a Solana wallet for the authenticated avatar"""
        if not self.token or not self.avatar_id:
            print("❌ Must authenticate first")
            return {}
        
        # Use LocalFileOASIS for wallet metadata storage (it's StorageLocal category)
        url = f"{self.base_url}/api/wallet/avatar/{self.avatar_id}/create-wallet?providerTypeToLoadSave=LocalFileOASIS"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": name,
            "description": description,
            "walletProviderType": SOLANA_PROVIDER_TYPE,
            "generateKeyPair": True,
            "isDefaultWallet": False
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and not data.get("isError"):
            result = data.get("result", {})
            self.wallet_address = result.get("walletAddress") or result.get("publicKey")
            print(f"✅ Wallet created: {self.wallet_address}")
            return data
        else:
            error_msg = data.get("message", "Unknown error")
            print(f"❌ Wallet creation failed: {error_msg}")
            if response.status_code == 400:
                print(f"   Response: {json.dumps(data, indent=2)}")
            return data
    
    def get_wallets(self, provider_type: str = "SolanaOASIS") -> Dict[str, Any]:
        """Get all wallets for the authenticated avatar"""
        if not self.token or not self.avatar_id:
            print("❌ Must authenticate first")
            return {}
        
        url = f"{self.base_url}/api/wallet/avatar/{self.avatar_id}/wallets"
        params = {"providerType": provider_type}
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and not data.get("isError"):
            wallets = data.get("result", {})
            if provider_type in wallets:
                wallet_list = wallets[provider_type]
                if wallet_list and len(wallet_list) > 0:
                    self.wallet_address = wallet_list[0].get("walletAddress") or wallet_list[0].get("publicKey")
                    print(f"✅ Found {len(wallet_list)} wallet(s)")
                    return data
            print("⚠️  No wallets found")
        else:
            error_msg = data.get("message", "Unknown error")
            print(f"❌ Failed to get wallets: {error_msg}")
        
        return data
    
    def send_solana_payment(self, to_wallet_address: str, amount_sol: float,
                           memo_text: str = "", lampposts: int = 5000,
                           from_wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Send a Solana payment to another wallet"""
        if not self.token:
            print("❌ Must authenticate first")
            return {}
        
        # Use provided from_wallet_address or default to self.wallet_address
        from_wallet = from_wallet_address or self.wallet_address
        if not from_wallet:
            print("❌ Must have a wallet address (either set wallet_address or provide from_wallet_address)")
            return {}
        
        url = f"{self.base_url}/api/solana/send"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Convert SOL to lamports
        amount_lamports = int(amount_sol * LAMPORTS_PER_SOL)
        
        payload = {
            "fromAccount": {
                "publicKey": from_wallet
            },
            "toAccount": {
                "publicKey": to_wallet_address
            },
            "amount": amount_lamports,
            "memoText": memo_text or f"Payment from {self.username or 'admin'}",
            "lampposts": lampposts
        }
        
        print(f"💸 Sending {amount_sol} SOL ({amount_lamports:,} lamports)")
        print(f"   From: {from_wallet[:8]}...{from_wallet[-8:]}")
        print(f"   To:   {to_wallet_address[:8]}...{to_wallet_address[-8:]}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        # Check if response is valid JSON
        try:
            data = response.json()
        except ValueError as e:
            print(f"❌ Invalid JSON response (status {response.status_code}): {response.text[:500]}")
            return {"isError": True, "message": f"Invalid response: {response.text[:200]}"}
        
        if response.status_code == 200 and not data.get("isError"):
            tx_hash = data.get("result", {}).get("transactionHash", "N/A")
            print(f"✅ Payment sent! Transaction hash: {tx_hash}")
            print(f"   View on Solana Explorer: https://explorer.solana.com/tx/{tx_hash}?cluster=devnet")
            return data
        else:
            error_msg = data.get("message", "Unknown error")
            print(f"❌ Payment failed: {error_msg}")
            if response.status_code == 400:
                print(f"   Response: {json.dumps(data, indent=2)}")
            return data
    
    def fund_wallet(self, to_wallet_address: str, amount_sol: float = FUNDING_AMOUNT_SOL,
                   memo_text: str = "Initial funding for agent wallet") -> Dict[str, Any]:
        """Fund a wallet from the admin wallet"""
        return self.send_solana_payment(
            to_wallet_address=to_wallet_address,
            amount_sol=amount_sol,
            memo_text=memo_text,
            from_wallet_address=ADMIN_WALLET_ADDRESS
        )


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    """Main demo flow"""
    print_section("Agent-to-Agent Solana Payment Demo")
    
    # Check API connectivity
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        print(f"✅ API is reachable at {API_BASE_URL}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach API at {API_BASE_URL}")
        print(f"   Error: {e}")
        print("\n💡 Make sure the OASIS API is running:")
        print("   cd ONODE/NextGenSoftware.OASIS.API.ONODE.WebAPI")
        print("   dotnet run --urls http://localhost:5003")
        sys.exit(1)
    
    # Create Agent A
    print_section("Step 1: Create Agent A")
    agent_a = OASISClient(API_BASE_URL)
    agent_a_username = f"agenta_{int(time.time())}"
    agent_a_email = f"agenta_{int(time.time())}@example.com"
    agent_a_password = "SecurePassword123!"
    
    register_result = agent_a.register_avatar(
        username=agent_a_username,
        email=agent_a_email,
        password=agent_a_password,
        first_name="Agent",
        last_name="A",
        avatar_type="Agent"  # Now using Agent type instead of User
    )
    
    if agent_a.avatar_id is None:
        print("❌ Failed to create Agent A. Exiting.")
        sys.exit(1)
    
    # Authenticate Agent A
    print_section("Step 2: Authenticate Agent A")
    if not agent_a.authenticate(agent_a_username, agent_a_password):
        print("❌ Failed to authenticate Agent A. Exiting.")
        sys.exit(1)
    
    # Create Solana wallet for Agent A
    print_section("Step 3: Create Solana Wallet for Agent A")
    wallet_result_a = agent_a.create_solana_wallet(
        name="Agent A Solana Wallet",
        description="Main wallet for Agent A"
    )
    
    if not agent_a.wallet_address:
        print("⚠️  Wallet creation didn't return address, trying to fetch wallets...")
        agent_a.get_wallets()
    
    if not agent_a.wallet_address:
        print("❌ Failed to get Agent A wallet address. Exiting.")
        sys.exit(1)
    
    # Create Agent B
    print_section("Step 4: Create Agent B")
    agent_b = OASISClient(API_BASE_URL)
    agent_b_username = f"agentb_{int(time.time())}"
    agent_b_email = f"agentb_{int(time.time())}@example.com"
    agent_b_password = "SecurePassword123!"
    
    register_result = agent_b.register_avatar(
        username=agent_b_username,
        email=agent_b_email,
        password=agent_b_password,
        first_name="Agent",
        last_name="B",
        avatar_type="Agent"  # Now using Agent type instead of User
    )
    
    if agent_b.avatar_id is None:
        print("❌ Failed to create Agent B. Exiting.")
        sys.exit(1)
    
    # Authenticate Agent B
    print_section("Step 5: Authenticate Agent B")
    if not agent_b.authenticate(agent_b_username, agent_b_password):
        print("❌ Failed to authenticate Agent B. Exiting.")
        sys.exit(1)
    
    # Create Solana wallet for Agent B
    print_section("Step 6: Create Solana Wallet for Agent B")
    wallet_result_b = agent_b.create_solana_wallet(
        name="Agent B Solana Wallet",
        description="Main wallet for Agent B"
    )
    
    if not agent_b.wallet_address:
        print("⚠️  Wallet creation didn't return address, trying to fetch wallets...")
        agent_b.get_wallets()
    
    if not agent_b.wallet_address:
        print("❌ Failed to get Agent B wallet address. Exiting.")
        sys.exit(1)
    
    # Display wallet addresses
    print_section("Wallet Information")
    print(f"Agent A Wallet: {agent_a.wallet_address}")
    print(f"Agent B Wallet: {agent_b.wallet_address}")
    
    # Funding step - automatically fund from admin wallet
    print_section("Step 7: Funding Agent Wallets")
    print(f"💰 Admin Wallet (OASIS_DNA.json): {ADMIN_WALLET_ADDRESS}")
    print(f"   Funding Amount: {FUNDING_AMOUNT_SOL} SOL per agent")
    
    # Try to authenticate as admin to fund wallets
    admin_client = OASISClient(API_BASE_URL)
    funding_success = False
    
    if ADMIN_PASSWORD:
        print(f"\n🔐 Authenticating as {ADMIN_USERNAME}...")
        if admin_client.authenticate(ADMIN_USERNAME, ADMIN_PASSWORD):
            funding_success = True
            # Use OASIS_DNA.json wallet for funding (it has 10.83 SOL balance)
            print(f"   ✅ Authenticated successfully")
            print(f"   Using OASIS_DNA.json wallet for funding (has 10.83 SOL)")
        else:
            print("⚠️  Admin authentication failed")
    else:
        print(f"\n⚠️  ADMIN_PASSWORD not set - skipping automatic funding")
        print(f"   Note: OASIS_DNA.json wallet ({ADMIN_WALLET_ADDRESS}) has 10.83 SOL")
        print(f"   But requires authentication to send payments")
    
    # Fund Agent A
    print(f"\n💸 Funding Agent A wallet...")
    if funding_success and admin_client.token:
        fund_result_a = admin_client.fund_wallet(
            to_wallet_address=agent_a.wallet_address,
            amount_sol=FUNDING_AMOUNT_SOL,
            memo_text="Initial funding for Agent A"
        )
        if fund_result_a.get("result", {}).get("transactionHash"):
            print(f"✅ Agent A funded successfully!")
        else:
            print(f"⚠️  Agent A funding may have failed. Check error above.")
    else:
        print(f"⚠️  Cannot fund automatically. Skipping funding step.")
        print(f"   Agent A wallet: {agent_a.wallet_address}")
        print(f"   Agent B wallet: {agent_b.wallet_address}")
        print(f"   To fund manually, use Solana devnet faucet: https://faucet.solana.com/")
        print(f"   Or authenticate as OASIS_ADMIN and use the admin wallet")
        print(f"\n⚠️  Continuing demo without funding - payment will fail if wallets are empty")
    
    # Fund Agent B (optional, but helpful for testing)
    print(f"\n💸 Funding Agent B wallet...")
    if funding_success and admin_client.token:
        fund_result_b = admin_client.fund_wallet(
            to_wallet_address=agent_b.wallet_address,
            amount_sol=FUNDING_AMOUNT_SOL,
            memo_text="Initial funding for Agent B"
        )
        if fund_result_b.get("result", {}).get("transactionHash"):
            print(f"✅ Agent B funded successfully!")
        else:
            print(f"⚠️  Agent B funding may have failed. Continuing anyway...")
    else:
        print(f"⚠️  Skipping Agent B funding (not required for demo)")
    
    print("\n⏳ Waiting 30 seconds for transactions to confirm...")
    time.sleep(30)
    
    # Agent A pays Agent B
    print_section("Step 8: Agent A Pays Agent B")
    payment_amount = 0.01  # 0.01 SOL (less than funding amount to ensure sufficient balance)
    service_description = "AI service provided by Agent B"
    
    payment_result = agent_a.send_solana_payment(
        to_wallet_address=agent_b.wallet_address,
        amount_sol=payment_amount,
        memo_text=f"Payment for {service_description}"
    )
    
    # Summary
    print_section("Demo Summary")
    print(f"✅ Agent A created: {agent_a_username}")
    print(f"   Wallet: {agent_a.wallet_address}")
    print(f"   Funded: {FUNDING_AMOUNT_SOL} SOL")
    print(f"\n✅ Agent B created: {agent_b_username}")
    print(f"   Wallet: {agent_b.wallet_address}")
    print(f"   Funded: {FUNDING_AMOUNT_SOL} SOL")
    
    if payment_result.get("result", {}).get("transactionHash"):
        tx_hash = payment_result["result"]["transactionHash"]
        print(f"\n✅ Payment successful!")
        print(f"   Amount: {payment_amount} SOL")
        print(f"   Transaction: {tx_hash}")
        print(f"   Explorer: https://explorer.solana.com/tx/{tx_hash}?cluster=devnet")
        print(f"\n📊 View wallets on Solana Explorer:")
        print(f"   Agent A: https://explorer.solana.com/address/{agent_a.wallet_address}?cluster=devnet")
        print(f"   Agent B: https://explorer.solana.com/address/{agent_b.wallet_address}?cluster=devnet")
    else:
        print(f"\n⚠️  Payment may have failed. Check the error messages above.")
        print("   Common issues:")
        print("   - Agent A wallet not funded")
        print("   - Insufficient balance")
        print("   - Network connectivity issues")
        print("   - Admin authentication required for funding")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

