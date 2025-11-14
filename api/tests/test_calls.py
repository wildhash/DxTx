def test_list_calls_empty(client):
    """Test listing calls when none exist"""
    response = client.get("/calls")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_nonexistent_call(client):
    """Test getting a call that doesn't exist"""
    response = client.get("/calls/nonexistent-id")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
