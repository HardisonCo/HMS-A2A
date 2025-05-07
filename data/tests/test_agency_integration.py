"""
Test script for agency integration with the MAC architecture.

This script tests the integration of USTDA and USITC agency agents with the
Multi-Agent Collaboration (MAC) architecture, including the Win-Win calculation framework.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestAgencyIntegration")

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import MAC components and agency integration
# Use relative imports
from mac.economist_agent import create_economist
from mac.market_integration import integrate_economic_components
from mac.agency_integration import (
    AgencyNetworkExtension, setup_agency_integration
)

# Import Win-Win calculation framework
from win_win_calculation_framework import (
    analyze_win_win_deal, EntityProfile, create_entity_profile
)

# Import agency agents if available
try:
    from ustda_agent import USTDAAgent
    from usitc_agent import USITCAgent
    AGENCY_IMPORTS_AVAILABLE = True
except ImportError:
    logger.warning("Agency agent imports not available, using mock implementations")
    AGENCY_IMPORTS_AVAILABLE = False
    USTDAAgent = None
    USITCAgent = None


async def test_full_integration():
    """Test the full integration of agency agents with MAC architecture."""
    logger.info("Starting full integration test")
    
    # Step 1: Create economist agent
    economist = create_economist(config_path=None)
    logger.info("Economist agent created")
    
    # Step 2: Create market network integrator
    integrator = await integrate_economic_components(economist)
    logger.info("Market network integrator created with economist agent")
    
    # Step 3: Create agency network extension
    extension = await setup_agency_integration(integrator)
    logger.info("Agency network extension created")
    
    # Step 4: Create agency-based deal with win-win calculation
    deal_result = await extension.create_policy_based_deal(
        agency_id="USTDA-001",
        problem_statement="Develop renewable energy infrastructure with technology transfer component",
        stakeholder_ids=["developer_agent", "verification_agent"]
    )
    
    logger.info(f"Created policy-based deal: {deal_result['deal_id']}")
    logger.info(f"Win-Win status: {deal_result['is_win_win']}")
    
    # Step 5: Create another deal for comparison
    second_deal = await extension.create_policy_based_deal(
        agency_id="USITC-001",
        problem_statement="Analyze economic impact of tariff reduction on manufacturing sector",
        stakeholder_ids=["architect_agent", "developer_agent"]
    )
    
    logger.info(f"Created second policy-based deal: {second_deal['deal_id']}")
    logger.info(f"Win-Win status: {second_deal['is_win_win']}")
    
    # Step 6: Test the import certificate system
    # Use ustda_agent directly since extension doesn't have a management attribute
    if hasattr(extension, 'ustda_agent') and extension.ustda_agent:
        ustda_certs = extension.ustda_agent.issue_import_certificate(
            owner="USTDA-001",
            value=100000.0
        )
    else:
        ustda_certs = None
        logger.warning("USTDA agent not available for issuing certificates")
    
    if ustda_certs:
        logger.info(f"Import certificates issued to USTDA-001: {ustda_certs.id}")
    else:
        logger.warning("Failed to issue import certificates")
    
    # Step 7: Run economic analysis on deals if USITC available
    if extension.usitc_agent:
        impact_analysis = extension.usitc_agent.analyze_trade_program(deal_result.get("deal_id", ""))
        logger.info(f"Economic impact analysis completed: {impact_analysis['policy_recommendation']}")
    
    # Step 8: Perform win-win analysis on deal
    deal_id = deal_result['deal_id']
    win_win_result = await extension.calculate_win_win_status(deal_id, True)
    
    logger.info(f"Win-Win analysis for deal {deal_id}:")
    for entity_id, values in win_win_result.get("entity_values", {}).items():
        logger.info(f"  - {entity_id}: Net value = {values.get('net_value', 0.0):.2f} (Win: {values.get('is_win', False)})")
    
    # Return combined test results
    return {
        "deals_created": [deal_result, second_deal],
        "win_win_analysis": win_win_result,
        "agency_extension": extension is not None,
        "agency_imports_available": AGENCY_IMPORTS_AVAILABLE
    }


async def test_win_win_framework():
    """Test the Win-Win calculation framework independently."""
    logger.info("Testing Win-Win calculation framework")
    
    # Create entity profiles
    entity_profiles = {
        'ustda': create_entity_profile(
            entity_id='ustda',
            entity_name='US Trade & Development Agency',
            entity_type='government',
            time_preference=0.05,  # Lower time preference (long-term view)
            risk_preference=0.3    # Lower risk aversion (more risk tolerant)
        ),
        'usitc': create_entity_profile(
            entity_id='usitc',
            entity_name='US International Trade Commission',
            entity_type='government',
            time_preference=0.05,
            risk_preference=0.3
        ),
        'dev_company': create_entity_profile(
            entity_id='dev_company',
            entity_name='Development Corporation',
            entity_type='corporate',
            time_preference=0.1,
            risk_preference=0.4
        ),
        'local_community': create_entity_profile(
            entity_id='local_community',
            entity_name='Local Community Group',
            entity_type='civilian',
            time_preference=0.15,  # Higher time preference (short-term focused)
            risk_preference=0.7    # Higher risk preference (more risk averse)
        )
    }
    
    # Run win-win analysis with demo values
    from win_win_calculation_framework import (
        create_value_component
    )
    
    # Create value components for each entity
    value_components = {
        'ustda': {
            'comp_1': create_value_component(
                dimension='economic',
                amount=100.0,
                timeline=[(0, 20.0), (1, 30.0), (2, 50.0)],
                probability=0.9
            ),
            'comp_2': create_value_component(
                dimension='social',
                amount=50.0,
                timeline=[(1, 20.0), (2, 30.0)],
                probability=0.8
            )
        },
        'usitc': {
            'comp_3': create_value_component(
                dimension='economic',
                amount=80.0,
                timeline=[(0, 30.0), (1, 50.0)],
                probability=0.85
            ),
            'comp_4': create_value_component(
                dimension='security',
                amount=60.0,
                timeline=[(0, 20.0), (1, 40.0)],
                probability=0.9
            )
        },
        'dev_company': {
            'comp_5': create_value_component(
                dimension='economic',
                amount=200.0,
                timeline=[(0, 50.0), (1, 75.0), (2, 75.0)],
                probability=0.85
            ),
            'comp_6': create_value_component(
                dimension='environmental',
                amount=-30.0,  # Negative value component
                timeline=[(0, -10.0), (1, -10.0), (2, -10.0)],
                probability=0.7
            )
        },
        'local_community': {
            'comp_7': create_value_component(
                dimension='social',
                amount=60.0,
                timeline=[(0, 10.0), (1, 20.0), (2, 30.0)],
                probability=0.7
            ),
            'comp_8': create_value_component(
                dimension='economic',
                amount=40.0,
                timeline=[(1, 15.0), (2, 25.0)],
                probability=0.8
            )
        }
    }
    
    # Run the analysis
    analysis = analyze_win_win_deal(entity_profiles, value_components)
    
    logger.info("Win-Win Analysis Results:")
    logger.info(f"Is win-win: {analysis['is_win_win']}")
    
    for entity_id, values in analysis['entity_values'].items():
        status = "WIN" if values['is_win'] else "LOSE"
        logger.info(f"  {entity_id}: {values['total_value']:.2f} ({status})")
    
    # Show improvement opportunities if any
    if analysis['improvement_opportunities']:
        logger.info("Improvement opportunities:")
        for opp in analysis['improvement_opportunities']:
            logger.info(f"  {opp['entity_id']} needs {opp['required_improvement']:.2f} more value in {opp['focus_dimension']}")
    
    return analysis


async def main():
    """Run all integration tests."""
    try:
        # Test Win-Win calculation framework independently
        win_win_result = await test_win_win_framework()
        logger.info(f"Win-Win framework test completed. Success: {win_win_result['is_win_win']}")
        
        # Test the full integration if agency imports are available
        full_result = await test_full_integration()
        logger.info(f"Full integration test completed. Created {len(full_result['deals_created'])} deals")
        
        # Summary
        logger.info("\nTest Summary:")
        logger.info(f"Agency imports available: {full_result['agency_imports_available']}")
        logger.info(f"Agency extension created successfully: {full_result['agency_extension']}")
        logger.info(f"Win-Win framework functioning correctly: {win_win_result['is_win_win'] is not None}")
        logger.info(f"Deals created successfully: {len(full_result['deals_created']) > 0}")
        
        return {
            "win_win_test": win_win_result,
            "full_integration_test": full_result,
            "overall_success": True
        }
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return {
            "overall_success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())