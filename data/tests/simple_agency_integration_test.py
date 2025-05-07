"""
Simple test script for agency integration.

This simplified test verifies that imports are working correctly and
establishes the basic integration between agency agents and the
win-win calculation framework.
"""

import os
import sys
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SimpleAgencyIntegrationTest")

def test_ustda_agent_imports():
    """Test importing USTDA agent."""
    try:
        from ustda_agent import USTDAAgent, GovernancePolicy, ProgramActivity
        
        # Create an instance
        agent = USTDAAgent()
        
        # Test basic functionality
        policy_id = next(iter(agent.policies.keys()))
        policy = agent.policies[policy_id]
        
        logger.info(f"USTDA Agent created successfully with ID: {agent.agent_id}")
        logger.info(f"Default policy: {policy.title} ({policy.policy_type})")
        
        # Test certificate issuance
        cert = agent.issue_import_certificate(owner="test-owner", value=50000)
        logger.info(f"Certificate issued: {cert.id} for value {cert.value}")
        
        return {
            "success": True, 
            "agent_id": agent.agent_id,
            "capabilities": agent.capabilities,
            "certificate_issued": cert.id
        }
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error testing USTDA agent: {str(e)}")
        return {"success": False, "error": str(e)}

def test_usitc_agent_imports():
    """Test importing USITC agent."""
    try:
        from usitc_agent import USITCAgent, EconomicModel, TradeImpactAssessment
        
        # Create an instance
        agent = USITCAgent()
        
        # Test basic functionality
        model_id = next(iter(agent.models.keys()))
        model = agent.models[model_id]
        
        logger.info(f"USITC Agent created successfully with ID: {agent.agent_id}")
        logger.info(f"Default model: {model.title} ({model.model_type})")
        
        # Test analysis functionality
        analysis = agent.analyze_trade_program("test-program-1234")
        logger.info(f"Analysis completed with recommendation: {analysis['policy_recommendation']}")
        
        return {
            "success": True, 
            "agent_id": agent.agent_id,
            "capabilities": agent.capabilities,
            "analysis_performed": analysis['assessment_id']
        }
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error testing USITC agent: {str(e)}")
        return {"success": False, "error": str(e)}

def test_trade_base_imports():
    """Test importing trade base components."""
    try:
        from trade_base import TradeFlow, DealSide, ImportCertificate, ComplianceCheck
        
        # Create basic certificate
        cert = ImportCertificate(
            id="IC-TEST-12345",
            owner="test-organization",
            value=100000.0,
            issued_date="2023-06-01T00:00:00",
            expiry_date="2023-12-01T00:00:00",
            issuing_authority="TEST-AUTHORITY",
            status="active",
            history=[{
                "timestamp": "2023-06-01T00:00:00",
                "action": "issued",
                "value": 100000.0
            }]
        )
        
        logger.info(f"Created certificate: {cert.id}")
        
        return {
            "success": True,
            "certificate_id": cert.id,
            "certificate_value": cert.value
        }
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error testing trade base components: {str(e)}")
        return {"success": False, "error": str(e)}

def run_all_tests():
    """Run all tests and report results."""
    results = {}
    
    # Test 1: Trade Base Imports
    logger.info("=== Testing Trade Base Imports ===")
    results["trade_base"] = test_trade_base_imports()
    
    # Test 2: USTDA Agent
    logger.info("\n=== Testing USTDA Agent ===")
    results["ustda_agent"] = test_ustda_agent_imports()
    
    # Test 3: USITC Agent
    logger.info("\n=== Testing USITC Agent ===")
    results["usitc_agent"] = test_usitc_agent_imports()
    
    # Verify integration capabilities
    integration_possible = all(
        result.get("success", False) for result in results.values()
    )
    
    logger.info("\n=== Summary ===")
    for test_name, result in results.items():
        status = "PASSED" if result.get("success", False) else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nComplete integration possible: {integration_possible}")
    
    return {
        "results": results,
        "integration_possible": integration_possible
    }

if __name__ == "__main__":
    test_results = run_all_tests()
    print("\nTests completed.")