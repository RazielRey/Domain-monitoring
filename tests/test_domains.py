from test_base import BaseTest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import os
from conftest import test_logger as logging

class DomainManagementTests(BaseTest):

    def setUp(self):
        """Setup for domain tests - login to the application"""
        super().setUp()
        logging.info("Starting domain tests setup")
        self.login()
        logging.info("Login successful")

    def login(self):
        """Helper method to login before tests"""
        logging.info("Performing login")
        self.driver.get(self.base_url)
        
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        username_field.send_keys("testuser")
        password_field.send_keys("Test123!")
        
        login_button = self.wait_for_element(By.ID, "login")
        login_button.click()
        
        # Wait for dashboard to load
        try:
            self.wait_for_element(By.CLASS_NAME, "dashboard-title", timeout=15)
            logging.info("Login successful")
        except TimeoutException:
            logging.error("Failed to login - dashboard not loaded")
            self.fail("Could not login before domain test")

    def test_add_domain(self):
        """Test adding a domain"""
        logging.info("Starting test to add a domain")
        
        # Find and fill the domain input
        try:
            domain_field = self.wait_for_element(By.ID, "domainInput")
            test_domain = "example.com"
            domain_field.send_keys(test_domain)
            logging.info(f"Domain entered: {test_domain}")

            # Click add button (using correct class name)
            add_button = self.wait_for_element(By.CLASS_NAME, "add-button")
            add_button.click()
            logging.info("Add button clicked")

            # Wait for AJAX request to complete
            time.sleep(2)

            # Verify domain in table
            table = self.wait_for_element(By.CLASS_NAME, "domains-table")
            domain_cells = table.find_elements(By.CLASS_NAME, "domain-name")
            
            domain_found = any(cell.text == test_domain for cell in domain_cells)
            if domain_found:
                logging.info("Domain successfully added to table")
                self.assertTrue(domain_found)
            else:
                logging.error("Added domain not found in table")
                self.fail("Domain not found in table after adding")

        except TimeoutException as e:
            logging.error(f"Failed to add domain: {e}")
            self.fail("Could not complete domain addition test")


    def test_delete_domain(self):
        """Test deleting a domain"""
        logging.info("Starting delete domain test")
        
        try:
            # Add a domain to delete
            test_domain = "delete-test.com"
            domain_field = self.wait_for_element(By.ID, "domainInput")
            domain_field.send_keys(test_domain)
            
            add_button = self.wait_for_element(By.CLASS_NAME, "add-button")
            add_button.click()
            logging.info(f"Added test domain: {test_domain}")
            
            # Wait for the domain to appear in the table
            table = self.wait_for_element(By.CLASS_NAME, "domains-table")
            domain_cells = table.find_elements(By.CLASS_NAME, "domain-name")
            domain_found = any(cell.text == test_domain for cell in domain_cells)
            if not domain_found:
                self.fail("Domain did not appear in the table after addition.")
            logging.info(f"Domain '{test_domain}' found in the table after addition.")
            
            # Click the delete button
            delete_button = self.wait_for_element(By.CLASS_NAME, "delete-button")
            delete_button.click()
            logging.info("Delete button clicked")

            # Handle the confirmation alert
            self.handle_alerts()

            # Search the table for the domain to ensure it's not there anymore
            table = self.wait_for_element(By.CLASS_NAME, "domains-table")
            domain_cells = table.find_elements(By.CLASS_NAME, "domain-name")
            domain_found = any(cell.text == test_domain for cell in domain_cells)
            
            if domain_found:
                logging.error(f"Domain '{test_domain}' still exists in the table after deletion.")
                self.fail("Domain was not removed from the table after deletion.")
            else:
                logging.info(f"Domain '{test_domain}' successfully removed from the table.")
                self.assertTrue(True)
                
        except TimeoutException as e:
            logging.error(f"Failed to delete domain: {e}")
            self.fail("Could not complete domain deletion test")

    def test_delete_domain(self):
        """Test deleting a domain"""
        logging.info("Starting delete domain test")
        
        try:
            # Add a domain to delete
            test_domain = "delete-test.com"
            domain_field = self.wait_for_element(By.ID, "domainInput")
            domain_field.send_keys(test_domain)
            
            add_button = self.wait_for_element(By.CLASS_NAME, "add-button")
            add_button.click()
            logging.info(f"Added test domain: {test_domain}")
            
            # Wait for the domain to appear in the table
            table = self.wait_for_element(By.CLASS_NAME, "domains-table")
            domain_cells = table.find_elements(By.CLASS_NAME, "domain-name")
            domain_found = any(cell.text.strip() == test_domain for cell in domain_cells)
            if not domain_found:
                self.fail("Domain did not appear in the table after addition.")
            logging.info(f"Domain '{test_domain}' found in the table after addition.")
            
            # Click the delete button
            delete_button = self.wait_for_element(By.CLASS_NAME, "delete-button")
            delete_button.click()
            logging.info("Delete button clicked")

            # Handle the confirmation alert
            self.handle_alerts()

            # Wait for the table to update
            WebDriverWait(self.driver, 10).until(
                lambda driver: all(cell.text.strip() != test_domain 
                                for cell in driver.find_elements(By.CLASS_NAME, "domain-name")),
                "Domain was not removed from the table after deletion."
            )
            logging.info(f"Domain '{test_domain}' successfully removed from the table.")

        except TimeoutException as e:
            logging.error(f"Failed to delete domain: {e}")
            self.fail("Could not complete domain deletion test")



    def test_refresh_domains(self):
        """Test refreshing domain statuses"""
        logging.info("Starting refresh domains test")
        
        try:
            # First add a test domain
            test_domain = "refresh-test.com"
            domain_field = self.wait_for_element(By.ID, "domainInput")
            domain_field.send_keys(test_domain)
            add_button = self.wait_for_element(By.CLASS_NAME, "add-button")
            add_button.click()
            logging.info(f"Added test domain: {test_domain}")
            
            time.sleep(2)  # Wait for domain to be added
            
            # Store initial status
            initial_status = None
            status_badge = self.wait_for_element(By.CLASS_NAME, "status-badge")
            initial_status = status_badge.text
            logging.info(f"Initial status: {initial_status}")

            # Click refresh
            refresh_button = self.wait_for_element(By.CLASS_NAME, "refresh-button")
            refresh_button.click()
            logging.info("Clicked refresh button")

            # Wait for spinner to appear and disappear
            spinner = self.wait_for_element(By.ID, "spinner")
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "spinner"))
            )
            logging.info("Refresh completed (spinner gone)")

            # Verify status was updated
            time.sleep(2)  # Give time for table to update
            new_status_badge = self.wait_for_element(By.CLASS_NAME, "status-badge")
            new_status = new_status_badge.text
            logging.info(f"New status: {new_status}")

            # Verify refresh occurred
            if new_status in ['OK', 'FAILED']:
                logging.info("Domain status refreshed successfully")
                self.assertTrue(True)
            else:
                logging.error("Invalid status after refresh")
                self.fail("Invalid status after refresh")
                
        except TimeoutException as e:
            logging.error(f"Failed to refresh domains: {e}")
            self.fail("Could not complete domain refresh test")
    
    
    def test_file_upload(self):
        """Test uploading domains from a file"""
        logging.info("Starting file upload test")
        
        try:
            # Create a test file with domains
            test_file_path = os.path.join(os.path.dirname(__file__), "test_domains.txt")
            test_domains = ["filetest1.com", "filetest2.com", "filetest3.com"]
            
            with open(test_file_path, "w") as f:
                f.write("\n".join(test_domains))
            logging.info("Created test domains file")
            
            # Upload the file
            file_input = self.wait_for_element(By.ID, "file-upload")
            file_input.send_keys(test_file_path)
            logging.info("Uploaded test file")

            #  Try to handle any alert that appears after file upload
            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                logging.info(f"Alert text: {alert.text}")
                alert.accept()
                logging.info("Alert dismissed")
            except TimeoutException:
                logging.warning("No alert appeared after file upload")

            # Add a delay to allow the table to update
            time.sleep(2)
            table = self.wait_for_element(By.CLASS_NAME, "domains-table")
            domain_cells = table.find_elements(By.CLASS_NAME, "domain-name")
            
            # Check if any of the uploaded domains are in the table
            domains_found = any(domain in cell.text for cell in domain_cells for domain in test_domains)
            
            if domains_found:
                logging.info("Successfully verified uploaded domains in table")
            else:
                logging.error("Could not find uploaded domains in table")
                self.fail("Uploaded domains not found in table")

        except Exception as e:
            logging.error(f"Unexpected error in file upload test: {e}")
            self.fail(f"Unexpected error: {str(e)}")
            
        finally:
            # Delete the test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                logging.info("Cleaned up test file in finally block")


if __name__ == "__main__":
    import unittest
    unittest.main()
