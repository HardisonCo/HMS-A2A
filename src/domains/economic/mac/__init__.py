"""
Multi-Agent Collaboration (MAC) Model for HMS-A2A.

This package implements the MAC architecture which enhances HMS-A2A with:
1. Supervisor Agent for central task orchestration
2. Domain-Specialist Agents for specialized expertise
3. Environment/State Store for persistent shared memory
4. External Checker for verification-first validation
5. Human Query Interface for governance and oversight

The MAC Model provides a robust, scalable framework for complex multi-agent collaboration,
ensuring verifiable outputs and transparent reasoning processes.
"""

__version__ = "1.0.0"

# Core components
from mac.supervisor_agent import SupervisorAgent, create_supervisor
from mac.environment.state_store import StateStore
from mac.verification.checker import ExternalChecker, VerificationResult
from mac.human_interface.interface import HumanQueryInterface

# Utility functions
from mac.utils.config import load_config, save_config
from mac.utils.visualization import visualize_collaboration

# Domain agents
from mac.domains.development import DevelopmentDomainAgent
from mac.domains.operations import OperationsDomainAgent
from mac.domains.governance import GovernanceDomainAgent

# Demo utilities
from mac.demo.github_demo import GitHubIssueDemo
from mac.demo.visualizer import MACCollaborationVisualizer