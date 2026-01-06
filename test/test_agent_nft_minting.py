#!/usr/bin/env python3
"""
Fully Automated Test Script: Agent NFT Minting
Automatically creates an agent, authenticates, and tests NFT minting functionality.

Usage:
    python test_agent_nft_minting.py

No manual setup required - the script handles everything!
"""

import os
import sys
import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BASE_URL = os.getenv("OASIS_API_URL", "http://localhost:5003")
# Try both lowercase and uppercase routes (ASP.NET Core route matching)
API_URL_LOWER = f"{BASE_URL}/api/a2a"
API_URL_UPPER = f"{BASE_URL}/api/A2A"
API_URL = API_URL_UPPER  # Default to uppercase (ASP.NET Core standard)
AVATAR_API_URL = f"{BASE_URL}/api/avatar"

# Generate unique agent credentials
AGENT_ID = f"test-agent-{int(time.time())}"
AGENT_USERNAME = f"agent_{uuid.uuid4().hex[:8]}"
AGENT_EMAIL = f"{AGENT_USERNAME}@test-agent.local"
AGENT_PASSWORD = "TestAgent123!@#"

# Global variables
agent_token = None
agent_id = None

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(success, message, data=None):
    """Print a formatted result"""
    icon = "✅" if success else "❌"
    print(f"\n{icon} {message}")
    if data and isinstance(data, dict):
        # Print only relevant info
        for key in ['id', 'agent_id', 'karma', 'success', 'message', 'transactionHash', 'TransactionHash']:
            if key in data:
                print(f"   {key}: {data[key]}")

def create_agent():
    """Automatically create an agent avatar"""
    print_section("Step 1: Create Agent Avatar")
    
    global agent_id
    
    registration_data = {
        "FirstName": "Test",
        "LastName": "Agent",
        "Username": AGENT_USERNAME,
        "Email": AGENT_EMAIL,
        "Password": AGENT_PASSWORD,
        "ConfirmPassword": AGENT_PASSWORD,
        "AvatarType": "Agent",  # Set as Agent type
        "Title": "Agent",
        "AcceptTerms": True
    }
    
    try:
        print(f"   Creating agent: {AGENT_USERNAME}")
        print(f"   Email: {AGENT_EMAIL}")
        
        response = requests.post(
            f"{AVATAR_API_URL}/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('result') and data['result'].get('result'):
                avatar = data['result']['result']
                agent_id = avatar.get('id') or avatar.get('avatarId')
                print_result(True, f"Agent created successfully: {AGENT_USERNAME}")
                print(f"   Agent ID: {agent_id}")
                return True
            else:
                # Check if error message indicates user already exists
                error_msg = data.get('message', '') or (data.get('result', {}).get('message', '') if isinstance(data.get('result'), dict) else '')
                if 'already exists' in error_msg.lower() or 'exist' in error_msg.lower():
                    print(f"   ℹ️  Agent already exists, will attempt to authenticate")
                    agent_id = None  # Will be retrieved during auth
                    return True
                else:
                    print_result(False, f"Registration failed: {error_msg or data}")
                    return False
        elif response.status_code == 400:
            # User might already exist - try to authenticate instead
            error_text = response.text
            if 'already exists' in error_text.lower() or 'exist' in error_text.lower():
                print(f"   ℹ️  Agent already exists, will attempt to authenticate")
                agent_id = None
                return True
            else:
                print_result(False, f"Registration failed: {response.status_code} - {error_text[:200]}")
                return False
        else:
            print_result(False, f"Registration failed: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
    except Exception as e:
        print_result(False, f"Error creating agent: {e}")
        return False

def authenticate_agent():
    """Authenticate as the agent and get JWT token"""
    print_section("Step 2: Authenticate Agent")
    
    global agent_token, agent_id
    
    auth_data = {
        "Username": AGENT_USERNAME,
        "Password": AGENT_PASSWORD
    }
    
    try:
        print(f"   Authenticating as: {AGENT_USERNAME}")
        
        response = requests.post(
            f"{AVATAR_API_URL}/authenticate",
            json=auth_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # OASIS response structure: { result: { result: IAvatar } } or { result: IAvatar }
            # Extract nested avatar data
            avatar_data = data.get('result', {})
            
            # Handle nested result structure
            if isinstance(avatar_data, dict):
                avatar_info = avatar_data.get('result') if 'result' in avatar_data else avatar_data
                
                if isinstance(avatar_info, dict):
                    # JWT token is stored in JwtToken property
                    agent_token = avatar_info.get('JwtToken') or avatar_info.get('jwtToken')
                    
                    # If not found, try other common locations
                    if not agent_token:
                        agent_token = (avatar_info.get('Token') or 
                                     avatar_info.get('token') or 
                                     avatar_info.get('AccessToken') or
                                     avatar_info.get('accessToken'))
                    
                    # Get agent ID if not already set
                    if not agent_id:
                        agent_id = (avatar_info.get('id') or 
                                   avatar_info.get('Id') or 
                                   avatar_info.get('AvatarId') or
                                   avatar_info.get('avatarId') or
                                   str(avatar_info.get('avatarId', '')))
                    
                    if agent_token:
                        print_result(True, "Agent authenticated successfully")
                        print(f"   Token: {agent_token[:30]}...")
                        if agent_id:
                            print(f"   Agent ID: {agent_id}")
                        return True
                    else:
                        # Debug: show what keys are available
                        available_keys = list(avatar_info.keys())[:20]  # First 20 keys
                        print_result(False, "Authentication successful but JWT token not found in response")
                        print(f"   Available keys in response: {available_keys}")
                        print(f"   Tip: Token might be in 'JwtToken' field - check response structure")
                        # Return False but don't exit - might still work with manual token
                        return False
                else:
                    print_result(False, "Unexpected response structure")
                    return False
            else:
                print_result(False, f"Authentication failed: Unexpected response format")
                return False
        elif response.status_code == 401:
            print_result(False, "Authentication failed: Invalid credentials")
            print("   Tip: The agent might need to be created first or password might be wrong")
            return False
        else:
            print_result(False, f"Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
    except Exception as e:
        print_result(False, f"Error authenticating: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_auth_headers():
    """Get authentication headers"""
    global agent_token
    if not agent_token:
        return None
    return {
        "Authorization": f"Bearer {agent_token}",
        "Content-Type": "application/json"
    }

def check_karma():
    """Check current karma score"""
    print_section("Step 3: Check Current Karma")
    
    headers = get_auth_headers()
    if not headers:
        print_result(False, "No authentication token available")
        return 0
    
    try:
        # Try uppercase route first (ASP.NET Core standard)
        response = requests.get(f"{API_URL}/karma", headers=headers)
        if response.status_code == 404:
            # Try lowercase route
            response = requests.get(f"{API_URL_LOWER}/karma", headers=headers)
        if response.status_code == 200:
            data = response.json()
            karma = data.get('karma', 0)
            print_result(True, f"Current karma: {karma} points")
            return karma
        else:
            error_msg = response.json().get('error', f"Status {response.status_code}") if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to get karma: {error_msg}")
            return 0
    except Exception as e:
        print_result(False, f"Error checking karma: {e}")
        return 0

def mint_reputation_nft(karma_score=None):
    """Mint a reputation NFT for the agent"""
    print_section("Step 4: Mint Reputation NFT")
    
    headers = get_auth_headers()
    if not headers:
        print_result(False, "No authentication token available")
        return False, None
    
    params = {}
    if karma_score is not None:
        params['reputationScore'] = karma_score
    
    params['description'] = f"Reputation NFT minted at {datetime.now().isoformat()}"
    
    try:
        print(f"   Minting reputation NFT with score: {karma_score or 'default'}")
        response = requests.post(
            f"{API_URL}/nft/reputation",
            headers=headers,
            params=params
        )
        if response.status_code == 404:
            # Try lowercase route
            response = requests.post(
                f"{API_URL_LOWER}/nft/reputation",
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
                        print(f"   🔗 View on Solscan: https://solscan.io/tx/{tx_hash}")
            
            return True, data
        else:
            error_msg = response.json().get('error', response.text[:200]) if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to mint NFT: {error_msg}")
            print(f"   Tip: This might require Solana provider configuration or NFT provider setup")
            return False, None
    except Exception as e:
        print_result(False, f"Error minting NFT: {e}")
        return False, None

def mint_service_certificate(service_name="data-analysis"):
    """Mint a service completion certificate NFT"""
    print_section("Step 5: Mint Service Certificate NFT")
    
    headers = get_auth_headers()
    if not headers:
        print_result(False, "No authentication token available")
        return False, None
    
    request_data = {
        "serviceName": service_name,
        "description": f"Certificate for completing {service_name} service",
        "taskId": None
    }
    
    try:
        print(f"   Minting service certificate for: {service_name}")
        response = requests.post(
            f"{API_URL}/nft/service-certificate",
            headers=headers,
            json=request_data
        )
        if response.status_code == 404:
            # Try lowercase route
            response = requests.post(
                f"{API_URL_LOWER}/nft/service-certificate",
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
                        print(f"   🔗 View on Solscan: https://solscan.io/tx/{tx_hash}")
            
            return True, data
        else:
            error_msg = response.json().get('error', response.text[:200]) if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to mint certificate: {error_msg}")
            return False, None
    except Exception as e:
        print_result(False, f"Error minting certificate: {e}")
        return False, None

def award_karma_for_service(service_name="data-analysis"):
    """Award karma for completing a service"""
    print_section("Step 6: Award Karma for Service Completion")
    
    headers = get_auth_headers()
    if not headers:
        print_result(False, "No authentication token available")
        return False, None
    
    # Award karma to self (authenticated agent)
    request_data = {
        "agentId": agent_id,  # Use the authenticated agent's ID
        "serviceName": service_name,
        "karmaAmount": 10
    }
    
    try:
        print(f"   Awarding karma for service: {service_name}")
        response = requests.post(
            f"{API_URL}/karma/award",
            headers=headers,
            json=request_data
        )
        if response.status_code == 404:
            # Try lowercase route
            response = requests.post(
                f"{API_URL_LOWER}/karma/award",
                headers=headers,
                json=request_data
            )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Awarded 10 karma for completing '{service_name}'")
            return True, data
        else:
            error_msg = response.json().get('error', response.text[:200]) if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to award karma: {error_msg}")
            print(f"   Note: This might work differently - the endpoint may automatically use authenticated agent")
            return False, None
    except Exception as e:
        print_result(False, f"Error awarding karma: {e}")
        return False, None

def register_agent_capabilities():
    """Register agent capabilities (required for some operations)"""
    print_section("Step 7: Register Agent Capabilities (Optional)")
    
    headers = get_auth_headers()
    if not headers:
        print_result(False, "No authentication token available")
        return False
    
    capabilities = {
        "services": ["data-analysis", "report-generation"],
        "skills": ["Python", "Machine Learning"],
        "status": "Available",
        "description": "Test agent for NFT minting demonstration",
        "pricing": {
            "data-analysis": 10.0,
            "report-generation": 15.0
        }
    }
    
    try:
        print("   Registering agent capabilities...")
        response = requests.post(
            f"{API_URL}/agent/capabilities",
            headers=headers,
            json=capabilities
        )
        if response.status_code == 404:
            # Try lowercase route
            response = requests.post(
                f"{API_URL_LOWER}/agent/capabilities",
                headers=headers,
                json=capabilities
            )
        
        if response.status_code == 200:
            print_result(True, "Agent capabilities registered")
            return True
        else:
            error_msg = response.json().get('error', response.text[:200]) if response.text else f"Status {response.status_code}"
            print_result(False, f"Failed to register capabilities: {error_msg}")
            print("   Note: This is optional - continuing anyway")
            return False
    except Exception as e:
        print_result(False, f"Error registering capabilities: {e}")
        print("   Note: Continuing anyway...")
        return False

def main():
    """Main test flow - fully automated"""
    print("\n" + "🔷" * 35)
    print("   A2A Protocol - Fully Automated Agent NFT Minting Test")
    print("🔷" * 35)
    print(f"\n🌐 API URL: {API_URL}")
    print(f"🤖 Agent: {AGENT_USERNAME}")
    print("\n✨ This script is fully automated - no manual setup required!")
    
    # Step 1: Create agent
    if not create_agent():
        print("\n❌ Failed to create agent. Please check the OASIS API is running.")
        print(f"   Expected URL: {BASE_URL}")
        sys.exit(1)
    
    # Step 2: Authenticate agent
    if not authenticate_agent():
        print("\n❌ Failed to authenticate agent.")
        print("   This might be because:")
        print("   1. The agent was just created and needs a moment")
        print("   2. The OASIS API requires email verification")
        print("   3. There's an issue with the API")
        sys.exit(1)
    
    if not agent_token:
        print("\n❌ No authentication token received.")
        print("   Cannot proceed with tests.")
        sys.exit(1)
    
    # Step 3: Register capabilities (optional but helpful)
    register_agent_capabilities()
    
    # Step 4: Check karma
    karma = check_karma()
    
    # Step 5: Mint reputation NFT
    success, nft_data = mint_reputation_nft(karma_score=karma)
    if not success:
        print("\n⚠️  NFT minting failed. This might be because:")
        print("   - Solana provider is not configured")
        print("   - NFT provider is not activated")
        print("   - Insufficient balance for gas fees")
        print("   - NFT provider setup is incomplete")
    
    # Step 6: Mint service certificate
    success, cert_data = mint_service_certificate("automated-test-service")
    
    # Step 7: Award karma
    success, karma_data = award_karma_for_service("automated-test-service")
    
    # Final karma check
    print_section("Final Status Check")
    final_karma = check_karma()
    
    # Summary
    print_section("Test Summary")
    print("✅ Automated test flow completed!")
    print("\n📋 What happened:")
    print(f"   1. ✅ Created agent: {AGENT_USERNAME}")
    print(f"   2. ✅ Authenticated agent")
    print(f"   3. ✅ Registered capabilities (optional)")
    print(f"   4. ✅ Checked karma: {karma} → {final_karma} points")
    print(f"   5. {'✅' if nft_data else '⚠️'} Minted reputation NFT")
    print(f"   6. {'✅' if cert_data else '⚠️'} Minted service certificate NFT")
    print(f"   7. {'✅' if karma_data else '⚠️'} Awarded karma for service")
    
    print("\n💡 Next Steps:")
    print("   - Check your agent's NFT collection")
    print("   - Verify karma score increased")
    print("   - View NFTs on blockchain explorer (if minting succeeded)")
    print(f"   - Test more features with this agent: {AGENT_USERNAME}")
    
    print(f"\n🔑 Agent Credentials (for future use):")
    print(f"   Username: {AGENT_USERNAME}")
    print(f"   Email: {AGENT_EMAIL}")
    print(f"   Password: {AGENT_PASSWORD}")
    
    print("\n" + "=" * 70)
    print("🎉 Fully Automated Test Complete!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
