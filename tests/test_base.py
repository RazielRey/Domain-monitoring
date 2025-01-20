import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
import time
import logging 
import requests
import os
from conftest import test_logger as logging

class BaseTest(unittest.TestCase):
    def setUp(self):
        # Setup Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize webdriver with options
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Get base URL from environment variable or use default
        self.base_url = os.getenv('APP_URL', 'http://host.docker.internal:8080')
        logging.info(f"Using base URL: {self.base_url}")
        
        # Create a test user
        self.create_test_user()

    def tearDown(self):
        """Reset application state after each test"""
        try:
            # Handle any unexpected alerts
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.dismiss()
            logging.info("Alert dismissed during teardown.")
        except TimeoutException:
            logging.info("No alert present during teardown.")

        # Close the browser
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed.")

    def wait_for_element(self, by, value, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except UnexpectedAlertPresentException:
            logging.warning("Unexpected alert present. Handling it.")
            alert = self.driver.switch_to.alert
            logging.info(f"Alert text: {alert.text}")
            alert.accept()
            logging.info("Alert dismissed.")
            raise

    def handle_alerts(self):
        """Handle all pending alerts"""
        try:
            while True:
                logging.info("Checking for alerts...")
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                logging.info(f"Alert found with text: {alert.text}")
                alert.accept()
                logging.info("Alert dismissed.")
        except TimeoutException:
            logging.info("No more alerts present.")

    def create_test_user(self): 
        """Create a test user if it does not exist"""
        user_data = {
            "username": "testuser",
            "password": "Test123!"
        }
        try:
            response = requests.post(f"{self.base_url}/NewUser", data=user_data)
            if response.status_code == 200:
                logging.info("Test user created successfully")
            elif "already exists" in response.text:
                logging.info("Test user already exists")
            else:
                logging.error("Failed to create test user")
        except Exception as e:
            logging.error(f"Error creating test user: {e}")

    def wait_for_element_clickable(self, by, value, timeout=10):
        """Helper method to wait for element to be clickable"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except Exception as e:
            logging.error(f"Element not clickable: {by}={value}")
            raise e