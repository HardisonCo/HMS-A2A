#!/usr/bin/env python3
"""
CDF Research Connector

A specialized connector for the Collaborative Decision Framework (CDF)
that provides integration between HMS-GOV and HMS-CDF systems.
"""

import os
import sys
import json
import re
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agency_issue_finder.base_connector import AgencyResearchConnector

class CDFException(Exception):
    """Custom exception for CDF connector errors."""
    pass

class CDFResearchConnector(AgencyResearchConnector):
    """
    CDF-specific research connector implementation.
    Provides bidirectional integration between HMS-GOV and HMS-CDF.
    """
    
    def __init__(self, base_path: str) -> None:
        """
        Initialize the CDF research connector.

        Args:
            base_path: Base path to CDF data
        """
        super().__init__("CDF", base_path)

        # Load CDF configuration
        self.config = self._load_cdf_config()

        # Load data with potential fallback to config
        self.decision_frameworks = self._load_decision_frameworks()
        self.endpoints = self._load_endpoints()
        self.integration_status = self._load_integration_status()

    def _load_cdf_config(self) -> Dict[str, Any]:
        """Load CDF connector configuration."""
        config_file = os.path.join(self.agency_dir, "cdf", "cdf_config.json")

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Process environment variables in config
                    config = self._process_env_variables(config)
                    return config
            except json.JSONDecodeError as e:
                raise CDFException(f"Invalid JSON in CDF config file: {e}")

        # Return default config if file not found
        return {
            "connector": {
                "version": "1.0.0",
                "name": "CDF Connector",
                "description": "Connects HMS-GOV to HMS-CDF via agency interface"
            },
            "api": {
                "base_url": "https://api.cdf.gov",
                "version": "v1",
                "timeout": 30
            },
            "domains": {
                "dnc": {"url": "https://dnc.dev"},
                "rnc": {"url": "https://rnc.dev"}
            },
            "transformation": {
                "protocol_format_version": "1.0",
                "supported_formats": ["hms-api", "cdf"]
            }
        }

    def _process_env_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process environment variables in configuration."""
        import re
        import os

        # Convert config to string for easier processing
        config_str = json.dumps(config)

        # Find all environment variable placeholders
        pattern = r'\{\{ENV:([A-Za-z0-9_]+)\}\}'
        matches = re.findall(pattern, config_str)

        # Replace placeholders with actual values
        for env_var in matches:
            value = os.environ.get(env_var, "")
            config_str = config_str.replace(f"{{{{ENV:{env_var}}}}}", value)

        # Convert back to dictionary
        return json.loads(config_str)
    
    def _load_decision_frameworks(self) -> Dict[str, Any]:
        """Load decision framework information."""
        frameworks_file = os.path.join(self.agency_dir, "decision_frameworks.json")
        
        if os.path.exists(frameworks_file):
            try:
                with open(frameworks_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise CDFException(f"Invalid JSON in frameworks file: {e}")
        
        # Return default frameworks if file not found
        return {
            "legislative": {
                "description": "Legislative decision-making frameworks",
                "components": ["debate", "vote", "amendment", "passage"]
            },
            "regulatory": {
                "description": "Regulatory decision-making frameworks",
                "components": ["assessment", "rule_making", "review", "implementation"]
            },
            "judicial": {
                "description": "Judicial decision-making frameworks",
                "components": ["case", "hearing", "opinion", "precedent"]
            },
            "executive": {
                "description": "Executive decision-making frameworks",
                "components": ["directive", "order", "guidance", "enforcement"]
            },
            "scientific": {
                "description": "Scientific decision-making frameworks",
                "components": ["hypothesis", "experiment", "analysis", "conclusion"]
            }
        }
    
    def _load_endpoints(self) -> Dict[str, Any]:
        """Load API endpoint information."""
        endpoints_file = os.path.join(self.agency_dir, "endpoints.json")

        if os.path.exists(endpoints_file):
            try:
                with open(endpoints_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise CDFException(f"Invalid JSON in endpoints file: {e}")

        # Use configuration-based endpoints if file not found
        if self.config:
            api_config = self.config.get("api", {})
            domains_config = self.config.get("domains", {})

            # Construct endpoints from configuration
            endpoints = {
                "base_url": api_config.get("base_url", "https://api.cdf.gov"),
                "protocol_endpoint": f"/{api_config.get('version', 'v1')}/protocols",
                "debate_endpoint": f"/{api_config.get('version', 'v1')}/debates",
                "vote_endpoint": f"/{api_config.get('version', 'v1')}/votes",
                "decision_endpoint": f"/{api_config.get('version', 'v1')}/decisions",
                "auth_endpoint": f"/{api_config.get('version', 'v1')}/auth/token"
            }

            # Add domain URLs
            if "dnc" in domains_config:
                endpoints["dnc_url"] = domains_config["dnc"].get("url", "https://dnc.dev")
            else:
                endpoints["dnc_url"] = "https://dnc.dev"

            if "rnc" in domains_config:
                endpoints["rnc_url"] = domains_config["rnc"].get("url", "https://rnc.dev")
            else:
                endpoints["rnc_url"] = "https://rnc.dev"

            return endpoints

        # Return default endpoints if no configuration available
        return {
            "base_url": "https://api.cdf.gov",
            "protocol_endpoint": "/api/v1/protocols",
            "debate_endpoint": "/api/v1/debates",
            "vote_endpoint": "/api/v1/votes",
            "decision_endpoint": "/api/v1/decisions",
            "dnc_url": "https://dnc.dev",
            "rnc_url": "https://rnc.dev",
            "auth_endpoint": "/api/v1/auth/token"
        }
    
    def _load_integration_status(self) -> Dict[str, Any]:
        """Load integration status information."""
        status_file = os.path.join(self.agency_dir, "integration_status.json")

        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise CDFException(f"Invalid JSON in status file: {e}")

        # Generate status from configuration if file not found
        if self.config:
            integrations_config = self.config.get("integrations", {})
            event_sync = integrations_config.get("event_synchronization", {})
            verification = integrations_config.get("verification", {})
            genetic_engine = integrations_config.get("genetic_engine", {})

            # Generate status based on configuration
            status = {
                "hms_gov": {
                    "status": "connected" if event_sync.get("enabled", True) else "disconnected",
                    "components": [
                        {"name": "Debate Visualization", "status": "operational"},
                        {"name": "Protocol Transformation", "status": "operational"},
                        {"name": "Protocol Verification", "status": "operational" if verification.get("enabled", True) else "disabled"}
                    ],
                    "last_updated": datetime.now().isoformat()
                },
                "hms_cdf": {
                    "status": "connected" if event_sync.get("enabled", True) else "disconnected",
                    "components": [
                        {"name": "Decision Framework", "status": "operational"},
                        {"name": "Voting System", "status": "operational"},
                        {"name": "Debate Model", "status": "operational"}
                    ],
                    "last_updated": datetime.now().isoformat()
                }
            }

            # Add genetic engine component if enabled
            if genetic_engine.get("enabled", True):
                status["hms_cdf"]["components"].append({
                    "name": "Genetic Engine",
                    "status": "operational",
                    "optimization_types": genetic_engine.get("optimization_types", [])
                })

            return status

        # Return default status if no configuration available
        return {
            "hms_gov": {
                "status": "connected",
                "components": [
                    {"name": "Debate Visualization", "status": "operational"},
                    {"name": "Protocol Transformation", "status": "operational"},
                    {"name": "Protocol Verification", "status": "operational"}
                ],
                "last_updated": datetime.now().isoformat()
            },
            "hms_cdf": {
                "status": "connected",
                "components": [
                    {"name": "Decision Framework", "status": "operational"},
                    {"name": "Voting System", "status": "operational"},
                    {"name": "Debate Model", "status": "operational"}
                ],
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def get_implementation_status(self) -> Dict[str, Any]:
        """
        Get implementation status for CDF.
        
        Returns:
            Implementation status dictionary
        """
        # Extract implementation status from implementation plan if available
        status = {
            "agency": "CDF",
            "frameworks": list(self.decision_frameworks.keys()),
            "integration_points": list(self.integration_status.keys()),
            "last_updated": datetime.now().isoformat()
        }
        
        # Parse implementation plan if available
        if "implementation_plan" in self.data:
            # Extract phases and tasks
            plan_content = self.data["implementation_plan"]
            phases = {}
            
            # Extract phase sections
            phase_matches = re.finditer(r'## Phase (\d+): (.*?)\n(.*?)(?=##|\Z)', 
                                      plan_content, re.DOTALL)
            
            for match in phase_matches:
                phase_num = match.group(1)
                phase_name = match.group(2)
                phase_content = match.group(3)
                
                # Extract tasks and their status
                tasks = []
                task_matches = re.finditer(r'- \[([ x])\] (.*?)$', phase_content, re.MULTILINE)
                
                for task_match in task_matches:
                    completed = task_match.group(1) == 'x'
                    task_name = task_match.group(2).strip()
                    
                    tasks.append({
                        "name": task_name,
                        "completed": completed
                    })
                
                # Calculate phase completion percentage
                completed_tasks = sum(1 for task in tasks if task["completed"])
                percentage = (completed_tasks / len(tasks)) * 100 if tasks else 0
                
                phases[f"phase_{phase_num}"] = {
                    "name": phase_name,
                    "tasks": tasks,
                    "completed_tasks": completed_tasks,
                    "total_tasks": len(tasks),
                    "percentage": percentage
                }
            
            status["implementation_phases"] = phases
            
            # Calculate overall completion
            all_tasks = [task for phase in phases.values() for task in phase["tasks"]]
            completed_all = sum(1 for task in all_tasks if task["completed"])
            overall_percentage = (completed_all / len(all_tasks)) * 100 if all_tasks else 0
            
            status["overall_completion"] = {
                "completed_tasks": completed_all,
                "total_tasks": len(all_tasks),
                "percentage": overall_percentage
            }
        
        # Add integration-specific status
        integration_status = {
            name: info.get("status", "unknown") 
            for name, info in self.integration_status.items()
        }
        status["integration_status"] = integration_status
        
        return status
    
    def get_cdf_recommendations(self) -> List[str]:
        """
        Get CDF-specific recommendations.
        
        Returns:
            List of CDF recommendations
        """
        recommendations = []
        
        # Get implementation status
        status = self.get_implementation_status()
        
        # Generate framework-specific recommendations
        for framework, info in self.decision_frameworks.items():
            recommendations.append(f"Enhance {framework} framework with focus on {', '.join(info['components'])}")
        
        # Generate integration-specific recommendations
        for system, info in self.integration_status.items():
            if info.get("status") != "operational":
                recommendations.append(f"Improve {system} integration status")
            
            # Check component status
            for component in info.get("components", []):
                if component.get("status") != "operational":
                    recommendations.append(f"Address issues with {component['name']} in {system}")
        
        # Generate recommendations based on implementation status
        if "implementation_phases" in status:
            phases = status["implementation_phases"]
            
            # Find the first incomplete phase
            current_phase = None
            for phase_key, phase in sorted(phases.items()):
                if phase["percentage"] < 100:
                    current_phase = phase
                    break
            
            if current_phase:
                # Add recommendations for incomplete tasks in the current phase
                for task in current_phase["tasks"]:
                    if not task["completed"]:
                        recommendations.append(f"Complete task: {task['name']}")
        
        return recommendations
    
    def get_codex_context(self) -> Dict[str, Any]:
        """
        Generate Codex context for CDF.
        
        Returns:
            Codex context dictionary
        """
        # Get implementation status
        status = self.get_implementation_status()
        
        # Get recommendations
        recommendations = self.get_cdf_recommendations()
        
        # Compile context
        context = {
            "agency": "CDF",
            "full_name": "Collaborative Decision Framework",
            "frameworks": self.decision_frameworks,
            "endpoints": self.endpoints,
            "integration_status": self.integration_status,
            "implementation_status": status,
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat()
        }
        
        return context
    
    def get_hms_gov_connection_status(self) -> Dict[str, Any]:
        """
        Get HMS-GOV connection status.
        
        Returns:
            HMS-GOV connection status dictionary
        """
        connection_status = {
            "agency": "CDF",
            "connection_target": "HMS-GOV",
            "status": self.integration_status.get("hms_gov", {}).get("status", "unknown"),
            "endpoints": {
                "dnc_url": self.endpoints.get("dnc_url"),
                "rnc_url": self.endpoints.get("rnc_url")
            },
            "components": self.integration_status.get("hms_gov", {}).get("components", []),
            "last_updated": datetime.now().isoformat()
        }
        
        return connection_status
    
    def connect_to_hms_cdf(self, auth_token: str) -> Dict[str, Any]:
        """
        Connect to HMS-CDF API.

        Args:
            auth_token: Authentication token

        Returns:
            Connection result
        """
        try:
            base_url = self.endpoints.get("base_url")
            auth_endpoint = self.endpoints.get("auth_endpoint")

            # Simulated API call for now
            # In a real implementation, this would make an actual HTTP request
            # headers = {"Authorization": f"Bearer {auth_token}"}
            # response = requests.get(f"{base_url}{auth_endpoint}", headers=headers)
            # response.raise_for_status()
            # result = response.json()

            # Simulated result
            result = {
                "status": "connected",
                "message": "Successfully connected to HMS-CDF API",
                "session_id": "cdf-session-12345",
                "expires_at": (datetime.now().timestamp() + 3600) * 1000,  # 1 hour from now
                "endpoints": self.endpoints
            }

            return result

        except Exception as e:
            raise CDFException(f"Failed to connect to HMS-CDF: {e}")

    def connect_to_hms_gov(self, domain: str, auth_token: str) -> Dict[str, Any]:
        """
        Connect to HMS-GOV via the specified domain.

        Args:
            domain: The domain (e.g., 'dnc.dev' or 'rnc.dev')
            auth_token: Authentication token

        Returns:
            Connection result
        """
        try:
            # Validate domain
            if domain not in ['dnc.dev', 'rnc.dev']:
                raise CDFException(f"Invalid domain: {domain}. Must be 'dnc.dev' or 'rnc.dev'")

            # Get domain configuration
            domain_key = 'dnc' if domain == 'dnc.dev' else 'rnc'
            domains_config = self.config.get("domains", {})
            domain_config = domains_config.get(domain_key, {})

            # Construct base URL
            base_url = domain_config.get("url", f"https://{domain}")
            api_path = domain_config.get("api_path", "/api/v1")

            # Get supported features
            features = domain_config.get("features", [])

            # Simulated API call for now
            # In a real implementation, this would make an actual HTTP request
            # headers = {"Authorization": f"Bearer {auth_token}"}
            # response = requests.get(f"{base_url}{api_path}/health", headers=headers)
            # response.raise_for_status()

            # Simulated result
            session_id = f"{domain_key}-session-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            result = {
                "status": "connected",
                "message": f"Successfully connected to HMS-GOV via {domain}",
                "domain": domain,
                "session_id": session_id,
                "features": features,
                "expires_at": (datetime.now().timestamp() + 3600) * 1000,  # 1 hour from now
                "endpoints": {
                    "base_url": base_url,
                    "api_path": api_path,
                    "protocols": f"{base_url}{api_path}/protocols",
                    "debates": f"{base_url}{api_path}/debates",
                    "votes": f"{base_url}{api_path}/votes",
                    "decisions": f"{base_url}{api_path}/decisions"
                }
            }

            return result

        except Exception as e:
            raise CDFException(f"Failed to connect to HMS-GOV via {domain}: {e}")
    
    def transform_protocol(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform protocol data between HMS-GOV and HMS-CDF formats.
        
        Args:
            protocol_data: Source protocol data
            
        Returns:
            Transformed protocol data
        """
        # This is a simplified implementation
        # A real implementation would use the Protocol Transformation Layer
        # to convert between the different protocol formats
        
        source_format = protocol_data.get("_source_format", "hms_gov")
        
        if source_format == "hms_gov":
            # Transform from HMS-GOV to HMS-CDF format
            return {
                "_source_format": "hms_cdf",
                "id": protocol_data.get("id"),
                "name": protocol_data.get("title"),
                "is_published": protocol_data.get("status") == "Active",
                "category": self._map_trial_type_to_category(protocol_data.get("type", "adaptive")),
                "problem": protocol_data.get("background"),
                "goal": protocol_data.get("objectives", {}).get("primary"),
                "solution_context": protocol_data.get("rationale"),
                "versions": protocol_data.get("versions"),
                "metadata": protocol_data.get("metadata", {})
            }
        else:
            # Transform from HMS-CDF to HMS-GOV format
            return {
                "_source_format": "hms_gov",
                "trialId": str(protocol_data.get("id")),
                "title": protocol_data.get("name"),
                "status": "Active" if protocol_data.get("is_published") else "Draft",
                "type": self._map_category_to_trial_type(protocol_data.get("category", "adaptive")),
                "background": protocol_data.get("problem"),
                "objectives": {
                    "primary": protocol_data.get("goal"),
                    "secondary": []
                },
                "rationale": protocol_data.get("solution_context"),
                "versions": protocol_data.get("versions"),
                "metadata": protocol_data.get("metadata", {})
            }
    
    def _map_trial_type_to_category(self, trial_type: str) -> str:
        """
        Map trial type to protocol category.
        
        Args:
            trial_type: Trial type
            
        Returns:
            Protocol category
        """
        # This mapping should match the mapping in protocol_adapter.php
        type_to_category = {
            "mams": "adaptive",
            "biomarker": "biomarker",
            "platform": "platform",
            "basket": "basket",
            "umbrella": "umbrella",
            "standard": "standard"
        }
        
        return type_to_category.get(trial_type.lower(), "adaptive")
    
    def _map_category_to_trial_type(self, category: str) -> str:
        """
        Map protocol category to trial type.

        Args:
            category: Protocol category

        Returns:
            Trial type
        """
        # This mapping should match the mapping in protocol_adapter.php
        category_to_type = {
            "adaptive": "mams",
            "biomarker": "biomarker",
            "platform": "platform",
            "basket": "basket",
            "umbrella": "umbrella",
            "standard": "standard"
        }

        # Use configuration-based mapping if available
        if self.config:
            transformation_config = self.config.get("transformation", {})
            default_mappings = transformation_config.get("default_mappings", {})
            category_mappings = default_mappings.get("category_mappings", {})

            if category_mappings:
                return category_mappings.get(category.lower(), "mams")

        return category_to_type.get(category.lower(), "mams")

    def handle_event(self, event_type: str, event_data: Dict[str, Any], signature: str = None) -> Dict[str, Any]:
        """
        Handle an event from CDF or HMS-GOV.

        Args:
            event_type: Type of event (protocol_update, decision_event, etc.)
            event_data: Event data
            signature: Event signature for verification

        Returns:
            Processing result
        """
        try:
            # Verify signature if provided
            if signature:
                self._verify_event_signature(event_type, event_data, signature)

            # Process event based on type
            if event_type == "protocol_update":
                return self._handle_protocol_update_event(event_data)
            elif event_type == "decision_event":
                return self._handle_decision_event(event_data)
            elif event_type == "debate_event":
                return self._handle_debate_event(event_data)
            elif event_type == "vote_event":
                return self._handle_vote_event(event_data)
            else:
                raise CDFException(f"Unknown event type: {event_type}")

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to handle event: {e}",
                "event_type": event_type
            }

    def _verify_event_signature(self, event_type: str, event_data: Dict[str, Any], signature: str) -> bool:
        """
        Verify event signature.

        Args:
            event_type: Type of event
            event_data: Event data
            signature: Event signature

        Returns:
            Whether signature is valid
        """
        # Get event configuration
        events_config = self.config.get("events", {})
        event_config = events_config.get(event_type, {})

        # Get signature algorithm
        signature_algorithm = event_config.get("signature_algorithm", "sha256")

        # In a real implementation, this would verify the signature
        # For now, just return True
        return True

    def _handle_protocol_update_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a protocol update event.

        Args:
            event_data: Event data

        Returns:
            Processing result
        """
        try:
            protocol_data = event_data.get("protocol", {})
            protocol_id = protocol_data.get("id")

            if not protocol_id:
                raise CDFException("Protocol ID not found in event data")

            # Transform protocol if needed
            source_format = protocol_data.get("_source_format")
            if source_format != "cdf":
                protocol_data = self.transform_protocol(protocol_data)

            # In a real implementation, this would update the protocol in the database
            # For now, just return success
            return {
                "status": "success",
                "message": f"Protocol {protocol_id} updated successfully",
                "protocol_id": protocol_id
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to handle protocol update event: {e}",
                "event_data": event_data
            }

    def _handle_decision_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a decision event.

        Args:
            event_data: Event data

        Returns:
            Processing result
        """
        try:
            decision_data = event_data.get("decision", {})
            decision_id = decision_data.get("id")
            protocol_id = event_data.get("protocol_id")

            if not decision_id or not protocol_id:
                raise CDFException("Decision ID or Protocol ID not found in event data")

            # In a real implementation, this would process the decision
            # For now, just return success
            return {
                "status": "success",
                "message": f"Decision {decision_id} for protocol {protocol_id} processed successfully",
                "decision_id": decision_id,
                "protocol_id": protocol_id
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to handle decision event: {e}",
                "event_data": event_data
            }

    def _handle_debate_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a debate event.

        Args:
            event_data: Event data

        Returns:
            Processing result
        """
        try:
            debate_data = event_data.get("debate", {})
            debate_id = debate_data.get("id")
            protocol_id = event_data.get("protocol_id")

            if not debate_id or not protocol_id:
                raise CDFException("Debate ID or Protocol ID not found in event data")

            # In a real implementation, this would process the debate
            # For now, just return success
            return {
                "status": "success",
                "message": f"Debate {debate_id} for protocol {protocol_id} processed successfully",
                "debate_id": debate_id,
                "protocol_id": protocol_id
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to handle debate event: {e}",
                "event_data": event_data
            }

    def _handle_vote_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a vote event.

        Args:
            event_data: Event data

        Returns:
            Processing result
        """
        try:
            vote_data = event_data.get("vote", {})
            vote_id = vote_data.get("id")
            protocol_id = event_data.get("protocol_id")

            if not vote_id or not protocol_id:
                raise CDFException("Vote ID or Protocol ID not found in event data")

            # In a real implementation, this would process the vote
            # For now, just return success
            return {
                "status": "success",
                "message": f"Vote {vote_id} for protocol {protocol_id} processed successfully",
                "vote_id": vote_id,
                "protocol_id": protocol_id
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to handle vote event: {e}",
                "event_data": event_data
            }


def main():
    """Main entry point function."""
    import argparse

    parser = argparse.ArgumentParser(description="CDF Research Connector")
    parser.add_argument("--base-path", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Base path to CDF data")
    parser.add_argument("--output", choices=["status", "recommendations", "context", "connection", "config"],
                       default="status", help="Type of output to generate")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format for the results")
    parser.add_argument("--connect", choices=["cdf", "dnc", "rnc"],
                       help="Connect to a specific service")
    parser.add_argument("--token", help="Authentication token for connection")
    parser.add_argument("--event", choices=["protocol_update", "decision_event", "debate_event", "vote_event"],
                       help="Handle a specific event type")
    parser.add_argument("--event-data", help="Event data in JSON format")
    parser.add_argument("--event-signature", help="Event signature for verification")

    args = parser.parse_args()

    try:
        # Initialize the CDF connector
        connector = CDFResearchConnector(args.base_path)

        # Handle connection request if specified
        if args.connect:
            if not args.token:
                raise CDFException("Authentication token is required for connection")

            if args.connect == "cdf":
                result = connector.connect_to_hms_cdf(args.token)
            elif args.connect == "dnc":
                result = connector.connect_to_hms_gov("dnc.dev", args.token)
            elif args.connect == "rnc":
                result = connector.connect_to_hms_gov("rnc.dev", args.token)

            # Output the connection result
            if args.format == "json":
                print(json.dumps(result, indent=2))
            else:
                print(f"Connection to {args.connect.upper()} Status")
                print(f"{'-' * (len(args.connect) + 20)}")
                print(f"Status: {result['status']}")
                print(f"Message: {result['message']}")
                if "session_id" in result:
                    print(f"Session ID: {result['session_id']}")
                if "expires_at" in result:
                    expiry_time = datetime.fromtimestamp(result['expires_at'] / 1000)
                    print(f"Expires: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
                if "endpoints" in result:
                    print(f"\nEndpoints:")
                    for name, url in result["endpoints"].items():
                        print(f"  {name}: {url}")
                if "features" in result:
                    print(f"\nFeatures:")
                    for feature in result["features"]:
                        print(f"  - {feature}")

            return

        # Handle event if specified
        if args.event:
            if not args.event_data:
                raise CDFException("Event data is required for event handling")

            try:
                event_data = json.loads(args.event_data)
            except json.JSONDecodeError:
                raise CDFException("Invalid JSON in event data")

            result = connector.handle_event(args.event, event_data, args.event_signature)

            # Output the event handling result
            if args.format == "json":
                print(json.dumps(result, indent=2))
            else:
                print(f"Event Handling Result")
                print(f"---------------------")
                print(f"Status: {result['status']}")
                print(f"Message: {result['message']}")

                # Print additional fields
                for key, value in result.items():
                    if key not in ["status", "message", "event_data"]:
                        print(f"{key}: {value}")

            return

        # Generate the requested output
        if args.output == "status":
            result = connector.get_implementation_status()
        elif args.output == "recommendations":
            result = connector.get_cdf_recommendations()
        elif args.output == "context":
            result = connector.get_codex_context()
        elif args.output == "connection":
            result = connector.get_hms_gov_connection_status()
        elif args.output == "config":
            result = connector.config

        # Output the result in the requested format
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if args.output == "status":
                print(f"CDF Implementation Status")
                print(f"-------------------------")

                if "overall_completion" in result:
                    overall = result["overall_completion"]
                    print(f"Overall Completion: {overall['completed_tasks']}/{overall['total_tasks']} "
                          f"({overall['percentage']:.1f}%)")

                if "implementation_phases" in result:
                    print("\nPhases:")
                    for phase_key, phase in sorted(result["implementation_phases"].items()):
                        print(f"  {phase['name']}: {phase['completed_tasks']}/{phase['total_tasks']} "
                              f"({phase['percentage']:.1f}%)")

                if "integration_status" in result:
                    print("\nIntegration Status:")
                    for system, status in result["integration_status"].items():
                        print(f"  {system}: {status}")

            elif args.output == "recommendations":
                print(f"CDF Implementation Recommendations")
                print(f"----------------------------------")
                for i, recommendation in enumerate(result, 1):
                    print(f"{i}. {recommendation}")

            elif args.output == "context":
                print(f"CDF Codex Context Summary")
                print(f"-------------------------")
                print(f"Frameworks: {', '.join(result['frameworks'].keys())}")

                if "implementation_status" in result and "overall_completion" in result["implementation_status"]:
                    overall = result["implementation_status"]["overall_completion"]
                    print(f"\nOverall Completion: {overall['percentage']:.1f}%")

                print(f"\nTop Recommendations:")
                for i, recommendation in enumerate(result["recommendations"][:3], 1):
                    print(f"{i}. {recommendation}")

            elif args.output == "connection":
                print(f"HMS-GOV Connection Status")
                print(f"-------------------------")
                print(f"Status: {result['status']}")
                print(f"\nEndpoints:")
                for name, url in result["endpoints"].items():
                    print(f"  {name}: {url}")
                print(f"\nComponents:")
                for component in result["components"]:
                    print(f"  {component['name']}: {component['status']}")
                print(f"\nLast Updated: {result['last_updated']}")

            elif args.output == "config":
                print(f"CDF Configuration")
                print(f"-----------------")
                print(f"Connector Version: {result.get('connector', {}).get('version', 'Unknown')}")
                print(f"API Base URL: {result.get('api', {}).get('base_url', 'Unknown')}")

                # Print domains
                domains = result.get('domains', {})
                if domains:
                    print(f"\nDomains:")
                    for domain, config in domains.items():
                        print(f"  {domain}: {config.get('url')}")
                        if 'features' in config:
                            print(f"    Features: {', '.join(config['features'])}")

                # Print transformation settings
                transformation = result.get('transformation', {})
                if transformation:
                    print(f"\nTransformation:")
                    print(f"  Protocol Format Version: {transformation.get('protocol_format_version', 'Unknown')}")
                    print(f"  Supported Formats: {', '.join(transformation.get('supported_formats', []))}")

                # Print integrations
                integrations = result.get('integrations', {})
                if integrations:
                    print(f"\nIntegrations:")
                    for integration, config in integrations.items():
                        status = 'Enabled' if config.get('enabled', False) else 'Disabled'
                        print(f"  {integration}: {status}")

    except CDFException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()