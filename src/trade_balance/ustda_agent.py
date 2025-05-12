"""
USTDA Agent for the Trade Balance System.

This module implements the US Trade & Development Agency (USTDA) agent
for the trade balance system, providing policy development, program
management, and import certificate functionality.
"""

import datetime
import random
import uuid
from typing import Dict, List, Optional, Any, Union

from trade_balance.interfaces import (
    GovernancePolicy, PolicyType, PolicyStatus, PolicyHistoryEntry,
    ProgramActivity, ProgramStatus, ProgramMetrics,
    Certificate, IUSTDAAgent
)
from trade_balance.certificate_system import CertificateManager


class USTDAAgent(IUSTDAAgent):
    """
    US Trade & Development Agency (USTDA) agent implementation for
    trade policy development and import certificate management.
    """
    
    def __init__(self):
        """Initialize the USTDA agent."""
        self.name = "US Trade & Development Agency"
        self._agent_id = "USTDA-001"
        self.description = "Government agency for trade development and policy implementation."
        self._capabilities = [
            "trade_facilitation", 
            "policy_development", 
            "certificate_issuance",
            "development_financing"
        ]
        
        # Initialize components
        self.policies: Dict[str, GovernancePolicy] = {}
        self.programs: Dict[str, ProgramActivity] = {}
        self.certificate_manager = CertificateManager()
        
        # Create default import certificate policy
        self._create_default_policy()
    
    @property
    def agent_id(self) -> str:
        """Get agent ID."""
        return self._agent_id
    
    @property
    def capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self._capabilities.copy()
    
    def _create_default_policy(self):
        """Create default import certificate policy."""
        policy_id = f"POL-{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()
        
        policy = GovernancePolicy(
            policy_id=policy_id,
            title="Import Certificate Trading System",
            description="Framework for balanced trade through certificate trading",
            policy_type=PolicyType.IMPORT_CERTIFICATE,
            status=PolicyStatus.ACTIVE,
            version="1.0",
            created_at=now,
            updated_at=now,
            parameters={
                "certificate_duration": 180,
                "initial_allocation": 100.0,
                "transfer_fee": 0.005
            },
            legislative_history=[
                PolicyHistoryEntry(
                    timestamp=now,
                    from_status=PolicyStatus.DRAFT,
                    to_status=PolicyStatus.ACTIVE,
                    comment="Initial policy activation"
                )
            ]
        )
        
        self.policies[policy_id] = policy
    
    def create_policy(self, policy_data: Dict[str, Any]) -> GovernancePolicy:
        """
        Create a new policy.
        
        Args:
            policy_data: Policy data
            
        Returns:
            Created policy
        """
        policy_id = policy_data.get("policy_id", f"POL-{uuid.uuid4().hex[:8]}")
        now = datetime.datetime.now().isoformat()
        
        # Convert string values to enums
        policy_type = policy_data.get("policy_type")
        if isinstance(policy_type, str):
            policy_type = PolicyType(policy_type)
            
        status = policy_data.get("status", "draft")
        if isinstance(status, str):
            status = PolicyStatus(status)
        
        # Create policy
        policy = GovernancePolicy(
            policy_id=policy_id,
            title=policy_data.get("title", "Untitled Policy"),
            description=policy_data.get("description", ""),
            policy_type=policy_type,
            status=status,
            version=policy_data.get("version", "1.0"),
            created_at=now,
            updated_at=now,
            parameters=policy_data.get("parameters", {}),
            legislative_history=[
                PolicyHistoryEntry(
                    timestamp=now,
                    from_status=PolicyStatus.DRAFT,
                    to_status=status,
                    comment=policy_data.get("comment", "Initial policy creation")
                )
            ]
        )
        
        # Store policy
        self.policies[policy_id] = policy
        
        return policy
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> GovernancePolicy:
        """
        Update an existing policy.
        
        Args:
            policy_id: Policy ID
            updates: Updates to apply
            
        Returns:
            Updated policy
        """
        # Check if policy exists
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")
        
        policy = self.policies[policy_id]
        now = datetime.datetime.now().isoformat()
        
        # Update fields
        if "title" in updates:
            policy.title = updates["title"]
        
        if "description" in updates:
            policy.description = updates["description"]
        
        if "version" in updates:
            policy.version = updates["version"]
        
        if "parameters" in updates:
            policy.parameters.update(updates["parameters"])
        
        if "status" in updates:
            old_status = policy.status
            new_status = updates["status"]
            
            # Convert string status to enum if needed
            if isinstance(new_status, str):
                new_status = PolicyStatus(new_status)
            
            policy.status = new_status
            
            # Add to legislative history
            policy.legislative_history.append(
                PolicyHistoryEntry(
                    timestamp=now,
                    from_status=old_status,
                    to_status=new_status,
                    comment=updates.get("comment", f"Status updated from {old_status.value} to {new_status.value}")
                )
            )
        
        # Update timestamp
        policy.updated_at = now
        
        # Store updated policy
        self.policies[policy_id] = policy
        
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[GovernancePolicy]:
        """
        Get a policy by ID.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Policy if found, None otherwise
        """
        return self.policies.get(policy_id)
    
    def list_policies(self, filters: Dict[str, Any] = None) -> List[GovernancePolicy]:
        """
        List policies matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching policies
        """
        if not filters:
            return list(self.policies.values())
        
        # Apply filters
        result = []
        for policy in self.policies.values():
            match = True
            
            for key, value in filters.items():
                if key == "policy_type":
                    # Handle enum matching
                    if isinstance(value, str):
                        value = PolicyType(value)
                    if policy.policy_type != value:
                        match = False
                        break
                elif key == "status":
                    # Handle enum matching
                    if isinstance(value, str):
                        value = PolicyStatus(value)
                    if policy.status != value:
                        match = False
                        break
                elif hasattr(policy, key):
                    if getattr(policy, key) != value:
                        match = False
                        break
            
            if match:
                result.append(policy)
        
        return result
    
    def create_program(self, program_data: Dict[str, Any]) -> ProgramActivity:
        """
        Create a new program.
        
        Args:
            program_data: Program data
            
        Returns:
            Created program
        """
        program_id = program_data.get("program_id", f"PROG-{uuid.uuid4().hex[:8]}")
        now = datetime.datetime.now().isoformat()
        
        # Convert string status to enum if needed
        status = program_data.get("status", "setup")
        if isinstance(status, str):
            status = ProgramStatus(status)
        
        # Create metrics
        metrics = ProgramMetrics(
            trade_flows=0,
            total_volume=0.0,
            balance=0.0,
            war_score=0.0,
            start_date=None,
            last_updated=None,
            custom_metrics=program_data.get("custom_metrics", {})
        )
        
        # Create program
        program = ProgramActivity(
            program_id=program_id,
            title=program_data.get("title", "Untitled Program"),
            description=program_data.get("description", ""),
            country_a=program_data.get("country_a", ""),
            country_b=program_data.get("country_b", ""),
            created_at=now,
            updated_at=now,
            status=status,
            metrics=metrics,
            activity_log=[
                {
                    "timestamp": now,
                    "action": "created",
                    "details": "Program created"
                }
            ]
        )
        
        # Store program
        self.programs[program_id] = program
        
        return program
    
    def update_program(self, program_id: str, updates: Dict[str, Any]) -> ProgramActivity:
        """
        Update an existing program.
        
        Args:
            program_id: Program ID
            updates: Updates to apply
            
        Returns:
            Updated program
        """
        # Check if program exists
        if program_id not in self.programs:
            raise ValueError(f"Program {program_id} not found")
        
        program = self.programs[program_id]
        now = datetime.datetime.now().isoformat()
        
        # Update fields
        if "title" in updates:
            program.title = updates["title"]
        
        if "description" in updates:
            program.description = updates["description"]
        
        if "country_a" in updates:
            program.country_a = updates["country_a"]
        
        if "country_b" in updates:
            program.country_b = updates["country_b"]
        
        if "status" in updates:
            old_status = program.status
            new_status = updates["status"]
            
            # Convert string status to enum if needed
            if isinstance(new_status, str):
                new_status = ProgramStatus(new_status)
            
            program.status = new_status
            
            # Add to activity log
            program.activity_log.append({
                "timestamp": now,
                "action": "status_change",
                "details": f"Status updated from {old_status.value} to {new_status.value}"
            })
            
            # Update start date if activating
            if new_status == ProgramStatus.ACTIVE and not program.metrics.start_date:
                program.metrics.start_date = now
        
        if "metrics" in updates:
            # Update metrics
            metrics_updates = updates["metrics"]
            
            if "trade_flows" in metrics_updates:
                program.metrics.trade_flows = metrics_updates["trade_flows"]
            
            if "total_volume" in metrics_updates:
                program.metrics.total_volume = metrics_updates["total_volume"]
            
            if "balance" in metrics_updates:
                program.metrics.balance = metrics_updates["balance"]
            
            if "war_score" in metrics_updates:
                program.metrics.war_score = metrics_updates["war_score"]
            
            if "custom_metrics" in metrics_updates:
                if not program.metrics.custom_metrics:
                    program.metrics.custom_metrics = {}
                
                program.metrics.custom_metrics.update(metrics_updates["custom_metrics"])
            
            # Update last updated timestamp
            program.metrics.last_updated = now
        
        # Add activity log entry if specified
        if "log_entry" in updates:
            program.activity_log.append({
                "timestamp": now,
                "action": updates["log_entry"].get("action", "update"),
                "details": updates["log_entry"].get("details", "Program updated")
            })
        
        # Update timestamp
        program.updated_at = now
        
        # Store updated program
        self.programs[program_id] = program
        
        return program
    
    def get_program(self, program_id: str) -> Optional[ProgramActivity]:
        """
        Get a program by ID.
        
        Args:
            program_id: Program ID
            
        Returns:
            Program if found, None otherwise
        """
        return self.programs.get(program_id)
    
    def list_programs(self, filters: Dict[str, Any] = None) -> List[ProgramActivity]:
        """
        List programs matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching programs
        """
        if not filters:
            return list(self.programs.values())
        
        # Apply filters
        result = []
        for program in self.programs.values():
            match = True
            
            for key, value in filters.items():
                if key == "status":
                    # Handle enum matching
                    if isinstance(value, str):
                        value = ProgramStatus(value)
                    if program.status != value:
                        match = False
                        break
                elif key == "country":
                    # Match either country
                    if program.country_a != value and program.country_b != value:
                        match = False
                        break
                elif hasattr(program, key):
                    if getattr(program, key) != value:
                        match = False
                        break
            
            if match:
                result.append(program)
        
        return result
    
    def create_trade_deal(
        self,
        title: str,
        description: str,
        country_a: str,
        country_b: str
    ) -> Dict[str, Any]:
        """
        Create a new trade deal between countries.
        
        Args:
            title: Deal title
            description: Deal description
            country_a: First country
            country_b: Second country
            
        Returns:
            Dictionary with deal details
        """
        # Create program for the deal
        program_data = {
            "title": title,
            "description": description,
            "country_a": country_a,
            "country_b": country_b,
            "status": "setup",
            "metrics": {
                "trade_flows": 0,
                "total_volume": 0.0,
                "balance": 0.0,
                "war_score": 2.5  # Neutral starting value
            }
        }
        
        program = self.create_program(program_data)
        
        return {
            "program_id": program.program_id,
            "title": program.title,
            "countries": [program.country_a, program.country_b],
            "status": program.status.value,
            "message": "Trade deal created successfully"
        }
    
    def issue_import_certificate(self, owner: str, value: float) -> Certificate:
        """
        Issue an import certificate to an entity.
        
        Args:
            owner: Entity receiving the certificate
            value: Certificate value
            
        Returns:
            Created ImportCertificate
        """
        return self.certificate_manager.issue_certificate(
            owner=owner,
            value=value
        )
    
    def get_moneyball_opportunities(self) -> List[Dict[str, Any]]:
        """
        Generate Moneyball-style opportunities.
        
        Returns:
            List of undervalued opportunities
        """
        # In a real implementation, this would use data analysis
        # to identify undervalued sectors. For the demo, we generate
        # simulated opportunities.
        sectors = ["technology", "renewable_energy", "infrastructure", "agriculture", "manufacturing"]
        
        opportunities = []
        for sector in sectors:
            if random.random() > 0.3:  # 70% chance of opportunity in each sector
                opportunity_score = random.uniform(1.2, 2.5)
                opportunities.append({
                    "sector": sector,
                    "opportunity_score": round(opportunity_score, 2),
                    "current_volume": random.uniform(50000, 500000),
                    "growth_potential": round(random.uniform(1.2, 2.5), 2),
                    "development_potential": round(random.uniform(0.8, 2.0), 2),
                    "recommendation": "Increase focus" if opportunity_score > 1.8 else "Monitor growth"
                })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return opportunities