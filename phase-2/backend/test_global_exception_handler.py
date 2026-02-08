"""
Quick test to verify global exception handler works
"""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Test that a deliberately raised exception gets caught
def test_global_exception_handler():
    """Test that unhandled exceptions return 500 with error_id"""
    # Create a test endpoint that raises an exception
    @app.get("/test/error")
    async def test_error_endpoint():
        raise ValueError("This is a test error")

    response = client.get("/test/error")

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Internal server error"
    assert "error_id" in data
    assert len(data["error_id"]) == 36  # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

    print(f"✓ Global exception handler test passed!")
    print(f"  Response: {data}")

if __name__ == "__main__":
    test_global_exception_handler()
