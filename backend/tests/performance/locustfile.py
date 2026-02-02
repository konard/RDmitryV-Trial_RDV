"""Locust performance tests for the API."""

from locust import HttpUser, task, between
import json


class MarketingResearchUser(HttpUser):
    """
    Simulated user performing marketing research operations.

    Usage:
        locust -f tests/performance/locustfile.py --host=http://localhost:8000
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts."""
        # Login to get authentication token
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(3)
    def view_homepage(self):
        """View the homepage."""
        self.client.get("/")

    @task(2)
    def health_check(self):
        """Check API health."""
        self.client.get("/health")

    @task(5)
    def list_researches(self):
        """List user's researches."""
        if self.headers:
            self.client.get(
                "/api/v1/research/",
                headers=self.headers
            )

    @task(3)
    def create_research(self):
        """Create a new research."""
        if self.headers:
            research_data = {
                "title": "Performance Test Research",
                "product_description": "Мобильное приложение для доставки еды",
                "industry": "Общественное питание",
                "region": "Москва",
                "research_type": "market"
            }

            response = self.client.post(
                "/api/v1/research/",
                json=research_data,
                headers=self.headers
            )

            # Store research ID for later use
            if response.status_code == 201:
                data = response.json()
                self.research_id = data.get("id")

    @task(4)
    def view_research(self):
        """View a specific research."""
        if hasattr(self, 'research_id') and self.headers:
            self.client.get(
                f"/api/v1/research/{self.research_id}",
                headers=self.headers
            )

    @task(1)
    def analyze_research(self):
        """Analyze a research (intensive operation)."""
        if hasattr(self, 'research_id') and self.headers:
            self.client.post(
                f"/api/v1/research/{self.research_id}/analyze",
                headers=self.headers,
                timeout=60  # Analysis may take longer
            )


class AdminUser(HttpUser):
    """Simulated admin user."""

    wait_time = between(2, 5)

    def on_start(self):
        """Login as admin."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "adminpassword"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(2)
    def view_all_researches(self):
        """View all researches (admin)."""
        if self.headers:
            self.client.get(
                "/api/v1/research/?limit=100",
                headers=self.headers
            )

    @task(1)
    def generate_report(self):
        """Generate a report."""
        if hasattr(self, 'research_id') and self.headers:
            self.client.post(
                f"/api/v1/reports/generate",
                json={
                    "research_id": self.research_id,
                    "format": "pdf"
                },
                headers=self.headers,
                timeout=120
            )


class QuickTestUser(HttpUser):
    """
    Quick test user for smoke testing.

    Usage for quick load test:
        locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 1m
    """

    wait_time = between(0.5, 1.5)

    @task
    def quick_health_check(self):
        """Quick health check."""
        self.client.get("/health")

    @task
    def quick_root_check(self):
        """Quick root endpoint check."""
        self.client.get("/")
