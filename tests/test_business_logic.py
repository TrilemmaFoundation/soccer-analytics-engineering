"""Tests for business logic: player canonicalization and data transformations."""
import pytest
import json


# Player canonicalization mapping from build.py
PLAYER_CANONICALIZATION = {
    4354: 'Philip Foden',
    25742: 'Karly Roestbakken',
    25546: 'Cheyna Lee Matthews',
    4951: 'Quinn',
    5082: 'Marta Vieira da Silva',
    18617: 'Mykola Matviyenko',
    3961: 'N\'Golo Kanté',
    5659: 'Khadim N\'Diaye',
    401453: 'David Ngog',
    184468: 'Álvaro Zamora',
}


class TestPlayerCanonicalization:
    """Test that player names are correctly canonicalized."""

    @pytest.mark.parametrize("player_id,expected_name", PLAYER_CANONICALIZATION.items())
    def test_player_canonicalized_in_players_table(self, cursor, player_id, expected_name):
        """Test that canonicalized player names appear in players table."""
        cursor.execute("""
            SELECT name FROM players WHERE id = ?;
        """, [player_id])
        result = cursor.fetchone()
        
        if result:
            actual_name = result[0]
            assert actual_name == expected_name, (
                f"Player {player_id}: Expected '{expected_name}', got '{actual_name}'"
            )

    @pytest.mark.parametrize("player_id,expected_name", PLAYER_CANONICALIZATION.items())
    def test_player_canonicalized_in_events_table(self, cursor, player_id, expected_name):
        """Test that canonicalized player names appear in events table."""
        cursor.execute("""
            SELECT DISTINCT player FROM events WHERE player_id = ?;
        """, [player_id])
        results = cursor.fetchall()
        
        if results:
            # All player names for this ID should be the canonicalized name
            actual_names = {row[0] for row in results if row[0] is not None}
            assert len(actual_names) == 1, (
                f"Player {player_id}: Found multiple names {actual_names}, expected single canonical name"
            )
            assert expected_name in actual_names, (
                f"Player {player_id}: Expected '{expected_name}' in {actual_names}"
            )

    def test_all_canonicalized_players_exist(self, cursor):
        """Test that all canonicalized player IDs exist in the database."""
        cursor.execute("""
            SELECT id FROM players WHERE id IN ({});
        """.format(','.join(map(str, PLAYER_CANONICALIZATION.keys()))))
        existing_ids = {row[0] for row in cursor.fetchall()}
        expected_ids = set(PLAYER_CANONICALIZATION.keys())
        
        missing_ids = expected_ids - existing_ids
        assert not missing_ids, (
            f"Canonicalized player IDs not found in database: {missing_ids}"
        )


class TestPassRecipientConsistency:
    """Test that pass recipient names match canonicalized player names."""

    def test_pass_recipient_matches_player_name(self, cursor):
        """Test that pass_recipient names match player names when recipient_id exists."""
        cursor.execute("""
            SELECT DISTINCT
                e.pass_recipient_id,
                e.pass_recipient,
                p.name as player_name
            FROM events e
            JOIN players p ON e.pass_recipient_id = p.id
            WHERE e.pass_recipient_id IS NOT NULL
                AND e.pass_recipient IS NOT NULL
                AND e.pass_recipient != p.name;
        """)
        mismatches = cursor.fetchall()
        
        # Check if mismatches are only due to canonicalization
        # (pass_recipient might not be canonicalized, but should match if recipient_id matches)
        for recipient_id, recipient_name, player_name in mismatches:
            # If this is a canonicalized player, recipient_name should match canonicalized name
            if recipient_id in PLAYER_CANONICALIZATION:
                expected_name = PLAYER_CANONICALIZATION[recipient_id]
                assert recipient_name == expected_name or player_name == expected_name, (
                    f"Pass recipient {recipient_id}: recipient_name='{recipient_name}', "
                    f"player_name='{player_name}', expected='{expected_name}'"
                )

    def test_pass_recipient_id_exists_in_players(self, cursor):
        """Test that all pass_recipient_id values reference valid players."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events e
            LEFT JOIN players p ON e.pass_recipient_id = p.id
            WHERE e.pass_recipient_id IS NOT NULL AND p.id IS NULL;
        """)
        orphaned = cursor.fetchone()[0]
        assert orphaned == 0, (
            f"Found {orphaned} passes with invalid pass_recipient_id references"
        )


class TestJSONFieldTransformations:
    """Test that JSON fields are correctly transformed from source data."""

    def test_location_json_format(self, cursor):
        """Test that location field contains valid JSON array [x, y]."""
        cursor.execute("""
            SELECT location, location_x, location_y
            FROM events
            WHERE location IS NOT NULL
            LIMIT 100;
        """)
        results = cursor.fetchall()
        
        for location_json, location_x, location_y in results:
            if location_json:
                try:
                    location_array = json.loads(location_json)
                    assert isinstance(location_array, list), (
                        f"Location should be JSON array, got: {location_json}"
                    )
                    assert len(location_array) >= 2, (
                        f"Location array should have at least 2 elements, got: {location_array}"
                    )
                    # Check that extracted coordinates match JSON
                    if location_x is not None and location_y is not None:
                        assert abs(location_array[0] - location_x) < 0.001, (
                            f"location_x mismatch: JSON={location_array[0]}, column={location_x}"
                        )
                        assert abs(location_array[1] - location_y) < 0.001, (
                            f"location_y mismatch: JSON={location_array[1]}, column={location_y}"
                        )
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in location field: {location_json}")

    def test_shot_end_location_json_format(self, cursor):
        """Test that shot_end_location contains valid JSON array [x, y, z]."""
        cursor.execute("""
            SELECT shot_end_location
            FROM events
            WHERE shot_end_location IS NOT NULL
            LIMIT 100;
        """)
        results = cursor.fetchall()
        
        for (shot_end_location,) in results:
            if shot_end_location:
                try:
                    location_array = json.loads(shot_end_location)
                    assert isinstance(location_array, list), (
                        f"shot_end_location should be JSON array, got: {shot_end_location}"
                    )
                    assert len(location_array) >= 2, (
                        f"shot_end_location array should have at least 2 elements, got: {location_array}"
                    )
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in shot_end_location field: {shot_end_location}")

    def test_pass_end_location_json_format(self, cursor):
        """Test that pass_end_location contains valid JSON array [x, y]."""
        cursor.execute("""
            SELECT pass_end_location, pass_end_location_x, pass_end_location_y
            FROM events
            WHERE pass_end_location IS NOT NULL
            LIMIT 100;
        """)
        results = cursor.fetchall()
        
        for pass_end_location, pass_end_location_x, pass_end_location_y in results:
            if pass_end_location:
                try:
                    location_array = json.loads(pass_end_location)
                    assert isinstance(location_array, list), (
                        f"pass_end_location should be JSON array, got: {pass_end_location}"
                    )
                    assert len(location_array) >= 2, (
                        f"pass_end_location array should have at least 2 elements, got: {location_array}"
                    )
                    # Check that extracted coordinates match JSON
                    if pass_end_location_x is not None and pass_end_location_y is not None:
                        assert abs(location_array[0] - pass_end_location_x) < 0.001, (
                            f"pass_end_location_x mismatch: JSON={location_array[0]}, column={pass_end_location_x}"
                        )
                        assert abs(location_array[1] - pass_end_location_y) < 0.001, (
                            f"pass_end_location_y mismatch: JSON={location_array[1]}, column={pass_end_location_y}"
                        )
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in pass_end_location field: {pass_end_location}")

    def test_carry_end_location_json_format(self, cursor):
        """Test that carry_end_location contains valid JSON array [x, y]."""
        cursor.execute("""
            SELECT carry_end_location, carry_end_location_x, carry_end_location_y
            FROM events
            WHERE carry_end_location IS NOT NULL
            LIMIT 100;
        """)
        results = cursor.fetchall()
        
        for carry_end_location, carry_end_location_x, carry_end_location_y in results:
            if carry_end_location:
                try:
                    location_array = json.loads(carry_end_location)
                    assert isinstance(location_array, list), (
                        f"carry_end_location should be JSON array, got: {carry_end_location}"
                    )
                    assert len(location_array) >= 2, (
                        f"carry_end_location array should have at least 2 elements, got: {location_array}"
                    )
                    # Check that extracted coordinates match JSON
                    if carry_end_location_x is not None and carry_end_location_y is not None:
                        assert abs(location_array[0] - carry_end_location_x) < 0.001, (
                            f"carry_end_location_x mismatch: JSON={location_array[0]}, column={carry_end_location_x}"
                        )
                        assert abs(location_array[1] - carry_end_location_y) < 0.001, (
                            f"carry_end_location_y mismatch: JSON={location_array[1]}, column={carry_end_location_y}"
                        )
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in carry_end_location field: {carry_end_location}")

    def test_shot_freeze_frame_json_format(self, cursor):
        """Test that shot_freeze_frame contains valid JSON array."""
        cursor.execute("""
            SELECT shot_freeze_frame
            FROM events
            WHERE shot_freeze_frame IS NOT NULL
            LIMIT 50;
        """)
        results = cursor.fetchall()
        
        for (shot_freeze_frame,) in results:
            if shot_freeze_frame:
                try:
                    freeze_frame = json.loads(shot_freeze_frame)
                    assert isinstance(freeze_frame, list), (
                        f"shot_freeze_frame should be JSON array, got: {shot_freeze_frame}"
                    )
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in shot_freeze_frame field: {shot_freeze_frame}")


class TestDataTransformations:
    """Test that data transformations from build.py are correct."""

    def test_match_id_extracted_from_filename(self, cursor):
        """Test that match_id is correctly extracted from event filenames."""
        # This is indirectly tested by checking that all events have valid match_id FKs
        # But we can also check that match_ids are reasonable (positive integers)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE match_id IS NOT NULL 
                AND (match_id <= 0 OR match_id != CAST(match_id AS INTEGER));
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with invalid match_id values"
        )

    def test_boolean_flags_default_to_false(self, cursor):
        """Test that boolean flags default to false when not set."""
        # This is tested in test_data_quality.py, but we verify the transformation logic
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN out = false THEN 1 ELSE 0 END) as false_count,
                SUM(CASE WHEN out = true THEN 1 ELSE 0 END) as true_count,
                SUM(CASE WHEN out IS NULL THEN 1 ELSE 0 END) as null_count
            FROM events;
        """)
        result = cursor.fetchone()
        total, false_count, true_count, null_count = result
        
        # Most events should have out=false (default), some should have out=true
        # None should be NULL
        assert null_count == 0, (
            f"Found {null_count} events with NULL 'out' flag (should default to false)"
        )
        assert false_count + true_count == total, "Boolean flag counts don't match total"

    def test_managers_json_format(self, cursor):
        """Test that manager fields contain valid JSON or are NULL."""
        cursor.execute("""
            SELECT home_managers, away_managers
            FROM matches
            WHERE home_managers IS NOT NULL OR away_managers IS NOT NULL
            LIMIT 50;
        """)
        results = cursor.fetchall()
        
        for home_managers, away_managers in results:
            for managers_json in [home_managers, away_managers]:
                if managers_json:
                    try:
                        managers = json.loads(managers_json)
                        assert isinstance(managers, list), (
                            f"Managers should be JSON array, got: {managers_json}"
                        )
                    except json.JSONDecodeError:
                        pytest.fail(f"Invalid JSON in managers field: {managers_json}")

