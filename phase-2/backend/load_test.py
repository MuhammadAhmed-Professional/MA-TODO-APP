"""
Load Testing Script for Phase II Todo API

Tests backend performance with 500 concurrent users.
Measures p95 latency, error rates, and throughput.

Usage:
    locust -f load_test.py -u 500 -r 50 --headless -t 5m -H http://localhost:8000 --html load-test-results.html
"""

import random
import uuid
from locust import HttpUser, task, between, events
from locust.exception import ResponseError


class TodoUser(HttpUser):
    """
    Simulates a user performing typical todo application operations.

    User behavior:
    - Login to get authentication token
    - List tasks (most frequent operation)
    - Create new tasks
    - Toggle task completion
    - Update existing tasks
    - Delete tasks

    Wait time: 1-3 seconds between requests (realistic user behavior)
    """

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_email = None
        self.user_password = None
        self.created_task_ids = []

    def on_start(self):
        """
        Called when a simulated user starts.
        Creates a unique test user and logs in to get authentication token.
        """
        # Generate unique user credentials
        random_id = random.randint(1, 100000)
        self.user_email = f"loadtest_user_{random_id}@example.com"
        self.user_password = "LoadTest123!"

        # Sign up new user
        signup_response = self.client.post(
            "/api/auth/signup",
            json={
                "name": f"Load Test User {random_id}",
                "email": self.user_email,
                "password": self.user_password,
            },
            name="POST /api/auth/signup",
        )

        if signup_response.status_code != 201:
            # User might already exist, try logging in instead
            login_response = self.client.post(
                "/api/auth/login",
                json={
                    "email": self.user_email,
                    "password": self.user_password,
                },
                name="POST /api/auth/login",
            )

            if login_response.status_code != 200:
                raise ResponseError(f"Failed to authenticate: {login_response.status_code}")

        # Auth token is now stored in HttpOnly cookie, automatically included in subsequent requests

    @task(5)
    def list_tasks(self):
        """
        List all tasks for the authenticated user.
        This is the most frequent operation (weight=5).
        """
        response = self.client.get("/api/tasks/", name="GET /api/tasks")

        if response.status_code == 200:
            tasks = response.json().get("tasks", [])
            # Store task IDs for use in other operations
            if tasks:
                self.created_task_ids = [task["id"] for task in tasks]

    @task(3)
    def create_task(self):
        """
        Create a new task.
        Moderately frequent operation (weight=3).
        """
        task_title = f"Load Test Task {uuid.uuid4().hex[:8]}"
        task_description = f"Created during load test at {random.randint(1, 1000000)}"

        response = self.client.post(
            "/api/tasks/",
            json={
                "title": task_title,
                "description": task_description,
            },
            name="POST /api/tasks",
        )

        if response.status_code == 201:
            task_data = response.json()
            self.created_task_ids.append(task_data["id"])

    @task(2)
    def toggle_task_complete(self):
        """
        Toggle a task's completion status.
        Less frequent operation (weight=2).
        """
        if not self.created_task_ids:
            # No tasks to toggle, skip this operation
            return

        task_id = random.choice(self.created_task_ids)

        self.client.patch(
            f"/api/tasks/{task_id}/complete",
            name="PATCH /api/tasks/{id}/complete",
        )

    @task(1)
    def get_single_task(self):
        """
        Get details of a single task.
        Least frequent operation (weight=1).
        """
        if not self.created_task_ids:
            # No tasks to retrieve, skip this operation
            return

        task_id = random.choice(self.created_task_ids)

        self.client.get(
            f"/api/tasks/{task_id}",
            name="GET /api/tasks/{id}",
        )

    @task(1)
    def update_task(self):
        """
        Update a task's title and description.
        Least frequent operation (weight=1).
        """
        if not self.created_task_ids:
            # No tasks to update, skip this operation
            return

        task_id = random.choice(self.created_task_ids)

        self.client.put(
            f"/api/tasks/{task_id}",
            json={
                "title": f"Updated Task {uuid.uuid4().hex[:8]}",
                "description": "Updated during load test",
            },
            name="PUT /api/tasks/{id}",
        )

    @task(1)
    def delete_task(self):
        """
        Delete a task.
        Least frequent operation (weight=1).
        """
        if not self.created_task_ids:
            # No tasks to delete, skip this operation
            return

        task_id = random.choice(self.created_task_ids)

        response = self.client.delete(
            f"/api/tasks/{task_id}",
            name="DELETE /api/tasks/{id}",
        )

        if response.status_code == 204:
            # Remove deleted task from list
            self.created_task_ids.remove(task_id)


# Event handlers for custom metrics and reporting

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test configuration when load test starts."""
    print("=" * 80)
    print("Load Test Starting")
    print(f"Target Host: {environment.host}")
    print(f"Number of Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print test summary when load test completes."""
    stats = environment.stats
    print("=" * 80)
    print("Load Test Complete")
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Failure Rate: {(stats.total.num_failures / stats.total.num_requests * 100) if stats.total.num_requests > 0 else 0:.2f}%")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Median Response Time (p50): {stats.total.median_response_time:.2f}ms")
    print(f"95th Percentile Response Time (p95): {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"99th Percentile Response Time (p99): {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests Per Second: {stats.total.total_rps:.2f}")
    print("=" * 80)

    # Validation checks
    failure_rate = (stats.total.num_failures / stats.total.num_requests * 100) if stats.total.num_requests > 0 else 0
    p95_latency = stats.total.get_response_time_percentile(0.95)

    print("\nValidation Results:")
    print(f"{'✅' if failure_rate < 1 else '❌'} Error Rate: {failure_rate:.2f}% (Target: <1%)")
    print(f"{'✅' if p95_latency < 200 else '❌'} p95 Latency: {p95_latency:.2f}ms (Target: <200ms)")
    print("=" * 80)
