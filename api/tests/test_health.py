def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DxTx API"


def test_get_stats(client):
    """Test the stats endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_calls" in data
    assert "active_calls" in data
    assert "completed_calls" in data
    assert "failed_calls" in data
