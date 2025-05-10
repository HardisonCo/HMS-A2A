"""
Collaboration Framework for Standards-Compliant Agents

This package provides a framework for standards-compliant agents to collaborate
using the Deals framework and MCP tools.
"""

from .deals import Deal, Problem, Solution, Player, Transaction
from .deal_tools import DealTools

__all__ = [
    'Deal', 'Problem', 'Solution', 'Player', 'Transaction',
    'DealTools'
]