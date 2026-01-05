#!/usr/bin/env python3
"""
A2A-OpenSERV Integration Test Script
Tests A2A Protocol integration with OpenSERV agents
"""

import os
import json
import requests
import uuid
from typing import Optional, Dict, Any

BASE_URL = os.getenv("BASE_URL", "http://localhost:5003")
API_URL = f"{BASE_URL}/api/a2a"

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_test(name: str):
    """Print test name with color"""
    print(f"\n{Colors.BLUE}Test: {name}{Colors.NC}")

def print_response(response: requests.Response):
    """Print formatted response"""
    try:
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_register_openserv_agent(
    open_serv_agent_id: Optional[str] = None,
    open_serv_endpoint: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Test registering an OpenSERV agent as an A2A agent"""
    print_test("Register OpenSERV Agent")
    
    if not open_serv_agent_id:
        open_serv_agent_id = f"test-agent-{uuid.uuid4().hex[:8]}"
    
    if not open_serv_endpoint:
        open_serv_endpoint = os.getenv("OPENSERV_ENDPOINT", "https://api.openserv.ai/agents/test")
    
    payload = {
        "openServAgentId": open_serv_agent_id,
        "openServEndpoint": open_serv_endpoint,
        "capabilities": ["data-analysis", "nlp", "image-generation"],
        "apiKey": api_key
    }
    
    response = requests.post(
        f"{API_URL}/openserv/register",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    print_response(response)
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"{Colors.GREEN}✓ OpenSERV agent registered successfully{Colors.NC}")
        return {"success": True, "data": data, "agent_id": open_serv_agent_id}
    else:
        print(f"{Colors.RED}✗ Failed to register OpenSERV agent{Colors.NC}")
        return {"success": False}

def test_execute_workflow(
    jwt_token: str,
    to_agent_id: Optional[str] = None,
    workflow_request: Optional[str] = None
) -> Dict[str, Any]:
    """Test executing an AI workflow via OpenSERV"""
    print_test("Execute AI Workflow via OpenSERV")
    
    if not to_agent_id:
        print(f"{Colors.YELLOW}Warning: TO_AGENT_ID not provided, skipping workflow test{Colors.NC}")
        return {"success": False, "skipped": True}
    
    if not workflow_request:
        workflow_request = "Analyze the sales data and generate a summary report with key insights"
    
    payload = {
        "toAgentId": to_agent_id,
        "workflowRequest": workflow_request,
        "workflowParameters": {
            "data_source": "sales_data.csv",
            "report_format": "markdown",
            "include_charts": True
        }
    }
    
    response = requests.post(
        f"{API_URL}/workflow/execute",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✓ Workflow executed successfully{Colors.NC}")
        return {"success": True, "data": data}
    else:
        print(f"{Colors.RED}✗ Failed to execute workflow{Colors.NC}")
        return {"success": False}

def test_discover_openserv_agents() -> Dict[str, Any]:
    """Test discovering OpenSERV agents via A2A"""
    print_test("Discover OpenSERV Agents via A2A")
    
    response = requests.get(f"{API_URL}/agents")
    
    print_response(response)
    
    if response.status_code == 200:
        agents = response.json()
        openserv_agents = [
            agent for agent in agents
            if agent.get("metadata", {}).get("openserv_agent_id") is not None
        ]
        print(f"{Colors.GREEN}✓ Found {len(openserv_agents)} OpenSERV agents{Colors.NC}")
        return {"success": True, "agents": openserv_agents, "count": len(openserv_agents)}
    else:
        print(f"{Colors.RED}✗ Failed to discover OpenSERV agents{Colors.NC}")
        return {"success": False}

def test_openserv_agent_capabilities(agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Test retrieving OpenSERV agent capabilities"""
    print_test(f"Get OpenSERV Agent Capabilities ({agent_id})")
    
    if not agent_id:
        print(f"{Colors.YELLOW}Warning: AGENT_ID not provided{Colors.NC}")
        return {"success": False, "skipped": True}
    
    response = requests.get(f"{API_URL}/agent-card/{agent_id}")
    
    print_response(response)
    
    if response.status_code == 200:
        agent_card = response.json()
        metadata = agent_card.get("metadata", {})
        if metadata.get("openserv_agent_id"):
            print(f"{Colors.GREEN}✓ OpenSERV agent capabilities retrieved{Colors.NC}")
            print(f"  OpenSERV Agent ID: {metadata.get('openserv_agent_id')}")
            print(f"  Endpoint: {metadata.get('openserv_endpoint')}")
            return {"success": True, "agent_card": agent_card}
        else:
            print(f"{Colors.YELLOW}Agent is not an OpenSERV agent{Colors.NC}")
            return {"success": False, "not_openserv": True}
    else:
        print(f"{Colors.RED}✗ Failed to get agent capabilities{Colors.NC}")
        return {"success": False}

def test_error_scenarios():
    """Test error scenarios for OpenSERV integration"""
    print_test("Error Scenarios")
    
    # Test 1: Register without required fields
    print(f"\n{Colors.YELLOW}Test 1: Register without required fields{Colors.NC}")
    payload = {
        "openServAgentId": "",
        "openServEndpoint": ""
    }
    response = requests.post(
        f"{API_URL}/openserv/register",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    print(f"Status: {response.status_code} (Expected: 400)")
    
    # Test 2: Execute workflow without authentication
    print(f"\n{Colors.YELLOW}Test 2: Execute workflow without authentication{Colors.NC}")
    payload = {
        "toAgentId": str(uuid.uuid4()),
        "workflowRequest": "Test workflow"
    }
    response = requests.post(
        f"{API_URL}/workflow/execute",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    print(f"Status: {response.status_code} (Expected: 401)")
    
    # Test 3: Execute workflow with invalid agent ID
    print(f"\n{Colors.YELLOW}Test 3: Execute workflow with invalid agent ID{Colors.NC}")
    jwt_token = os.getenv("JWT_TOKEN")
    if jwt_token:
        payload = {
            "toAgentId": "00000000-0000-0000-0000-000000000000",
            "workflowRequest": "Test workflow"
        }
        response = requests.post(
            f"{API_URL}/workflow/execute",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        print(f"Status: {response.status_code} (Expected: 400 or 404)")
    else:
        print(f"{Colors.YELLOW}Skipped: JWT_TOKEN not provided{Colors.NC}")

def main():
    """Main test function"""
    print(f"{Colors.YELLOW}=== A2A-OpenSERV Integration Tests ==={Colors.NC}")
    
    # Get environment variables
    jwt_token = os.getenv("JWT_TOKEN")
    open_serv_agent_id = os.getenv("OPENSERV_AGENT_ID")
    open_serv_endpoint = os.getenv("OPENSERV_ENDPOINT")
    open_serv_api_key = os.getenv("OPENSERV_API_KEY")
    to_agent_id = os.getenv("TO_AGENT_ID")
    workflow_request = os.getenv("WORKFLOW_REQUEST")
    
    results = []
    
    # Test 1: Register OpenSERV agent
    register_result = test_register_openserv_agent(
        open_serv_agent_id,
        open_serv_endpoint,
        open_serv_api_key
    )
    results.append(("Register OpenSERV Agent", register_result))
    
    # Extract agent ID from registration if successful
    registered_agent_id = None
    if register_result.get("success") and register_result.get("data"):
        # Note: Agent ID would be in the response, but we'll use the openServAgentId for now
        registered_agent_id = register_result.get("agent_id")
    
    # Test 2: Discover OpenSERV agents
    discover_result = test_discover_openserv_agents()
    results.append(("Discover OpenSERV Agents", discover_result))
    
    # Test 3: Get OpenSERV agent capabilities
    if registered_agent_id or to_agent_id:
        agent_id = registered_agent_id or to_agent_id
        capabilities_result = test_openserv_agent_capabilities(agent_id)
        results.append(("Get OpenSERV Agent Capabilities", capabilities_result))
    
    # Test 4: Execute workflow (requires JWT token and agent ID)
    if jwt_token and (to_agent_id or registered_agent_id):
        workflow_result = test_execute_workflow(
            jwt_token,
            to_agent_id or registered_agent_id,
            workflow_request
        )
        results.append(("Execute Workflow", workflow_result))
    else:
        print(f"\n{Colors.YELLOW}Skipping workflow test: JWT_TOKEN and TO_AGENT_ID required{Colors.NC}")
    
    # Test 5: Error scenarios
    test_error_scenarios()
    
    # Summary
    print(f"\n{Colors.YELLOW}=== Test Summary ==={Colors.NC}")
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if result.get("success") else f"{Colors.RED}✗ FAIL{Colors.NC}"
        skipped = " (SKIPPED)" if result.get("skipped") else ""
        print(f"{test_name}: {status}{skipped}")
    
    print(f"\n{Colors.GREEN}=== Tests Complete ==={Colors.NC}")

if __name__ == "__main__":
    main()

