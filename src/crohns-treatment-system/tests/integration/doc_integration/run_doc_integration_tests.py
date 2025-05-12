#!/usr/bin/env python
"""
Test runner for HMS integration system tests
"""

import os
import sys
import unittest
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_tests():
    """
    Run all doc integration tests and return the test result
    """
    logger.info("Starting HMS integration system tests...")
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover and run tests
    test_suite = unittest.defaultTestLoader.discover(
        start_dir=current_dir,
        pattern='test_*.py'
    )
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(test_suite)
    
    # Log test results
    logger.info("Tests completed.")
    logger.info("Ran %d tests", result.testsRun)
    
    if result.wasSuccessful():
        logger.info("All tests PASSED!")
    else:
        logger.error("Tests FAILED: %d errors, %d failures", 
                  len(result.errors), len(result.failures))
        
        if result.errors:
            logger.error("Errors:")
            for test, error in result.errors:
                logger.error("%s: %s", test, error)
                
        if result.failures:
            logger.error("Failures:")
            for test, failure in result.failures:
                logger.error("%s: %s", test, failure)
    
    return result

if __name__ == '__main__':
    result = run_tests()
    
    # Exit with appropriate code for CI/CD pipelines
    sys.exit(0 if result.wasSuccessful() else 1)