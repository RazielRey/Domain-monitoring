from test_base import BaseTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from conftest import test_logger as logging

class SchedulerTests(BaseTest):
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
        """Helper to add a test domain"""
        try:
            test_domain = "scheduler-test.com"
            domain_field = self.wait_for_element(By.ID, "domainInput")  

            domain_field.send_keys(test_domain)
            add_button = self.wait_for_element(By.CLASS_NAME, "add-button")
            add_button.click()
            time.sleep(2)
            logging.info(f"Domain entered: {test_domain}")

        except TimeoutException as e:
            logging.error(f"Failed to add domain: {e}")
            raise e
        
    def test_hourly_schedule(self):
        """Test setting up hourly checks"""
        logging.info("Starting hourly schedule test")
        
        try:
            # Add domain
            domain_field = self.wait_for_element(By.ID, "domainInput")
            test_domain = "scheduler-test.com"
            domain_field.send_keys(test_domain)
            logging.info(f"Domain entered: {test_domain}")
            
            add_button = self.wait_for_element(By.CLASS_NAME, "add-button")
            add_button.click()
            time.sleep(2)  # Wait for domain to be added

            # Find the radio button's label and click it
            schedule_label = self.wait_for_element(By.CSS_SELECTOR, "label.schedule-label")
            hourly_radio = schedule_label.find_element(By.CSS_SELECTOR, "input[value='hourly']")
            self.driver.execute_script("arguments[0].click();", hourly_radio)
            logging.info("Selected hourly schedule")

            time.sleep(1)  # Wait for UI to update

            # Click start schedule
            start_button = self.wait_for_element(By.ID, "startSchedule")
            self.driver.execute_script("arguments[0].click();", start_button)
            logging.info("Started schedule")
            
            time.sleep(2)  # Wait for schedule to start

            # Verify schedule
            next_run = self.wait_for_element(By.ID, "nextRunTime")
            actual_text = next_run.text
            logging.info(f"Next run text: {actual_text}")
            
            # Check schedule started
            self.assertTrue(
                "Next check:" in actual_text and "Not scheduled" not in actual_text,
                f"Schedule not started properly. Got text: {actual_text}"
            )
            logging.info("Schedule verified running")
                
        except Exception as e:
            logging.error(f"Failed to set hourly schedule: {e}")
            self.fail("Could not complete hourly schedule test")


    def test_stop_schedule(self):
        """Test stopping a schedule"""
        logging.info("Starting stop schedule test")
        
        try:
            # Start a schedule first
            self.test_hourly_schedule()
            
            # Click stop button
            stop_button = self.wait_for_element(By.ID, "stopSchedule")
            stop_button.click()
            logging.info("Clicked stop button")

            # Wait for the "Not scheduled" text to appear
            WebDriverWait(self.driver, 20).until(
                lambda driver: "Not scheduled" in driver.find_element(By.ID, "nextRunTime").text,
                "The 'Not scheduled' status did not appear in time."
            )

            next_run = self.wait_for_element(By.ID, "nextRunTime")
            logging.info(f"Final nextRunTime text: {next_run.text}")
            self.assertIn("Not scheduled", next_run.text)
            logging.info("Schedule verified stopped")
                
        except TimeoutException as e:
            logging.error(f"Failed to stop schedule: {e}")
            self.fail("Could not complete stop schedule test")


    def test_daily_schedule(self):
        """Test setting up daily checks"""
        logging.info("Starting daily schedule test")
        
        try:
            # Add a domain first
            self.test_add_domain()
            
            # Select daily radio button
            daily_radio = self.wait_for_element(By.CSS_SELECTOR, "input[value='daily']")
            daily_radio.click()
            logging.info("Selected daily schedule")

            # Set a time (e.g., 13:00)
            time_input = self.wait_for_element(By.ID, "dailyTime")
            time_input.clear()
            time_input.send_keys("13:00")
            logging.info(f"Set daily time to {time_input.get_attribute('value')}")

            # Click start schedule
            start_button = self.wait_for_element(By.ID, "startSchedule")
            start_button.click()
            logging.info("Started daily schedule")

            # Wait for the next run time to update
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda d: "Not scheduled" not in self.wait_for_element(By.ID, "nextRunTime").text
                )
                next_run = self.wait_for_element(By.ID, "nextRunTime")
                logging.info(f"Next check updated: {next_run.text}")
                self.assertNotIn("Not scheduled", next_run.text)
            except TimeoutException:
                logging.error("Next check did not update in time.")
                self.fail("Failed to verify daily schedule start.")

        except TimeoutException as e:
            logging.error(f"Failed to set daily schedule: {e}")
            self.fail("Could not complete daily schedule test")
