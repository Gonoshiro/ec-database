import pytest
from src.database.connection import db

def test_database_connection():
    """データベース接続テスト"""
    assert db.test_connection() == True

def test_database_schema():
    """テーブル存在確認"""
    session = db.get_session()
    try:
        from sqlalchemy import text
        result = session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'dbo'
        """))
        tables = [row[0] for row in result]
        assert 'members' in tables
        assert 'orders' in tables
        assert 'order_details' in tables
        assert 'products' in tables
    finally:
        session.close()