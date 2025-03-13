from locust import HttpUser, task, between, events
import random
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DomainMonitorUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """Setup before starting tasks"""
        self.username = f"testuser_{int(time.time())}_{random.randint(1000, 9999)}"
        self.password = "Test123!"
        
        # Login with generated credentials
        self.login()
        
        # Prepare test domains
        self.single_domain = "google.com"
        self.bulk_domains = [f"test-domain-{i}.com" for i in range(100)]

    def login(self):
        """Login with credentials"""
        with self.client.post("/api/login",
            json={
                "username": self.username,
                "password": self.password
            },
            catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Login failed: {response.status_code}")
                logger.error(f"Login failed for user {self.username}")

    # @task(1)
    # def check_single_domain(self):
    #     """Check a single domain"""
    #     start_time = time.time()
        
    #     with self.client.post("/api/check-domains",
    #         json={
    #             "domains": [self.single_domain],
    #             "username": self.username
    #         },
    #         name="/api/check-domains (single domain)",
    #         catch_response=True) as response:
            
    #         duration = time.time() - start_time
            
    #         if response.status_code != 200:
    #             response.failure(f"Single domain check failed: {response.status_code}")
    #             logger.error(f"Single domain check failed for user {self.username}")
            
    #         # Track response time for degradation monitoring
    #         if duration > 5:  # 5 second threshold
    #             logger.warning(f"Performance degradation detected: {duration}s for single domain")

    @task(4)
    def check_bulk_domains(self):
        """Check 100 domains at once"""
        start_time = time.time()
        
        with self.client.post("/api/check-domains",
            json={
                "domains": self.bulk_domains,
                "username": self.username
            },
            name="/api/check-domains (bulk - 100 domains)",
            catch_response=True) as response:
            
            duration = time.time() - start_time
            
            if response.status_code != 200:
                response.failure(f"Bulk domain check failed: {response.status_code}")
                logger.error(f"Bulk domain check failed for user {self.username}")
            
            # Track response time for degradation monitoring
            if duration > 10:  # 10 second threshold for bulk
                logger.warning(f"Performance degradation detected: {duration}s for bulk domains")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("Performance test is starting")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logger.info("Performance test is ending")