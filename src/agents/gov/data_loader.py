"""
Agency Data Loader

Loads agency data from data files to configure agents properly.
"""

import os
import json
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define paths
DATA_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..",
    "data"
))

AGENCY_DATA_FILE = os.path.join(DATA_DIR, "GOV_A2A_MCP_TOOL.json")
AGENCY_META_FILE = os.path.join(DATA_DIR, "GOV_A2A_MCP_TOOL_META.json")
FED_DATA_FILE = os.path.join(DATA_DIR, "fed.json")

# Global cache for loaded data
_agency_data_cache = {}
_agency_meta_cache = {}
_fed_data_cache = None


def load_agency_data(agency_label: str) -> Dict[str, Any]:
    """Load data for a specific agency.
    
    Args:
        agency_label: The agency label (e.g., "CIA", "USADF")
        
    Returns:
        Dictionary with agency data
        
    Raises:
        ValueError: If agency data is not found
    """
    global _agency_data_cache
    
    # Check cache first
    if agency_label in _agency_data_cache:
        return _agency_data_cache[agency_label]
    
    # Try to load from AGENCY_DATA_FILE if it exists
    if os.path.exists(AGENCY_DATA_FILE):
        try:
            with open(AGENCY_DATA_FILE, 'r') as f:
                data = json.load(f)
                
            # Find matching agency
            if "agencyMappings" in data:
                for agency in data["agencyMappings"]:
                    if agency.get("agencyLabel") == agency_label:
                        # Cache and return
                        _agency_data_cache[agency_label] = agency
                        return agency
        except Exception as e:
            logger.error(f"Error loading agency data from {AGENCY_DATA_FILE}: {e}")
    
    # If not found in AGENCY_DATA_FILE, try FED_DATA_FILE
    agency_data = load_agency_data_from_fed(agency_label)
    if agency_data:
        _agency_data_cache[agency_label] = agency_data
        return agency_data
    
    # Agency not found
    raise ValueError(f"Agency data not found for {agency_label}")


def load_agency_data_from_fed(agency_label: str) -> Optional[Dict[str, Any]]:
    """Load agency data from the fed.json file.
    
    Args:
        agency_label: The agency label
        
    Returns:
        Dictionary with agency data or None if not found
    """
    global _fed_data_cache
    
    # Load fed data if not cached
    if _fed_data_cache is None:
        if os.path.exists(FED_DATA_FILE):
            try:
                with open(FED_DATA_FILE, 'r') as f:
                    _fed_data_cache = json.load(f)
            except Exception as e:
                logger.error(f"Error loading fed data from {FED_DATA_FILE}: {e}")
                _fed_data_cache = {}
        else:
            logger.warning(f"Fed data file not found: {FED_DATA_FILE}")
            _fed_data_cache = {}
    
    # Find matching agency
    if "agencyMappings" in _fed_data_cache:
        for agency in _fed_data_cache["agencyMappings"]:
            if agency.get("agencyLabel") == agency_label:
                return agency
    
    return None


def load_agency_metadata(agency_label: str) -> Dict[str, Any]:
    """Load metadata for a specific agency.
    
    Args:
        agency_label: The agency label
        
    Returns:
        Dictionary with agency metadata or empty dict if not found
    """
    global _agency_meta_cache
    
    # Check cache first
    if agency_label in _agency_meta_cache:
        return _agency_meta_cache[agency_label]
    
    # Try to load from AGENCY_META_FILE if it exists
    if os.path.exists(AGENCY_META_FILE):
        try:
            with open(AGENCY_META_FILE, 'r') as f:
                data = json.load(f)
                
            # Find matching agency
            if "agencyAgentToolMapping" in data:
                for agency in data["agencyAgentToolMapping"]:
                    if agency.get("agencyLabel") == agency_label:
                        # Cache and return
                        _agency_meta_cache[agency_label] = agency
                        return agency
        except Exception as e:
            logger.error(f"Error loading agency metadata from {AGENCY_META_FILE}: {e}")
    
    # Return empty dict if not found
    return {}


def get_all_agency_labels() -> List[str]:
    """Get all available agency labels.
    
    Returns:
        List of agency labels
    """
    labels = set()
    
    # Check AGENCY_DATA_FILE
    if os.path.exists(AGENCY_DATA_FILE):
        try:
            with open(AGENCY_DATA_FILE, 'r') as f:
                data = json.load(f)
                
            if "agencyMappings" in data:
                for agency in data["agencyMappings"]:
                    if "agencyLabel" in agency:
                        labels.add(agency["agencyLabel"])
        except Exception as e:
            logger.error(f"Error loading agency data for labels from {AGENCY_DATA_FILE}: {e}")
    
    # Check FED_DATA_FILE
    if os.path.exists(FED_DATA_FILE):
        try:
            with open(FED_DATA_FILE, 'r') as f:
                data = json.load(f)
                
            if "agencyMappings" in data:
                for agency in data["agencyMappings"]:
                    if "agencyLabel" in agency:
                        labels.add(agency["agencyLabel"])
        except Exception as e:
            logger.error(f"Error loading fed data for labels from {FED_DATA_FILE}: {e}")
    
    return sorted(list(labels))


def get_agent_types_for_agency(agency_label: str) -> List[str]:
    """Get the agent types for a specific agency.
    
    Args:
        agency_label: The agency label
        
    Returns:
        List of agent types
    """
    # Try to get from agency data
    try:
        agency_data = load_agency_data(agency_label)
        if "relevantAgentTypes" in agency_data:
            return agency_data["relevantAgentTypes"]
    except ValueError:
        pass
    
    # Try to get from metadata
    agency_meta = load_agency_metadata(agency_label)
    if "relevantAgents" in agency_meta:
        return agency_meta["relevantAgents"]
    
    # Default
    return ["default-agent"]


def get_mcp_tools_for_agency(agency_label: str) -> List[Dict[str, Any]]:
    """Get the MCP tools for a specific agency.
    
    Args:
        agency_label: The agency label
        
    Returns:
        List of MCP tool definitions
    """
    # Try to get from agency data
    try:
        agency_data = load_agency_data(agency_label)
        if "neededMCPTools" in agency_data:
            return agency_data["neededMCPTools"]
    except ValueError:
        pass
    
    # Try to get from metadata
    agency_meta = load_agency_metadata(agency_label)
    if "requiredMCPTools" in agency_meta:
        # Convert from string list to dict list if needed
        tools = agency_meta["requiredMCPTools"]
        if tools and isinstance(tools[0], str):
            return [{"toolName": tool.replace("MCP Tool: ", ""), "description": ""} for tool in tools]
        return tools
    
    # Default
    return []