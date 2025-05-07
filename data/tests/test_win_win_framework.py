"""
Simple test for the Win-Win calculation framework.
"""

import logging
from win_win_calculation_framework import (
    analyze_win_win_deal, EntityProfile, create_entity_profile,
    create_value_component
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestWinWinFramework")

def test_win_win_framework():
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

if __name__ == "__main__":
    result = test_win_win_framework()
    print("\nValue distribution:")
    for entity_id, value in result['value_distribution'].items():
        print(f"  {entity_id}: {value:.2%}")
    
    print(f"\nValue inequality (Gini): {result['value_inequality_gini']:.2f}")
    
    print("\nTest completed successfully")