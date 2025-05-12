#!/usr/bin/env python3
"""
Test script for the APHIS Bird Flu Tracking System Genetic Analysis API

This script sends test requests to the genetic analysis API endpoints
and displays the responses. It is useful for testing that the API is
working correctly.

Usage:
  python test_genetic_api.py [--host HOST] [--port PORT]

Options:
  --host HOST    API server host [default: localhost]
  --port PORT    API server port [default: 8000]
"""

import sys
import json
import argparse
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

def print_json(data: Any) -> None:
    """Print JSON data in a readable format."""
    print(json.dumps(data, indent=2))

def test_sequence_analysis(base_url: str) -> None:
    """Test the sequence analysis endpoint."""
    print("\n=== Testing Sequence Analysis ===")
    
    url = f"{base_url}/genetic/sequences/analyze"
    
    # Example H5N1 HA sequence (this is a shortened placeholder sequence)
    payload = {
        "sequence": "ATGGAGAAAATAGTGCTTCTTCTTGCAATAGTCAGTCTTGTTAAAAGTGATCAGATTTGCATTGGTTACCATGCAAACAACTCGACAGAGCAGGTTGACACAATAATGGAAAAGAACGTTACTGTTACACATGCCCAAGACATACTGGAAAAGACACACA",
        "subtype": "H5N1",
        "gene": "HA"
    }
    
    print(f"Sending request to {url}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print("Status: Success")
        print(f"Found {len(result.get('mutations', []))} mutations")
        print(f"Lineage: {result.get('lineage', {}).get('lineage')}")
        print(f"Zoonotic risk: {result.get('zoonotic_potential', {}).get('zoonotic_risk_level')}")
        print("\nFull Response:")
        print_json(result)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print_json(e.response.json())
            except:
                print(e.response.text)

def test_transmission_network(base_url: str) -> None:
    """Test the transmission network analysis endpoint."""
    print("\n=== Testing Transmission Network Analysis ===")
    
    url = f"{base_url}/genetic/transmission/network"
    
    payload = {
        "genetic_threshold": 0.05,
        "temporal_window": 30,
        "spatial_threshold": 100.0
    }
    
    print(f"Sending request to {url}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print("Status: Success")
        print(f"Cases analyzed: {result.get('cases', 0)}")
        print(f"Links found: {len(result.get('links', []))}")
        print(f"Clusters identified: {len(result.get('clusters', []))}")
        print("\nFull Response:")
        print_json(result)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print_json(e.response.json())
            except:
                print(e.response.text)

def test_transmission_pattern(base_url: str) -> None:
    """Test the transmission pattern assessment endpoint."""
    print("\n=== Testing Transmission Pattern Assessment ===")
    
    # First get a network to use for pattern assessment
    network_url = f"{base_url}/genetic/transmission/network"
    network_payload = {
        "genetic_threshold": 0.05,
        "temporal_window": 30,
        "spatial_threshold": 100.0
    }
    
    print(f"Fetching network from {network_url}")
    try:
        network_response = requests.post(network_url, json=network_payload)
        network_response.raise_for_status()
        network = network_response.json()
        
        # Now assess the pattern
        pattern_url = f"{base_url}/genetic/transmission/pattern"
        pattern_payload = {
            "network": network
        }
        
        print(f"Sending pattern request to {pattern_url}")
        pattern_response = requests.post(pattern_url, json=pattern_payload)
        pattern_response.raise_for_status()
        result = pattern_response.json()
        
        print("Status: Success")
        print(f"Pattern type: {result.get('pattern_type')}")
        print(f"Geographic focus: {result.get('geographic_focus')}")
        print(f"Transmission intensity: {result.get('transmission_intensity')}")
        
        print("\nRecommended Interventions:")
        interventions = result.get('intervention_recommendations', {})
        print(f"Priority level: {interventions.get('priority_level')}")
        
        print("\nSurveillance recommendations:")
        for rec in interventions.get('surveillance', []):
            print(f"- {rec}")
            
        print("\nControl recommendations:")
        for rec in interventions.get('control', []):
            print(f"- {rec}")
        
        print("\nFull Response:")
        print_json(result)
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                print_json(e.response.json())
            except:
                print(e.response.text)

def main():
    """Run the test script."""
    parser = argparse.ArgumentParser(description='Test the APHIS Bird Flu Tracking System Genetic Analysis API')
    parser.add_argument('--host', default='localhost', help='API server host')
    parser.add_argument('--port', default='8000', help='API server port')
    
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}/api/v1"
    
    print(f"Testing API at {base_url}")
    
    # Test the sequence analysis endpoint
    test_sequence_analysis(base_url)
    
    # Test the transmission network endpoint
    test_transmission_network(base_url)
    
    # Test the transmission pattern endpoint
    test_transmission_pattern(base_url)
    
    print("\nTests completed.")

if __name__ == "__main__":
    main()