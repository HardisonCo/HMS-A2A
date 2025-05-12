#!/usr/bin/env python3
"""
Python bindings for the agency FFI interface.

This module provides Python bindings for the agency FFI interface,
allowing Python code to interact with the agency system.
"""

import os
import json
import ctypes
from typing import Dict, List, Any, Optional, Union, Tuple

# Load the agency FFI library
_lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'c/libagency_ffi.so')
_lib = ctypes.CDLL(_lib_path)

# Define argument and return types for FFI functions
_lib.agency_get_context.argtypes = [ctypes.c_char_p]
_lib.agency_get_context.restype = ctypes.c_char_p

_lib.agency_get_issue_finder.argtypes = [ctypes.c_char_p]
_lib.agency_get_issue_finder.restype = ctypes.c_char_p

_lib.agency_get_research_connector.argtypes = [ctypes.c_char_p]
_lib.agency_get_research_connector.restype = ctypes.c_char_p

_lib.agency_get_ascii_art.argtypes = [ctypes.c_char_p]
_lib.agency_get_ascii_art.restype = ctypes.c_char_p

_lib.agency_free_context.argtypes = [ctypes.c_char_p]
_lib.agency_free_context.restype = None

_lib.agency_get_all_agencies.argtypes = []
_lib.agency_get_all_agencies.restype = ctypes.c_char_p

_lib.agency_get_agencies_by_tier.argtypes = [ctypes.c_int]
_lib.agency_get_agencies_by_tier.restype = ctypes.c_char_p

_lib.agency_get_agencies_by_domain.argtypes = [ctypes.c_char_p]
_lib.agency_get_agencies_by_domain.restype = ctypes.c_char_p

_lib.agency_verify_issue.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_lib.agency_verify_issue.restype = ctypes.c_int


class AgencyError(Exception):
    """Exception raised for errors in the agency FFI interface."""
    pass


def _check_string_result(result: Optional[bytes]) -> str:
    """
    Check and convert a string result from the FFI interface.
    
    Args:
        result: The result from the FFI function call.
        
    Returns:
        The decoded string.
        
    Raises:
        AgencyError: If the result is None or empty.
    """
    if result is None:
        raise AgencyError("Operation failed")
    
    # Convert bytes to string
    string_result = result.decode('utf-8')
    
    # Free the result
    _lib.agency_free_context(result)
    
    return string_result


def get_context(agency: str) -> Dict[str, Any]:
    """
    Get the context information for an agency.
    
    Args:
        agency: The agency acronym (e.g., "HHS", "DOD").
        
    Returns:
        A dictionary containing the context information.
        
    Raises:
        AgencyError: If the agency is not found or an error occurs.
    """
    agency_bytes = agency.encode('utf-8')
    result = _lib.agency_get_context(agency_bytes)
    context_str = _check_string_result(result)
    
    try:
        return json.loads(context_str)
    except json.JSONDecodeError as e:
        raise AgencyError(f"Error parsing context: {e}")


def get_issue_finder(agency: str) -> str:
    """
    Get the issue finder data for an agency.
    
    Args:
        agency: The agency acronym (e.g., "HHS", "DOD").
        
    Returns:
        A string containing the issue finder data.
        
    Raises:
        AgencyError: If the agency is not found or an error occurs.
    """
    agency_bytes = agency.encode('utf-8')
    result = _lib.agency_get_issue_finder(agency_bytes)
    return _check_string_result(result)


def get_research_connector(agency: str) -> str:
    """
    Get the research connector data for an agency.
    
    Args:
        agency: The agency acronym (e.g., "HHS", "DOD").
        
    Returns:
        A string containing the research connector data.
        
    Raises:
        AgencyError: If the agency is not found or an error occurs.
    """
    agency_bytes = agency.encode('utf-8')
    result = _lib.agency_get_research_connector(agency_bytes)
    return _check_string_result(result)


def get_ascii_art(agency: str) -> str:
    """
    Get the ASCII art for an agency.
    
    Args:
        agency: The agency acronym (e.g., "HHS", "DOD").
        
    Returns:
        A string containing the ASCII art.
        
    Raises:
        AgencyError: If the agency is not found or an error occurs.
    """
    agency_bytes = agency.encode('utf-8')
    result = _lib.agency_get_ascii_art(agency_bytes)
    return _check_string_result(result)


def get_all_agencies() -> List[str]:
    """
    Get the list of all available agencies.
    
    Returns:
        A list of agency acronyms.
        
    Raises:
        AgencyError: If an error occurs.
    """
    result = _lib.agency_get_all_agencies()
    agencies_str = _check_string_result(result)
    
    try:
        return json.loads(agencies_str)
    except json.JSONDecodeError as e:
        raise AgencyError(f"Error parsing agencies: {e}")


def get_agencies_by_tier(tier: int) -> List[str]:
    """
    Get the agencies in a specific tier.
    
    Args:
        tier: The tier number (1-8).
        
    Returns:
        A list of agency acronyms.
        
    Raises:
        AgencyError: If an error occurs.
    """
    result = _lib.agency_get_agencies_by_tier(tier)
    agencies_str = _check_string_result(result)
    
    try:
        return json.loads(agencies_str)
    except json.JSONDecodeError as e:
        raise AgencyError(f"Error parsing agencies: {e}")


def get_agencies_by_domain(domain: str) -> List[str]:
    """
    Get the agencies for a specific domain.
    
    Args:
        domain: The domain name (e.g., "healthcare", "defense").
        
    Returns:
        A list of agency acronyms.
        
    Raises:
        AgencyError: If an error occurs.
    """
    domain_bytes = domain.encode('utf-8')
    result = _lib.agency_get_agencies_by_domain(domain_bytes)
    agencies_str = _check_string_result(result)
    
    try:
        return json.loads(agencies_str)
    except json.JSONDecodeError as e:
        raise AgencyError(f"Error parsing agencies: {e}")


def verify_issue(agency: str, issue: Dict[str, Any]) -> bool:
    """
    Verify an issue using the agency theorem prover.
    
    Args:
        agency: The agency acronym (e.g., "HHS", "DOD").
        issue: The issue to verify.
        
    Returns:
        True if the issue is valid, False otherwise.
        
    Raises:
        AgencyError: If an error occurs.
    """
    agency_bytes = agency.encode('utf-8')
    
    try:
        issue_json = json.dumps(issue)
    except TypeError as e:
        raise AgencyError(f"Error serializing issue: {e}")
    
    issue_bytes = issue_json.encode('utf-8')
    result = _lib.agency_verify_issue(agency_bytes, issue_bytes)
    
    if result == 1:
        return True
    elif result == 0:
        return False
    else:
        raise AgencyError("Error verifying issue")


class Agency:
    """
    A class representing an agency.
    """
    
    def __init__(self, acronym: str, name: str, domain: str = "", description: str = "", tier: int = 0):
        """
        Initialize an agency.
        
        Args:
            acronym: The agency acronym.
            name: The agency name.
            domain: The agency domain.
            description: The agency description.
            tier: The agency tier.
        """
        self.acronym = acronym
        self.name = name
        self.domain = domain
        self.description = description
        self.tier = tier
    
    @classmethod
    def from_context(cls, agency: str) -> 'Agency':
        """
        Create an Agency object from the agency context.
        
        Args:
            agency: The agency acronym.
            
        Returns:
            An Agency object.
            
        Raises:
            AgencyError: If the agency is not found or an error occurs.
        """
        context = get_context(agency)
        
        return cls(
            acronym=context.get('acronym', ''),
            name=context.get('name', ''),
            domain=context.get('domain', ''),
            description=context.get('description', ''),
            tier=context.get('tier', 0)
        )
    
    def get_issue_finder(self) -> str:
        """
        Get the issue finder data for this agency.
        
        Returns:
            A string containing the issue finder data.
            
        Raises:
            AgencyError: If an error occurs.
        """
        return get_issue_finder(self.acronym)
    
    def get_research_connector(self) -> str:
        """
        Get the research connector data for this agency.
        
        Returns:
            A string containing the research connector data.
            
        Raises:
            AgencyError: If an error occurs.
        """
        return get_research_connector(self.acronym)
    
    def get_ascii_art(self) -> str:
        """
        Get the ASCII art for this agency.
        
        Returns:
            A string containing the ASCII art.
            
        Raises:
            AgencyError: If an error occurs.
        """
        return get_ascii_art(self.acronym)
    
    def verify_issue(self, issue: Dict[str, Any]) -> bool:
        """
        Verify an issue using this agency's theorem prover.
        
        Args:
            issue: The issue to verify.
            
        Returns:
            True if the issue is valid, False otherwise.
            
        Raises:
            AgencyError: If an error occurs.
        """
        return verify_issue(self.acronym, issue)
    
    def __str__(self) -> str:
        """Return a string representation of the agency."""
        return f"{self.acronym}: {self.name}"
    
    def __repr__(self) -> str:
        """Return a string representation of the agency."""
        return f"Agency(acronym='{self.acronym}', name='{self.name}', domain='{self.domain}', tier={self.tier})"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agency FFI Python Bindings")
    parser.add_argument("--agency", help="Agency acronym")
    parser.add_argument("--tier", type=int, help="Agency tier")
    parser.add_argument("--domain", help="Agency domain")
    parser.add_argument("--all", action="store_true", help="List all agencies")
    parser.add_argument("--context", action="store_true", help="Get agency context")
    parser.add_argument("--finder", action="store_true", help="Get agency issue finder")
    parser.add_argument("--connector", action="store_true", help="Get agency research connector")
    parser.add_argument("--ascii", action="store_true", help="Get agency ASCII art")
    
    args = parser.parse_args()
    
    try:
        if args.all:
            agencies = get_all_agencies()
            print(f"All agencies: {agencies}")
        
        if args.tier is not None:
            agencies = get_agencies_by_tier(args.tier)
            print(f"Tier {args.tier} agencies: {agencies}")
        
        if args.domain:
            agencies = get_agencies_by_domain(args.domain)
            print(f"Domain '{args.domain}' agencies: {agencies}")
        
        if args.agency:
            if args.context:
                context = get_context(args.agency)
                print(f"Context for {args.agency}:")
                print(json.dumps(context, indent=2))
            
            if args.finder:
                finder = get_issue_finder(args.agency)
                print(f"Issue finder for {args.agency}:")
                print(finder)
            
            if args.connector:
                connector = get_research_connector(args.agency)
                print(f"Research connector for {args.agency}:")
                print(connector)
            
            if args.ascii:
                art = get_ascii_art(args.agency)
                print(f"ASCII art for {args.agency}:")
                print(art)
            
            if not (args.context or args.finder or args.connector or args.ascii):
                agency = Agency.from_context(args.agency)
                print(f"Agency: {agency}")
                print(f"Name: {agency.name}")
                print(f"Domain: {agency.domain}")
                print(f"Tier: {agency.tier}")
                print(f"Description: {agency.description}")
    
    except AgencyError as e:
        print(f"Error: {e}")
        exit(1)