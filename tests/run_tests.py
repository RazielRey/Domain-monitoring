import unittest
from test_auth import AuthenticationTests
from test_domains import DomainManagementTests
from test_scheduler import SchedulerTests
from conftest import test_logger as logging

def run_selected_tests():
    """Run only selected core tests"""
    # Create test suite
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Add only specific test methods with correct names
    suite.addTest(AuthenticationTests('test_registration_success') ) # Changed from test_registration
    suite.addTest(AuthenticationTests('test_login_success'))      # Changed from test_login
    suite.addTest(DomainManagementTests('test_add_domain'))
    suite.addTest(DomainManagementTests('test_file_upload'))
    suite.addTest(SchedulerTests('test_hourly_schedule'))
    
    # Run the tests
    logging.info("Starting core test suite")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log results
    logging.info(f"Tests run: {result.testsRun}")
    logging.info(f"Tests failed: {len(result.failures)}")
    logging.info(f"Tests with errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_selected_tests()
    exit(0 if success else 1)