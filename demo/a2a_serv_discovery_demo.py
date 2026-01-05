#!/usr/bin/env python3
"""
A2A-SERV Discovery Demo Script

This script demonstrates A2A Protocol integration with SERV infrastructure:
1. Register agent capabilities via A2A
2. Register agent as SERV service
3. Discover agents via SERV infrastructure
4. Filter agents by service type

Requirements:
    pip install requests

Usage:
    python a2a_serv_discovery_demo.py
"""

import requests
import json
import time
import sys
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

class SERVDiscoveryDemo:
    """Demo client for A2A-SERV discovery"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.agent_id: Optional[str] = None
        
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
    
    def register_capabilities(self, services: List[str], skills: List[str], 
                             description: str) -> bool:
        """Register agent capabilities"""
        print_step("Registering agent capabilities...")
        url = f"{API_URL}/agent/capabilities"
        payload = {
            "services": services,
            "skills": skills,
            "status": "Available",
            "description": description,
            "pricing": {service: 0.1 for service in services}
        }
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                print_success("Capabilities registered successfully")
                return True
            else:
                print_error(f"Failed to register capabilities: {response.status_code}")
                print(response.text)
        except Exception as e:
            print_error(f"Error registering capabilities: {e}")
        return False
    
    def register_as_serv_service(self) -> bool:
        """Register agent as SERV service"""
        print_step("Registering agent as SERV service...")
        url = f"{API_URL}/agent/register-service"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print_success("Agent registered as SERV service successfully")
                return True
            else:
                print_error(f"Failed to register as SERV service: {response.status_code}")
                print(response.text)
        except Exception as e:
            print_error(f"Error registering as SERV service: {e}")
        return False
    
    def discover_all_agents_via_serv(self) -> List[Dict[str, Any]]:
        """Discover all agents via SERV infrastructure"""
        print_step("Discovering all agents via SERV...")
        url = f"{API_URL}/agents/discover-serv"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                agents = response.json()
                print_success(f"Found {len(agents)} agents via SERV")
                return agents
            else:
                print_error(f"Failed to discover agents: {response.status_code}")
        except Exception as e:
            print_error(f"Error discovering agents: {e}")
        return []
    
    def discover_agents_by_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Discover agents by specific service"""
        print_step(f"Discovering agents for service: {service_name}...")
        url = f"{API_URL}/agents/discover-serv"
        params = {"service": service_name}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                agents = response.json()
                print_success(f"Found {len(agents)} agents for service '{service_name}'")
                return agents
            else:
                print_error(f"Failed to discover agents by service: {response.status_code}")
        except Exception as e:
            print_error(f"Error discovering agents by service: {e}")
        return []
    
    def display_agent_info(self, agent: Dict[str, Any]):
        """Display agent information"""
        agent_id = agent.get("agentId", "Unknown")
        name = agent.get("name", "Unknown")
        capabilities = agent.get("capabilities", {})
        services = capabilities.get("services", [])
        skills = capabilities.get("skills", [])
        connection = agent.get("connection", {})
        endpoint = connection.get("endpoint", "Unknown")
        
        print(f"\n  {Colors.YELLOW}Agent:{Colors.NC} {name}")
        print(f"  {Colors.YELLOW}ID:{Colors.NC} {agent_id}")
        print(f"  {Colors.YELLOW}Services:{Colors.NC} {', '.join(services) if services else 'None'}")
        print(f"  {Colors.YELLOW}Skills:{Colors.NC} {', '.join(skills) if skills else 'None'}")
        print(f"  {Colors.YELLOW}Endpoint:{Colors.NC} {endpoint}")

def main():
    """Main demo function"""
    print_header("A2A-SERV Discovery Demo")
    
    # Get credentials from environment or use defaults
    import os
    username = os.getenv("USERNAME", "test_agent")
    password = os.getenv("PASSWORD", "test_password")
    
    print_info(f"Using API: {API_BASE_URL}")
    print_info(f"Username: {username}")
    
    # Create demo client
    demo = SERVDiscoveryDemo()
    
    # Step 1: Authenticate
    print_header("Step 1: Authentication")
    if not demo.authenticate(username, password):
        print_error("Authentication failed. Please check your credentials.")
        sys.exit(1)
    
    # Step 2: Register capabilities
    print_header("Step 2: Register Agent Capabilities")
    services = ["data-analysis", "report-generation", "ml-prediction"]
    skills = ["Python", "Machine Learning", "Data Science", "Statistics"]
    description = "Data analysis and machine learning agent for SERV discovery demo"
    
    if not demo.register_capabilities(services, skills, description):
        print_error("Failed to register capabilities")
        sys.exit(1)
    
    # Wait a moment for registration to complete
    time.sleep(1)
    
    # Step 3: Register as SERV service
    print_header("Step 3: Register as SERV Service")
    if not demo.register_as_serv_service():
        print_error("Failed to register as SERV service")
        sys.exit(1)
    
    # Wait a moment for SERV registration
    time.sleep(2)
    
    # Step 4: Discover all agents
    print_header("Step 4: Discover All Agents via SERV")
    all_agents = demo.discover_all_agents_via_serv()
    
    if all_agents:
        print(f"\n{Colors.GREEN}Discovered Agents:{Colors.NC}")
        for agent in all_agents[:5]:  # Show first 5
            demo.display_agent_info(agent)
        if len(all_agents) > 5:
            print_info(f"... and {len(all_agents) - 5} more agents")
    
    # Step 5: Discover agents by service
    print_header("Step 5: Discover Agents by Service")
    
    for service in services:
        agents = demo.discover_agents_by_service(service)
        if agents:
            print(f"\n{Colors.GREEN}Agents providing '{service}':{Colors.NC}")
            for agent in agents:
                demo.display_agent_info(agent)
        else:
            print_info(f"No agents found for service '{service}'")
    
    # Summary
    print_header("Demo Summary")
    print_success(f"Agent registered and discoverable via SERV infrastructure")
    print_success(f"Total agents discovered: {len(all_agents)}")
    print_info("Agents can now be discovered via SERV service registry")
    print_info("This enables unified service discovery across A2A and SERV platforms")
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}Demo Complete!{Colors.NC}")
    print(f"{Colors.GREEN}{'='*60}{Colors.NC}\n")

if __name__ == "__main__":
    main()

