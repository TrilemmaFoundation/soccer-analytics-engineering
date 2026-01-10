"""Pytest configuration and shared fixtures for database tests."""
import pytest
import duckdb
import os


@pytest.fixture(scope="session")
def db_connection():
    """Create a DuckDB connection to the stats.duckdb database."""
    db_path = "stats.duckdb"
    
    if not os.path.exists(db_path):
        pytest.skip(f"Database file {db_path} not found. Run build.py first.")
    
    db = duckdb.connect(db_path)
    yield db
    db.close()


@pytest.fixture(scope="function")
def cursor(db_connection):
    """Create a cursor for executing queries."""
    return db_connection.cursor()

