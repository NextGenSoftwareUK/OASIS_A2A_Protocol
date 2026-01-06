#!/usr/bin/env python3
"""
Test Script: Agent NFT Minting
Demonstrates how an agent can mint NFTs for reputation and service completion.

Usage:
    export JWT_TOKEN="your_jwt_token"
    python test_agent_nft_minting.py
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = os.getenv("OASIS_API_URL", "http://localhost:5003")
API_URL = f"{BASE_URL}/api/a2a"
JWT_TOKEN = os.getenv("JWT_TOKEN")

if not JWT_TOKEN:
    print("❌ Error: JWT_TOKEN environment variable not set")
    print("   Set it with: export JWT_TOKEN='your_token_here'")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(success, message, data=None):
    """Print a formatted result"""
    icon = "✅" if success else "❌"
    print(f"\n{icon} {message}")
    if data:
        print(f"   Details: {json.dumps(data, indent=2, default=str)}")

def check_agent_status():
    """Check if the authenticated user is an agent"""
    print_section("Step 1: Check Agent Status")
    
    # Get agent card to verify agent status
    try:
        # First, try to get current avatar info from a simple endpoint
        response = requests.get(f"{BASE_URL}/api/a2a/agent-card/my", headers=headers)
        if response.status_code == 200:
            agent_data = response.json()
            print_result(True, f"Agent found: {agent_data.get('name', 'Unknown')}")
            agent_id = agent_data.get('agent_id')
            if agent_id:
                return agent_id
    except Exception as e:
        print(f"   Note: Could not get agent card automatically: {e}")
    
    # Alternative: Use the karma endpoint which requires agent
    try:
        response = requests.get(f"{API_URL}/karma", headers=headers)
        if response.status_code == 200:
            print_result(True, "Agent authentication verified")
            return "authenticated_agent"  # Placeholder
    except Exception as e:
        print_result(False, f"Agent verification failed: {e}")
        return None

def check_karma():
    """Check current karma score"""
    print_section("Step 2: Check Current Karma")
    
    try:
        response = requests.get(f"{API_URL}/karma", headers=headers)
        if response.status_code == 200:
            data = response.json()
            karma = data.get('karma', 0)
            print_result(True, f"Current karma: {karma} points")
            return karma
        else:
            print_result(False, f"Failed to get karma: {response.status_code}")
            return 0
    except Exception as e:
        print_result(False, f"Error checking karma: {e}")
        return 0

def mint_reputation_nft(karma_score=None):
    """Mint a reputation NFT for the agent"""
    print_section("Step 3: Mint Reputation NFT")
    
    params = {}
    if karma_score:
        params['reputationScore'] = karma_score
    
    params['description'] = f"Reputation NFT minted at {datetime.now().isoformat()}"
    
    try:
        response = requests.post(
            f"{API_URL}/nft/reputation",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Reputation NFT minted successfully!")
            
            if 'result' in data:
                nft_result = data['result']
                if isinstance(nft_result, dict):
                    tx_hash = nft_result.get('transactionHash') or nft_result.get('TransactionHash')
                    if tx_hash:
                        print(f"   📦 Transaction Hash: {tx_hash}")
                        print(f"   🔗 View on blockchain: https://solscan.io/tx/{tx_hash}")
            
            return True, data
        else:
            error_msg = response.json().get('error', response.text) if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to mint NFT: {error_msg}")
            return False, None
    except Exception as e:
        print_result(False, f"Error minting NFT: {e}")
        return False, None

def mint_service_certificate(service_name="test-service"):
    """Mint a service completion certificate NFT"""
    print_section("Step 4: Mint Service Certificate NFT")
    
    request_data = {
        "serviceName": service_name,
        "description": f"Certificate for completing {service_name}",
        "taskId": None  # Optional: can link to a task ID
    }
    
    try:
        response = requests.post(
            f"{API_URL}/nft/service-certificate",
            headers=headers,
            json=request_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Service certificate NFT minted for '{service_name}'!")
            
            if 'result' in data:
                nft_result = data['result']
                if isinstance(nft_result, dict):
                    tx_hash = nft_result.get('transactionHash') or nft_result.get('TransactionHash')
                    if tx_hash:
                        print(f"   📦 Transaction Hash: {tx_hash}")
                        print(f"   🔗 View on blockchain: https://solscan.io/tx/{tx_hash}")
            
            return True, data
        else:
            error_msg = response.json().get('error', response.text) if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to mint certificate: {error_msg}")
            return False, None
    except Exception as e:
        print_result(False, f"Error minting certificate: {e}")
        return False, None

def award_karma_for_service(agent_id, service_name="test-service"):
    """Award karma for completing a service"""
    print_section("Step 5: Award Karma for Service Completion")
    
    request_data = {
        "agentId": agent_id if agent_id != "authenticated_agent" else None,
        "serviceName": service_name,
        "karmaAmount": 10
    }
    
    # If agent_id is placeholder, we'll let the endpoint use authenticated agent
    if request_data["agentId"] == "authenticated_agent":
        # Try without agentId - endpoint should use authenticated agent
        pass
    
    try:
        response = requests.post(
            f"{API_URL}/karma/award",
            headers=headers,
            json=request_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Awarded 10 karma for completing '{service_name}'")
            return True, data
        else:
            error_msg = response.json().get('error', response.text) if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to award karma: {error_msg}")
            # This might fail if we can't specify agentId - that's okay for demo
            print(f"   Note: This endpoint might require the agent ID in the request")
            return False, None
    except Exception as e:
        print_result(False, f"Error awarding karma: {e}")
        return False, None

def main():
    """Main test flow"""
    print("\n" + "🔷" * 35)
    print("   A2A Protocol - Agent NFT Minting Test")
    print("🔷" * 35)
    print(f"\n🌐 API URL: {API_URL}")
    print(f"🔑 Token: {JWT_TOKEN[:20]}...")
    
    # Step 1: Check agent status
    agent_id = check_agent_status()
    if not agent_id:
        print("\n❌ Cannot proceed: Agent authentication failed")
        print("\n💡 Tip: Make sure:")
        print("   1. You have a valid JWT token")
        print("   2. The avatar associated with the token is of type 'Agent'")
        print("   3. The OASIS API is running on", BASE_URL)
        sys.exit(1)
    
    # Step 2: Check karma
    karma = check_karma()
    
    # Step 3: Mint reputation NFT
    success, nft_data = mint_reputation_nft(karma_score=karma)
    if not success:
        print("\n⚠️  Note: NFT minting may require:")
        print("   - Solana provider configured")
        print("   - NFT provider activated")
        print("   - Sufficient balance for gas fees")
    
    # Step 4: Mint service certificate
    success, cert_data = mint_service_certificate("data-analysis")
    
    # Step 5: Award karma (optional - might need agent ID)
    if agent_id and agent_id != "authenticated_agent":
        award_karma_for_service(agent_id, "data-analysis")
    
    # Summary
    print_section("Test Summary")
    print("✅ Completed NFT minting test flow")
    print("\n📋 What happened:")
    print("   1. Verified agent authentication")
    print("   2. Checked current karma score")
    print("   3. Attempted to mint reputation NFT")
    print("   4. Attempted to mint service certificate NFT")
    print("   5. Attempted to award karma")
    
    print("\n💡 Next Steps:")
    print("   - Check your agent's NFT collection")
    print("   - Verify karma score increased")
    print("   - View NFTs on blockchain explorer")
    
    print("\n" + "=" * 70)
    print("Test Complete! 🎉")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

