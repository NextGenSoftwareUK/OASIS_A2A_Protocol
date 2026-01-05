#!/usr/bin/env python3
"""
A2A Protocol Endpoint Test Script (Python)
Tests all A2A endpoints with proper authentication
"""

import os
import json
import requests
from typing import Optional, Dict, Any

BASE_URL = os.getenv("BASE_URL", "http://localhost:5003")
API_URL = f"{BASE_URL}/api/a2a"

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

def print_test(name: str):
    """Print test name with color"""
    print(f"\n{Colors.GREEN}Test: {name}{Colors.NC}")

def print_response(response: requests.Response):
    """Print formatted response"""
    try:
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_ping(jwt_token: str) -> Dict[str, Any]:
    """Test ping (health check)"""
    print_test("Ping (Health Check)")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "ping",
        "id": "test-ping-1"
    }
    
    response = requests.post(
        f"{API_URL}/jsonrpc",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_get_all_agents() -> Dict[str, Any]:
    """Test get all agents"""
    print_test("Get All Agents")
    
    response = requests.get(f"{API_URL}/agents")
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_get_agent_card(agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Test get agent card"""
    if not agent_id:
        print(f"{Colors.YELLOW}Skipping: AGENT_ID not provided{Colors.NC}")
        return None
    
    print_test(f"Get Agent Card ({agent_id})")
    
    response = requests.get(f"{API_URL}/agent-card/{agent_id}")
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_get_my_agent_card(jwt_token: str) -> Dict[str, Any]:
    """Test get my agent card"""
    print_test("Get My Agent Card")
    
    response = requests.get(
        f"{API_URL}/agent-card",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_register_capabilities(jwt_token: str) -> Dict[str, Any]:
    """Test register capabilities"""
    print_test("Register Capabilities")
    
    payload = {
        "services": ["data-analysis", "report-generation"],
        "pricing": {
            "data-analysis": 0.1,
            "report-generation": 0.05
        },
        "skills": ["Python", "Machine Learning", "Data Science"],
        "status": "Available",
        "max_concurrent_tasks": 3,
        "description": "Data analysis and reporting agent"
    }
    
    response = requests.post(
        f"{API_URL}/agent/capabilities",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_capability_query(jwt_token: str, target_agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Test capability query"""
    if not target_agent_id:
        print(f"{Colors.YELLOW}Skipping: TARGET_AGENT_ID not provided{Colors.NC}")
        return None
    
    print_test(f"Capability Query ({target_agent_id})")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "capability_query",
        "params": {
            "to_agent_id": target_agent_id
        },
        "id": "test-capability-query-1"
    }
    
    response = requests.post(
        f"{API_URL}/jsonrpc",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_service_request(jwt_token: str, target_agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Test service request"""
    if not target_agent_id:
        print(f"{Colors.YELLOW}Skipping: TARGET_AGENT_ID not provided{Colors.NC}")
        return None
    
    print_test(f"Service Request ({target_agent_id})")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "service_request",
        "params": {
            "to_agent_id": target_agent_id,
            "service": "data-analysis",
            "parameters": {
                "dataset": "sales_data.csv",
                "analysis_type": "trend"
            }
        },
        "id": "test-service-request-1"
    }
    
    response = requests.post(
        f"{API_URL}/jsonrpc",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_get_pending_messages(jwt_token: str) -> Dict[str, Any]:
    """Test get pending messages"""
    print_test("Get Pending Messages")
    
    response = requests.get(
        f"{API_URL}/messages",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_find_agents_by_service(service_name: str = "data-analysis") -> Dict[str, Any]:
    """Test find agents by service"""
    print_test(f"Find Agents by Service ({service_name})")
    
    response = requests.get(f"{API_URL}/agents/by-service/{service_name}")
    print_response(response)
    return response.json() if response.status_code == 200 else None

def main():
    """Main test function"""
    print(f"{Colors.YELLOW}=== A2A Protocol Endpoint Tests ==={Colors.NC}")
    
    # Get JWT token from environment
    jwt_token = os.getenv("JWT_TOKEN")
    if not jwt_token:
        print(f"{Colors.RED}Error: JWT_TOKEN environment variable is required{Colors.NC}")
        print("Usage: JWT_TOKEN='your_token_here' python test_a2a_endpoints.py")
        return
    
    # Optional parameters
    agent_id = os.getenv("AGENT_ID")
    target_agent_id = os.getenv("TARGET_AGENT_ID")
    
    # Run tests
    test_ping(jwt_token)
    test_get_all_agents()
    test_get_agent_card(agent_id)
    test_get_my_agent_card(jwt_token)
    test_register_capabilities(jwt_token)
    test_capability_query(jwt_token, target_agent_id)
    test_service_request(jwt_token, target_agent_id)
    test_get_pending_messages(jwt_token)
    test_find_agents_by_service("data-analysis")
    
    print(f"\n{Colors.GREEN}=== Tests Complete ==={Colors.NC}")

if __name__ == "__main__":
    main()

