"""Tests for ETL infrastructure resilience and fault tolerance."""
import pytest
import os
import json
from schema.loaders import _get_valid_json_files

class TestJSONValidation:
    """Test the robust JSON loading utility."""

    def test_filter_malformed_json(self, tmp_path):
        """Test that _get_valid_json_files correctly ignores malformed JSON files."""
        # Create a valid JSON file
        valid_file = tmp_path / "valid.json"
        valid_file.write_text('{"key": "value"}')
        
        # Create a malformed JSON file
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text('{"key": "value" broken }')
        
        # Create a non-JSON file
        text_file = tmp_path / "extra.txt"
        text_file.write_text("Hello World")
        
        # Run the utility
        pattern = str(tmp_path / "*.json")
        valid_files = _get_valid_json_files(pattern)
        
        # Verify results
        assert len(valid_files) == 1
        assert str(valid_file) in valid_files
        assert str(malformed_file) not in valid_files

class TestSchemaResilience:
    """Test that the build process maintains critical schema constraints."""

    def test_primary_keys_defined(self, cursor):
        """Verify that critical tables have primary keys defined in the schema."""
        tables_to_check = ['competitions', 'matches', 'teams', 'events', 'lineups']
        for table in tables_to_check:
            # query to find table schema
            cursor.execute(f"PRAGMA table_info('{table}')")
            info = cursor.fetchall()
            pk_count = sum(1 for col in info if col[5] > 0) # col[5] is pk flag
            assert pk_count > 0, f"Table {table} does not have a primary key defined"

    def test_foreign_keys_defined(self, cursor):
        """Verify that foreign keys are defined in the schema."""
        cursor.execute("""
            SELECT count(*) 
            FROM duckdb_constraints() 
            WHERE table_name = 'events' AND constraint_type = 'FOREIGN KEY';
        """)
        fk_count = cursor.fetchone()[0]
        assert fk_count > 0, "No foreign keys found on the events table"
        
        # Check specific critical FKs
        cursor.execute("""
            SELECT referenced_table 
            FROM duckdb_constraints() 
            WHERE table_name = 'events' AND constraint_type = 'FOREIGN KEY';
        """)
        referencing_tables = {row[0] for row in cursor.fetchall()}
        expected_refs = {'matches', 'teams', 'players', 'event_types'}
        for ref in expected_refs:
            assert ref in referencing_tables, f"Missing FK reference from events to {ref}"
