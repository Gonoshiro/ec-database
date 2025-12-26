import pytest
from src.api.auth import auth
from src.api.makeshop_client import client

def test_api_authentication():
    """API認証テスト"""
    assert auth.test_connection() == True

@pytest.mark.skipif(not auth.api_token, reason="API token not configured")
def test_search_members():
    """会員検索APIテスト"""
    result = client.search_members(page=1, limit=10)
    assert 'members' in result
    assert isinstance(result['members'], list)