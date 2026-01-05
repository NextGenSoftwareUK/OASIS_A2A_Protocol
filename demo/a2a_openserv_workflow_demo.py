#!/usr/bin/env python3
"""
A2A-OpenSERV Workflow Demo Script

This script demonstrates A2A Protocol integration with OpenSERV agents:
1. Register an OpenSERV agent as an A2A agent
2. Execute AI workflows via OpenSERV through A2A Protocol
3. Route workflow requests and responses via A2A messaging

Requirements:
    pip install requests

Usage:
    python a2a_openserv_workflow_demo.py
"""

import requests
import json
import time
import sys
import uuid
from typing import Optional, Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:5003"
API_URL = f"{API_BASE_URL}/api/a2a"

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.NC}")
    print(f"{Colors.CYAN}{text}{Colors.NC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")

def print_step(text: str):
    """Print step description"""
    print(f"{Colors.BLUE}→ {text}{Colors.NC}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.NC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

class OpenSERVWorkflowDemo:
    """Demo client for A2A-OpenSERV workflow execution"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.agent_id: Optional[str] = None
        self.openserv_agent_id: Optional[str] = None
        
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        print_step(f"Authenticating as {username}...")
        url = f"{self.base_url}/api/avatar/authenticate"
        payload = {"username": username, "password": password}
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                self.token = result.get("token")
                self.agent_id = result.get("avatar", {}).get("id")
                if self.token:
                    print_success(f"Authenticated successfully (Agent ID: {self.agent_id})")
                    return True
        except Exception as e:
            print_error(f"Authentication failed: {e}")
        return False
    
    def register_openserv_agent(self, open_serv_agent_id: str, 
                                open_serv_endpoint: str,
                                capabilities: List[str],
                                api_key: Optional[str] = None) -> bool:
        """Register an OpenSERV agent as an A2A agent"""
        print_step(f"Registering OpenSERV agent: {open_serv_agent_id}...")
        url = f"{API_URL}/openserv/register"
        payload = {
            "openServAgentId": open_serv_agent_id,
            "openServEndpoint": open_serv_endpoint,
            "capabilities": capabilities,
            "apiKey": api_key
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print_success(f"OpenSERV agent registered successfully")
                self.openserv_agent_id = open_serv_agent_id
                print_info(f"OpenSERV Agent ID: {open_serv_agent_id}")
                print_info(f"Endpoint: {open_serv_endpoint}")
                return True
            else:
                print_error(f"Failed to register OpenSERV agent: {response.status_code}")
                print(response.text)
        except Exception as e:
            print_error(f"Error registering OpenSERV agent: {e}")
        return False
    
    def execute_workflow(self, to_agent_id: str, workflow_request: str,
                        workflow_parameters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute an AI workflow via OpenSERV"""
        print_step(f"Executing workflow via OpenSERV agent: {to_agent_id}...")
        url = f"{API_URL}/workflow/execute"
        payload = {
            "toAgentId": to_agent_id,
            "workflowRequest": workflow_request,
            "workflowParameters": workflow_parameters or {}
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            print_info(f"Workflow Request: {workflow_request[:100]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                print_success("Workflow executed successfully")
                return data
            else:
                print_error(f"Failed to execute workflow: {response.status_code}")
                print(response.text)
        except Exception as e:
            print_error(f"Error executing workflow: {e}")
        return None
    
    def get_agent_card(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent card for an agent"""
        print_step(f"Retrieving agent card: {agent_id}...")
        url = f"{API_URL}/agent-card/{agent_id}"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                agent_card = response.json()
                print_success("Agent card retrieved successfully")
                return agent_card
            else:
                print_error(f"Failed to get agent card: {response.status_code}")
        except Exception as e:
            print_error(f"Error getting agent card: {e}")
        return None

def main():
    """Main demo function"""
    print_header("A2A-OpenSERV Workflow Demo")
    
    # Get configuration from environment
    import os
    username = os.getenv("USERNAME", "test_agent")
    password = os.getenv("PASSWORD", "test_password")
    openserv_endpoint = os.getenv("OPENSERV_ENDPOINT", "https://api.openserv.ai/agents/demo")
    openserv_api_key = os.getenv("OPENSERV_API_KEY")
    openserv_agent_id = os.getenv("OPENSERV_AGENT_ID", f"demo-agent-{uuid.uuid4().hex[:8]}")
    to_agent_id = os.getenv("TO_AGENT_ID")  # Optional: use existing agent
    
    print_info(f"Using API: {API_BASE_URL}")
    print_info(f"Username: {username}")
    if openserv_endpoint:
        print_info(f"OpenSERV Endpoint: {openserv_endpoint}")
    
    # Create demo client
    demo = OpenSERVWorkflowDemo()
    
    # Step 1: Authenticate
    print_header("Step 1: Authentication")
    if not demo.authenticate(username, password):
        print_error("Authentication failed. Please check your credentials.")
        sys.exit(1)
    
    # Step 2: Register OpenSERV agent (if not using existing)
    if not to_agent_id:
        print_header("Step 2: Register OpenSERV Agent")
        capabilities = ["data-analysis", "nlp", "text-generation", "summarization"]
        if not demo.register_openserv_agent(
            openserv_agent_id,
            openserv_endpoint,
            capabilities,
            openserv_api_key
        ):
            print_warning("Failed to register OpenSERV agent. Continuing with demo...")
        else:
            time.sleep(1)  # Wait for registration
    
    # Step 3: Get agent information
    if to_agent_id or demo.openserv_agent_id:
        print_header("Step 3: Get Agent Information")
        agent_id = to_agent_id or demo.agent_id  # Use provided ID or demo agent ID
        agent_card = demo.get_agent_card(agent_id)
        if agent_card:
            metadata = agent_card.get("metadata", {})
            if metadata.get("openserv_agent_id"):
                print_info(f"OpenSERV Agent ID: {metadata.get('openserv_agent_id')}")
                print_info(f"OpenSERV Endpoint: {metadata.get('openserv_endpoint')}")
    
    # Step 4: Execute workflow
    print_header("Step 4: Execute AI Workflow")
    
    workflow_request = "Analyze the following text and provide a summary with key points: " \
                      "The OASIS Platform is a comprehensive blockchain and AI infrastructure " \
                      "that enables the creation of decentralized applications and autonomous agents."
    
    workflow_parameters = {
        "analysis_type": "summarization",
        "max_length": 200,
        "include_keywords": True
    }
    
    # Use provided agent ID or demo agent ID
    target_agent_id = to_agent_id or demo.agent_id
    
    if target_agent_id:
        workflow_result = demo.execute_workflow(
            target_agent_id,
            workflow_request,
            workflow_parameters
        )
        
        if workflow_result:
            print("\n" + "="*60)
            print("Workflow Result:")
            print("="*60)
            result_data = workflow_result.get("result", workflow_result)
            if isinstance(result_data, str):
                print(result_data)
            else:
                print(json.dumps(result_data, indent=2))
            print("="*60 + "\n")
    else:
        print_warning("No target agent ID available. Skipping workflow execution.")
        print_info("Set TO_AGENT_ID environment variable to test workflow execution")
    
    # Summary
    print_header("Demo Summary")
    print_success("A2A-OpenSERV integration demonstrated")
    print_info("OpenSERV agents can be registered as A2A agents")
    print_info("Workflows can be executed via A2A Protocol and routed to OpenSERV")
    print_info("Responses are sent back through A2A messaging system")
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}Demo Complete!{Colors.NC}")
    print(f"{Colors.GREEN}{'='*60}{Colors.NC}\n")

if __name__ == "__main__":
    main()

