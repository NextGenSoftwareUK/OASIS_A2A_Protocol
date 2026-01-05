#!/usr/bin/env python3
"""
A2A Protocol Integrated Solana Payment Demo

This script demonstrates the complete A2A Protocol integrated payment flow:
1. Create two agent avatars
2. Register agent capabilities via A2A
3. Discover agents via A2A service discovery
4. Send payment request via A2A JSON-RPC
5. Execute Solana payment
6. Send payment confirmation via A2A

Requirements:
    pip install requests

Usage:
    python a2a_integrated_payment_demo.py
"""

import requests
import json
import time
import sys
import subprocess
from typing import Optional, Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:5003"

# Solana constants
SOLANA_PROVIDER_TYPE = 3  # SolanaOASIS
LAMPORTS_PER_SOL = 1_000_000_000  # 1 SOL = 1 billion lamports

# Admin wallet from OASIS_DNA.json (SolanaOASIS.PublicKey)
ADMIN_WALLET_ADDRESS = "6rF4zzvuBgM5RgftahPQHuPfp9WmVLYkGn44CkbRijfv"
ADMIN_USERNAME = "OASIS_ADMIN"
ADMIN_PASSWORD = "Uppermall1!"

# Funding amount per agent wallet (in SOL)
FUNDING_AMOUNT_SOL = 0.05  # 0.05 SOL per agent
PAYMENT_AMOUNT_SOL = 0.01  # 0.01 SOL payment


class A2AIntegratedClient:
    """Client for A2A Protocol integrated payments"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.avatar_id: Optional[str] = None
        self.username: Optional[str] = None
        self.wallet_address: Optional[str] = None
        
    def register_avatar(self, username: str, email: str, password: str, 
                       first_name: str = "Agent", last_name: str = "User",
                       avatar_type: str = "Agent") -> Dict[str, Any]:
        """Register a new agent avatar"""
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
        
        payload_json = json.dumps(payload)
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
            result = data.get("result", {})
            if data.get("statusCode") == 200 and not result.get("isError"):
                self.avatar_id = result.get("result", {}).get("id")
                self.username = username
                print(f"✅ Avatar registered: {username} (ID: {self.avatar_id})")
                return data
        
        print(f"❌ Registration failed")
        return {}
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        url = f"{self.base_url}/api/avatar/authenticate"
        payload = {"username": username, "password": password}
        
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and not data.get("isError"):
            result = data.get("result", {}).get("result", {}) or data.get("result", {})
            self.token = result.get("jwtToken") or result.get("token")
            self.avatar_id = result.get("id") or result.get("avatarId")
            self.username = username
            print(f"✅ Authenticated: {username}")
            return True
        
        print(f"❌ Authentication failed")
        return False
    
    def register_capabilities(self, services: List[str], skills: List[str],
                            pricing: Dict[str, float], description: str = "") -> bool:
        """Register agent capabilities via A2A Protocol"""
        if not self.token:
            print("❌ Must authenticate first")
            return False
        
        url = f"{self.base_url}/api/a2a/agent/capabilities"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "services": services,
            "pricing": pricing,
            "skills": skills,
            "status": 0,  # Available = 0
            "max_concurrent_tasks": 3,
            "description": description
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print(f"✅ Capabilities registered: {', '.join(services)}")
            return True
        
        print(f"❌ Failed to register capabilities: {data.get('error', 'Unknown error')}")
        return False
    
    def discover_agents_by_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Discover agents via A2A Protocol"""
        url = f"{self.base_url}/api/a2a/agents/by-service/{service_name}"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            agents = data.get("$values", []) if isinstance(data, dict) else data
            if isinstance(agents, list):
                print(f"✅ Found {len(agents)} agent(s) providing '{service_name}'")
                return agents
        
        return []
    
    def get_agent_card(self, agent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get Agent Card via A2A Protocol"""
        if not agent_id:
            agent_id = self.avatar_id
        
        if not agent_id:
            return None
        
        url = f"{self.base_url}/api/a2a/agent-card/{agent_id}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        
        return None
    
    def send_a2a_payment_request(self, to_agent_id: str, amount_sol: float,
                                 description: str) -> Optional[str]:
        """Send payment request via A2A JSON-RPC"""
        if not self.token:
            print("❌ Must authenticate first")
            return None
        
        url = f"{self.base_url}/api/a2a/jsonrpc"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "payment_request",
            "params": {
                "to_agent_id": to_agent_id,
                "amount": amount_sol,
                "description": description,
                "currency": "SOL"
            },
            "id": f"payment-{int(time.time())}"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and data.get("result"):
            message_id = data.get("result", {}).get("message_id")
            print(f"✅ Payment request sent via A2A (Message ID: {message_id})")
            return message_id
        
        error = data.get("error", {})
        print(f"❌ Payment request failed: {error.get('message', 'Unknown error')}")
        return None
    
    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """Get pending A2A messages"""
        if not self.token:
            return []
        
        url = f"{self.base_url}/api/a2a/messages"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            messages = data.get("$values", []) if isinstance(data, dict) else data
            return messages if isinstance(messages, list) else []
        
        return []
    
    def create_solana_wallet(self) -> bool:
        """Create a Solana wallet for the authenticated avatar"""
        if not self.token or not self.avatar_id:
            print("❌ Must authenticate first")
            return False
        
        url = f"{self.base_url}/api/wallet/avatar/{self.avatar_id}/create-wallet?providerTypeToLoadSave=LocalFileOASIS"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": "Solana Wallet",
            "description": "Main Solana wallet",
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
            return True
        
        print(f"❌ Wallet creation failed")
        return False
    
    def send_solana_payment(self, to_wallet_address: str, amount_sol: float,
                           memo_text: str = "") -> Optional[str]:
        """Send a Solana payment"""
        if not self.token or not self.wallet_address:
            print("❌ Must authenticate and have wallet")
            return None
        
        url = f"{self.base_url}/api/solana/send"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        amount_lamports = int(amount_sol * LAMPORTS_PER_SOL)
        payload = {
            "fromAccount": {"publicKey": self.wallet_address},
            "toAccount": {"publicKey": to_wallet_address},
            "amount": amount_lamports,
            "memoText": memo_text,
            "lampposts": 5000
        }
        
        print(f"💸 Sending {amount_sol} SOL to {to_wallet_address[:8]}...{to_wallet_address[-8:]}")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        data = response.json()
        
        if response.status_code == 200 and not data.get("isError"):
            tx_hash = data.get("result", {}).get("transactionHash")
            print(f"✅ Payment sent! Transaction: {tx_hash}")
            return tx_hash
        
        print(f"❌ Payment failed: {data.get('message', 'Unknown error')}")
        return None
    
    def fund_wallet(self, to_wallet_address: str, amount_sol: float) -> Optional[str]:
        """Fund a wallet from admin"""
        return self.send_solana_payment(
            to_wallet_address=to_wallet_address,
            amount_sol=amount_sol,
            memo_text="Initial funding"
        )


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Main A2A integrated payment demo"""
    print_section("A2A Protocol Integrated Solana Payment Demo")
    
    # Check API connectivity
    try:
        response = requests.get(f"{API_BASE_URL}/api/a2a/agents", timeout=5)
        print(f"✅ API is reachable at {API_BASE_URL}")
    except Exception as e:
        print(f"❌ Cannot reach API at {API_BASE_URL}: {e}")
        sys.exit(1)
    
    # Step 1: Create and setup Agent A (Service Provider)
    print_section("Step 1: Create Agent A (Service Provider)")
    agent_a = A2AIntegratedClient(API_BASE_URL)
    agent_a_username = f"provider_{int(time.time())}"
    
    if not agent_a.register_avatar(
        username=agent_a_username,
        email=f"{agent_a_username}@example.com",
        password="SecurePassword123!",
        first_name="Agent",
        last_name="A",
        avatar_type="Agent"
    ):
        sys.exit(1)
    
    if not agent_a.authenticate(agent_a_username, "SecurePassword123!"):
        sys.exit(1)
    
    if not agent_a.create_solana_wallet():
        sys.exit(1)
    
    # Register Agent A capabilities
    print_section("Step 2: Register Agent A Capabilities (A2A Protocol)")
    agent_a.register_capabilities(
        services=["data-analysis", "ai-processing"],
        skills=["Python", "Machine Learning", "Data Science"],
        pricing={"data-analysis": 0.1, "ai-processing": 0.15},
        description="AI and data analysis service provider"
    )
    
    # Step 3: Create and setup Agent B (Service Consumer)
    print_section("Step 3: Create Agent B (Service Consumer)")
    agent_b = A2AIntegratedClient(API_BASE_URL)
    agent_b_username = f"consumer_{int(time.time())}"
    
    if not agent_b.register_avatar(
        username=agent_b_username,
        email=f"{agent_b_username}@example.com",
        password="SecurePassword123!",
        first_name="Agent",
        last_name="B",
        avatar_type="Agent"
    ):
        sys.exit(1)
    
    if not agent_b.authenticate(agent_b_username, "SecurePassword123!"):
        sys.exit(1)
    
    if not agent_b.create_solana_wallet():
        sys.exit(1)
    
    # Step 4: Agent B discovers Agent A via A2A Protocol
    print_section("Step 4: Agent B Discovers Agent A (A2A Service Discovery)")
    discovered_agents = agent_b.discover_agents_by_service("data-analysis")
    
    if not discovered_agents:
        print("⚠️  No agents found. Waiting 2 seconds and retrying...")
        time.sleep(2)
        discovered_agents = agent_b.discover_agents_by_service("data-analysis")
    
    if not discovered_agents:
        print("❌ Agent A not found via service discovery")
        sys.exit(1)
    
    # Find Agent A in discovered agents
    agent_a_card = None
    for agent in discovered_agents:
        if agent.get("agentId") == agent_a.avatar_id:
            agent_a_card = agent
            break
    
    if not agent_a_card:
        print("❌ Agent A not found in discovery results")
        sys.exit(1)
    
    print(f"✅ Found Agent A:")
    print(f"   Name: {agent_a_card.get('name')}")
    print(f"   Services: {', '.join(agent_a_card.get('capabilities', {}).get('services', []))}")
    print(f"   Skills: {', '.join(agent_a_card.get('capabilities', {}).get('skills', []))}")
    
    # Step 5: Fund wallets
    print_section("Step 5: Fund Agent Wallets")
    admin_client = A2AIntegratedClient(API_BASE_URL)
    
    if admin_client.authenticate(ADMIN_USERNAME, ADMIN_PASSWORD):
        admin_client.wallet_address = ADMIN_WALLET_ADDRESS
        print(f"💸 Funding Agent A...")
        admin_client.fund_wallet(agent_a.wallet_address, FUNDING_AMOUNT_SOL)
        print(f"💸 Funding Agent B...")
        admin_client.fund_wallet(agent_b.wallet_address, FUNDING_AMOUNT_SOL)
        print("\n⏳ Waiting 30 seconds for funding transactions to confirm...")
        time.sleep(30)
    else:
        print("⚠️  Admin authentication failed - skipping funding")
        print("   Note: Payment will fail if wallets are not funded")
    
    # Step 6: Agent B sends payment request via A2A Protocol
    print_section("Step 6: Agent B Sends Payment Request (A2A Protocol)")
    service_description = "Data analysis service - Q4 sales report"
    message_id = agent_b.send_a2a_payment_request(
        to_agent_id=agent_a.avatar_id,
        amount_sol=PAYMENT_AMOUNT_SOL,
        description=service_description
    )
    
    if not message_id:
        print("⚠️  Payment request failed, but continuing with direct payment...")
    
    # Step 7: Agent A checks for pending messages
    print_section("Step 7: Agent A Checks Pending Messages (A2A Protocol)")
    time.sleep(1)  # Small delay for message processing
    messages = agent_a.get_pending_messages()
    
    if messages:
        print(f"✅ Agent A has {len(messages)} pending message(s)")
        for msg in messages:
            print(f"   Message Type: {msg.get('messageType')}")
            print(f"   Content: {msg.get('content', 'N/A')}")
    else:
        print("⚠️  No pending messages found")
    
    # Step 8: Execute Solana payment
    print_section("Step 8: Execute Solana Payment")
    tx_hash = agent_b.send_solana_payment(
        to_wallet_address=agent_a.wallet_address,
        amount_sol=PAYMENT_AMOUNT_SOL,
        memo_text=f"A2A Payment: {service_description}"
    )
    
    # Step 9: Send payment confirmation via A2A
    if tx_hash:
        print_section("Step 9: Send Payment Confirmation (A2A Protocol)")
        confirmation_message_id = agent_b.send_a2a_payment_request(
            to_agent_id=agent_a.avatar_id,
            amount_sol=PAYMENT_AMOUNT_SOL,
            description=f"Payment confirmed: {tx_hash}"
        )
        
        if confirmation_message_id:
            print(f"✅ Payment confirmation sent via A2A")
    
    # Summary
    print_section("Demo Summary")
    print(f"✅ Agent A (Provider):")
    print(f"   Username: {agent_a_username}")
    print(f"   Wallet: {agent_a.wallet_address}")
    print(f"   Services: data-analysis, ai-processing")
    
    print(f"\n✅ Agent B (Consumer):")
    print(f"   Username: {agent_b_username}")
    print(f"   Wallet: {agent_b.wallet_address}")
    
    if tx_hash:
        print(f"\n✅ Payment Successful!")
        print(f"   Amount: {PAYMENT_AMOUNT_SOL} SOL")
        print(f"   Transaction: {tx_hash}")
        print(f"   Explorer: https://explorer.solana.com/tx/{tx_hash}?cluster=devnet")
    
    print("\n" + "=" * 70)
    print("A2A Integrated Payment Demo Completed!")
    print("=" * 70)


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

