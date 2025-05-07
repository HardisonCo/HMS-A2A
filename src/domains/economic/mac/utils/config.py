"""
Configuration utilities for the MAC architecture.

This module provides functions for loading and saving MAC configuration,
as well as validation and default configuration generation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "supervisor": {
        "name": "MAC-Supervisor",
        "cort_depth": 3,
        "generate_alternatives": 2,
        "human_verification_timeout": 300
    },
    "environment": {
        "persistence_dir": "mac_environment",
        "max_history_length": 1000,
        "auto_persist": True
    },
    "checker": {
        "use_cort_for_verification": True,
        "cort_depth": 2,
        "generate_alternatives": 1,
        "validators": {
            "policy": {
                "type": "policy",
                "rules": {}
            }
        }
    },
    "human_interface": {
        "interface_type": "file",
        "auto_approve_timeout": 600,
        "interface_config": {
            "query_dir": "human_queries",
            "response_dir": "human_responses"
        }
    },
    "domains": {
        "development": {
            "enabled": True,
            "cort_depth": 2
        },
        "operations": {
            "enabled": True,
            "cort_depth": 2
        },
        "governance": {
            "enabled": True,
            "cort_depth": 2
        }
    },
    "demo": {
        "github_token": "",
        "repo_owner": "",
        "repo_name": "",
        "visualization_enabled": True
    }
}

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    # Check if file exists
    if not os.path.exists(config_path):
        logging.warning(f"Configuration file not found: {config_path}")
        return DEFAULT_CONFIG
    
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Merge with defaults for missing keys
        merged_config = _merge_with_defaults(config)
        
        logging.info(f"Loaded configuration from {config_path}")
        return merged_config
        
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Save configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info(f"Saved configuration to {config_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error saving configuration: {str(e)}")
        return False

def create_default_config(config_path: str) -> bool:
    """
    Create default configuration file.
    
    Args:
        config_path: Path to save configuration
        
    Returns:
        True if successful, False otherwise
    """
    return save_config(DEFAULT_CONFIG, config_path)

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration and fix any issues.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated configuration dictionary
    """
    # Ensure all required sections exist
    validated = _merge_with_defaults(config)
    
    # Validate specific values
    # Supervisor
    if validated["supervisor"]["cort_depth"] < 1:
        validated["supervisor"]["cort_depth"] = 1
    
    # Environment
    if validated["environment"]["max_history_length"] < 100:
        validated["environment"]["max_history_length"] = 100
    
    # Human interface
    if validated["human_interface"]["interface_type"] not in ["file", "api", "console"]:
        validated["human_interface"]["interface_type"] = "file"
    
    # Ensure timeout is positive if set
    if validated["human_interface"]["auto_approve_timeout"] is not None:
        if validated["human_interface"]["auto_approve_timeout"] <= 0:
            validated["human_interface"]["auto_approve_timeout"] = None
    
    return validated

def _merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge configuration with defaults for missing keys.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    # Start with defaults
    merged = DEFAULT_CONFIG.copy()
    
    # Helper function for recursive merge
    def _deep_merge(target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                _deep_merge(target[key], value)
            else:
                target[key] = value
    
    # Merge user config
    _deep_merge(merged, config)
    
    return merged