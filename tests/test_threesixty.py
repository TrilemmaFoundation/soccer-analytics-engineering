"""Tests for StatsBomb 360 tracking data integrity and quality."""
import pytest
import json

class TestThreeSixtyDataExistence:
    """Test that 360 tables have data proportional to matches with 360 availability."""

    def test_three_sixty_frames_have_data(self, cursor):
        """Test that three_sixty_frames table has data."""
        cursor.execute("SELECT COUNT(*) FROM three_sixty_frames;")
        count = cursor.fetchone()[0]
        assert count > 0, "three_sixty_frames table is empty"

    def test_three_sixty_positions_have_data(self, cursor):
        """Test that three_sixty_positions table has data."""
        cursor.execute("SELECT COUNT(*) FROM three_sixty_positions;")
        count = cursor.fetchone()[0]
        assert count > 0, "three_sixty_positions table is empty"

    def test_three_sixty_availability_match(self, cursor):
        """Test that matches with match_status_360='available' have frames.
        Note: We allow some mismatches as StatsBomb open-data might not include 
        all 360 files even if metadata says available.
        """
        cursor.execute("""
            SELECT COUNT(DISTINCT m.match_id)
            FROM matches m
            LEFT JOIN three_sixty_frames f ON m.match_id = f.match_id
            WHERE m.match_status_360 = 'available'
            AND f.match_id IS NULL;
        """)
        orphans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT match_id) FROM matches WHERE match_status_360 = 'available';")
        total_available = cursor.fetchone()[0]
        
        # In open data, it's common that some available data is missing. 
        # We just want to ensure it's not a complete failure.
        if total_available > 0:
            assert orphans / total_available < 0.5, f"Too many available 360 matches ({orphans}/{total_available}) missing frames"

class TestThreeSixtyReferentialIntegrity:
    """Test referential integrity for 360 tracking data."""

    def test_frames_link_to_valid_events(self, cursor):
        """Test that event_uuid in three_sixty_frames links to a valid event."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM three_sixty_frames f
            LEFT JOIN events e ON f.event_uuid = e.id
            WHERE e.id IS NULL;
        """)
        orphans = cursor.fetchone()[0]
        assert orphans == 0, f"Found {orphans} 360 frames linking to non-existent events"

    def test_positions_link_to_valid_frames(self, cursor):
        """Test that event_uuid in three_sixty_positions links to a valid frame."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM three_sixty_positions p
            LEFT JOIN three_sixty_frames f ON p.event_uuid = f.event_uuid
            WHERE f.event_uuid IS NULL;
        """)
        orphans = cursor.fetchone()[0]
        assert orphans == 0, f"Found {orphans} 360 positions linking to non-existent frames"

class TestThreeSixtyDataQuality:
    """Test data quality and coordinate ranges for 360 data."""

    def test_three_sixty_coordinate_ranges(self, cursor):
        """Test that 360 positions are within reasonable coordinate ranges.
        Note: 360 data can include objects outside the pitch, so we use a wide buffer.
        """
        # Pitch is 0-120x and 0-80y. 360 data often has wider bounds.
        cursor.execute("""
            SELECT COUNT(*)
            FROM three_sixty_positions
            WHERE location_x < -100 OR location_x > 220
               OR location_y < -100 OR location_y > 180;
        """)
        out_of_bounds = cursor.fetchone()[0]
        assert out_of_bounds == 0, f"Found {out_of_bounds} 360 positions outside extremes [-100, 220]x, [-100, 180]y"

    @pytest.mark.parametrize("flag", ["teammate", "actor", "keeper"])
    def test_three_sixty_flags_not_null(self, cursor, flag):
        """Test that 360 flags are not NULL."""
        cursor.execute(f"SELECT COUNT(*) FROM three_sixty_positions WHERE {flag} IS NULL;")
        null_count = cursor.fetchone()[0]
        assert null_count == 0, f"Found {null_count} instances where {flag} is NULL"

    def test_visible_area_is_valid_json(self, cursor):
        """Test that visible_area field contains valid JSON."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM three_sixty_frames
            WHERE visible_area IS NOT NULL
            AND json_valid(visible_area) = false;
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, f"Found {invalid_count} 360 frames with invalid visible_area JSON"
