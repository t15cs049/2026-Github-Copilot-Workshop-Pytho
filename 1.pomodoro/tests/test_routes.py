import pytest
from app import create_app

def test_create_app():
    app = create_app()
    assert app is not None
    assert app.testing is False

def test_index_route():
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'ポモドーロタイマー' in response.data
