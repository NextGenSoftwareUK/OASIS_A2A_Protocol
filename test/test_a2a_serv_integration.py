#!/usr/bin/env python3
"""
A2A-SERV Integration Test Script
Tests A2A Protocol integration with SERV infrastructure
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

def test_register_agent_as_service(jwt_token: str, agent_id: str) -> Dict[str, Any]:
    """Test registering an A2A agent as a SERV service"""
    print_test("Register Agent as SERV Service")
    
    # First, register agent capabilities
    capabilities_payload = {
        "services": ["data-analysis", "report-generation"],
        "skills": ["Python", "Machine Learning", "Data Analysis"],
        "status": "Available",
        "description": "Test agent for SERV integration",
        "pricing": {
            "data-analysis": 0.1,
            "report-generation": 0.05
        }
    }
    
    # Register capabilities
    cap_response = requests.post(
        f"{API_URL}/agents/{agent_id}/capabilities",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json=capabilities_payload
    )
    
    if cap_response.status_code not in [200, 201]:
        print(f"{Colors.RED}Failed to register capabilities{Colors.NC}")
        print_response(cap_response)
        return {"success": False}
    
    # Now register as SERV service
    response = requests.post(
        f"{API_URL}/agent/register-service",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json={
            "agentId": agent_id
        }
    )
    
    print_response(response)
    
    if response.status_code in [200, 201]:
        print(f"{Colors.GREEN}✓ Agent registered as SERV service{Colors.NC}")
        return {"success": True, "data": response.json()}
    else:
        print(f"{Colors.RED}✗ Failed to register agent as SERV service{Colors.NC}")
        return {"success": False}

def test_discover_agents_via_serv(service_name: Optional[str] = None) -> Dict[str, Any]:
    """Test discovering agents via SERV infrastructure"""
    print_test(f"Discover Agents via SERV" + (f" (service: {service_name})" if service_name else ""))
    
    url = f"{API_URL}/agents/discover-serv"
    if service_name:
        url += f"?service={service_name}"
    
    response = requests.get(url)
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        agents = data.get("result", [])
        print(f"{Colors.GREEN}✓ Found {len(agents)} agents via SERV{Colors.NC}")
        return {"success": True, "agents": agents, "count": len(agents)}
    else:
        print(f"{Colors.RED}✗ Failed to discover agents via SERV{Colors.NC}")
        return {"success": False}

def test_discover_agents_by_service(service_name: str) -> Dict[str, Any]:
    """Test discovering agents by specific service"""
    print_test(f"Discover Agents by Service: {service_name}")
    
    response = requests.get(
        f"{API_URL}/agents/discover-serv",
        params={"service": service_name}
    )
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        agents = data.get("result", [])
        print(f"{Colors.GREEN}✓ Found {len(agents)} agents for service '{service_name}'{Colors.NC}")
        
        # Verify agents have the requested service
        for agent in agents:
            capabilities = agent.get("capabilities", {})
            services = capabilities.get("services", [])
            if service_name.lower() in [s.lower() for s in services]:
                print(f"  - Agent {agent.get('agentId')} has service '{service_name}'")
        
        return {"success": True, "agents": agents, "count": len(agents)}
    else:
        print(f"{Colors.RED}✗ Failed to discover agents by service{Colors.NC}")
        return {"success": False}

def test_auto_registration(jwt_token: str, agent_id: str) -> Dict[str, Any]:
    """Test that agent auto-registers with SERV when capabilities are registered"""
    print_test("Auto-Registration with SERV")
    
    capabilities_payload = {
        "services": ["auto-test-service"],
        "skills": ["Testing", "Integration"],
        "status": "Available",
        "description": "Auto-registration test agent"
    }
    
    response = requests.post(
        f"{API_URL}/agents/{agent_id}/capabilities",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        },
        json=capabilities_payload
    )
    
    print_response(response)
    
    if response.status_code in [200, 201]:
        print(f"{Colors.YELLOW}Waiting 2 seconds for auto-registration...{Colors.NC}")
        import time
        time.sleep(2)
        
        # Check if agent is discoverable via SERV
        serv_response = requests.get(
            f"{API_URL}/agents/discover-serv",
            params={"service": "auto-test-service"}
        )
        
        if serv_response.status_code == 200:
            data = serv_response.json()
            agents = data.get("result", [])
            found = any(agent.get("agentId") == agent_id for agent in agents)
            
            if found:
                print(f"{Colors.GREEN}✓ Agent auto-registered with SERV successfully{Colors.NC}")
                return {"success": True, "auto_registered": True}
            else:
                print(f"{Colors.YELLOW}⚠ Agent capabilities registered but not yet discoverable via SERV{Colors.NC}")
                return {"success": True, "auto_registered": False}
        else:
            print(f"{Colors.YELLOW}⚠ Could not verify auto-registration{Colors.NC}")
            return {"success": True, "auto_registered": None}
    else:
        print(f"{Colors.RED}✗ Failed to register capabilities{Colors.NC}")
        return {"success": False}

def main():
    """Run all SERV integration tests"""
    print(f"{Colors.GREEN}=== A2A-SERV Integration Tests ==={Colors.NC}")
    
    # Get JWT token from environment
    jwt_token = os.getenv("JWT_TOKEN")
    if not jwt_token:
        print(f"{Colors.RED}Error: JWT_TOKEN environment variable is required{Colors.NC}")
        print("Usage: JWT_TOKEN='your_token_here' python test_a2a_serv_integration.py")
        return
    
    # Get agent ID
    agent_id = os.getenv("AGENT_ID")
    if not agent_id:
        print(f"{Colors.YELLOW}Warning: AGENT_ID not provided. Some tests will be skipped.{Colors.NC}")
    
    # Run tests
    if agent_id:
        test_register_agent_as_service(jwt_token, agent_id)
        test_auto_registration(jwt_token, agent_id)
    
    test_discover_agents_via_serv()
    test_discover_agents_by_service("data-analysis")
    test_discover_agents_by_service("report-generation")
    
    print(f"\n{Colors.GREEN}=== Tests Complete ==={Colors.NC}")

if __name__ == "__main__":
    main()

