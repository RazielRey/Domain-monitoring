from test_base import BaseTest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from conftest import test_logger as logging
class AuthenticationTests(BaseTest):
    def test_registration_success(self):
        """Test user registration"""
        self.driver.get(self.base_url)
        
        logging.info("Navigating to registration page")
        register_button = self.wait_for_element(By.ID, "register", timeout=15)
        register_button.click()
        logging.info("Register button clicked")

        # Fill in user details
        username = f"testuser_{int(time.time())}"  # Dynamic username
        password = "Test123!"
        
        username_field = self.wait_for_element(By.ID, "username", timeout=15)
        username_field.send_keys(username)
        logging.info("Username entered")
        
        password_field = self.wait_for_element(By.ID, "password", timeout=15)
        password_field.send_keys(password)
        logging.info("Password entered")
        
        confirm_field = self.wait_for_element(By.ID, "confirm-password", timeout=15)
        confirm_field.send_keys(password)
        logging.info("Confirm password entered")
        
        # Submit the form
        submit_button = self.wait_for_element(By.ID, "register", timeout=15)
        time.sleep(1)  # Ensure form is ready
        self.driver.execute_script("arguments[0].click();", submit_button)
        logging.info("Register button clicked")
        
        # Check for success message
        try:
            success_message = self.wait_for_element(By.ID, "positive", timeout=15)
            if success_message.text == "You have successfully registered. Please sign in.":
                logging.info("User registered successfully")
            else:
                logging.error("Unexpected success message")
                self.fail("Unexpected success message")
        except TimeoutException as e:
            logging.error(f"Success message not found: {e}")
            self.fail("Registration success message not found or delayed.")



    def test_login_success(self):
        """Test user login"""
        logging.info("Starting login test")

        # Navigate to the base URL
        logging.info("Navigating to the base URL")
        self.driver.get(self.base_url)
        logging.info("Page loaded")

        # Locate username and password fields
        logging.info("Locating username field")
        username_field = self.wait_for_element(By.ID, "username")
        logging.info("Username field located")

        logging.info("Locating password field")
        password_field = self.wait_for_element(By.ID, "password")
        logging.info("Password field located")

        # Fill in login details
        logging.info("Entering username")
        username_field.send_keys("testuser")  # Pre-existing test user
        logging.info("Entering password")
        password_field.send_keys("Test123!")

        # Locate and click the login button
        logging.info("Locating login button")
        login_button = self.wait_for_element(By.ID, "login")
        logging.info("Login button located")

        logging.info("Clicking login button")
        login_button.click()

        # Verify that the dashboard page loads
        logging.info("Verifying dashboard page load")
        try:
            dashboard_title = self.wait_for_element(By.CLASS_NAME, "dashboard-title", timeout=15)
            logging.info(f"Dashboard title located: {dashboard_title.text}")
            self.assertIn("Domain Management Dashboard", dashboard_title.text)
            logging.info("Dashboard page loaded successfully")
        except TimeoutException:
            logging.error("Dashboard page did not load")
            self.fail("Dashboard not loaded after login.")

    def test_logout(self):
        """Test user logout"""
        logging.info("Starting logout test")

        # Log in first
        logging.info("Logging in before performing logout")
        self.test_login_success()
        logging.info("Login successful, proceeding to logout")

        # Locate and click the logout button
        logging.info("Locating logout button")
        logout_button = self.wait_for_element(By.CLASS_NAME, "logout-button")
        logging.info("Logout button located")

        logging.info("Clicking logout button")
        logout_button.click()

        # Verify redirection to the login page
        logging.info("Verifying redirection to the login page")
        try:
            login_button = self.wait_for_element(By.ID, "login", timeout=15)
            logging.info("Login page loaded successfully")
            self.assertIsNotNone(login_button)
        except TimeoutException:
            logging.error("Redirection to login page failed")
            self.fail("Logout did not redirect to login page.")
