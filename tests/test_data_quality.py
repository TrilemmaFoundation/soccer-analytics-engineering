"""Tests for data quality: row counts, value ranges, and data validity."""
import pytest
import json


class TestRowCounts:
    """Test that all tables have data."""

    @pytest.mark.parametrize("table_name", [
        "competitions",
        "teams",
        "matches",
        "event_types",
        "players",
        "positions",
        "play_patterns",
        "events",
    ])
    def test_table_has_data(self, cursor, table_name):
        """Test that each table has at least one row."""
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        assert count > 0, f"Table {table_name} has no data"


class TestCoordinateRanges:
    """Test that coordinates are within reasonable ranges.
    
    Note: Some events (throw-ins, corners, out-of-bounds) can legitimately have
    coordinates slightly outside the field boundaries (0-120 for x, 0-80 for y).
    We allow a margin of -10 to 130 for x and -10 to 90 for y to catch truly invalid data.
    """

    def test_event_location_x_range(self, cursor):
        """Test that location_x values are within reasonable range."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE location_x IS NOT NULL 
                AND (location_x < -10 OR location_x > 130);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with location_x outside reasonable range [-10, 130]"
        )

    def test_event_location_y_range(self, cursor):
        """Test that location_y values are within reasonable range."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE location_y IS NOT NULL 
                AND (location_y < -10 OR location_y > 90);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with location_y outside reasonable range [-10, 90]"
        )

    def test_pass_end_location_x_range(self, cursor):
        """Test that pass_end_location_x values are within reasonable range."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE pass_end_location_x IS NOT NULL 
                AND (pass_end_location_x < -10 OR pass_end_location_x > 130);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} passes with pass_end_location_x outside reasonable range [-10, 130]"
        )

    def test_pass_end_location_y_range(self, cursor):
        """Test that pass_end_location_y values are within reasonable range."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE pass_end_location_y IS NOT NULL 
                AND (pass_end_location_y < -10 OR pass_end_location_y > 90);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} passes with pass_end_location_y outside reasonable range [-10, 90]"
        )

    def test_carry_end_location_x_range(self, cursor):
        """Test that carry_end_location_x values are within reasonable range."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE carry_end_location_x IS NOT NULL 
                AND (carry_end_location_x < -10 OR carry_end_location_x > 130);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} carries with carry_end_location_x outside reasonable range [-10, 130]"
        )

    def test_carry_end_location_y_range(self, cursor):
        """Test that carry_end_location_y values are within reasonable range."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE carry_end_location_y IS NOT NULL 
                AND (carry_end_location_y < -10 OR carry_end_location_y > 90);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} carries with carry_end_location_y outside reasonable range [-10, 90]"
        )


class TestXGValues:
    """Test that xG (expected goals) values are in valid range [0, 1]."""

    def test_shot_xg_range(self, cursor):
        """Test that shot_statsbomb_xg values are between 0 and 1."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE shot_statsbomb_xg IS NOT NULL 
                AND (shot_statsbomb_xg < 0 OR shot_statsbomb_xg > 1);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} shots with shot_statsbomb_xg outside valid range [0, 1]"
        )

    def test_shot_xg_statistics(self, cursor):
        """Test that xG statistics are reasonable."""
        cursor.execute("""
            SELECT 
                MIN(shot_statsbomb_xg) as min_xg,
                MAX(shot_statsbomb_xg) as max_xg,
                AVG(shot_statsbomb_xg) as avg_xg
            FROM events 
            WHERE shot_statsbomb_xg IS NOT NULL;
        """)
        result = cursor.fetchone()
        if result[0] is not None:  # If there are any xG values
            min_xg, max_xg, avg_xg = result
            assert 0 <= min_xg <= 1, f"Minimum xG {min_xg} is outside [0, 1]"
            assert 0 <= max_xg <= 1, f"Maximum xG {max_xg} is outside [0, 1]"
            assert 0 <= avg_xg <= 1, f"Average xG {avg_xg} is outside [0, 1]"


class TestBooleanFlags:
    """Test that boolean flags default to false, not NULL."""

    BOOLEAN_FLAGS = [
        "out",
        "off_camera",
        "counterpress",
        "under_pressure",
        "shot_first_time",
        "shot_deflected",
        "shot_aerial_won",
        "shot_follows_dribble",
        "shot_one_on_one",
        "shot_open_goal",
        "shot_redirect",
        "shot_saved_off_target",
        "shot_saved_to_post",
        "pass_goal_assist",
        "pass_shot_assist",
        "pass_cross",
        "pass_switch",
        "pass_through_ball",
        "pass_aerial_won",
        "pass_deflected",
        "pass_inswinging",
        "pass_outswinging",
        "pass_no_touch",
        "pass_cut_back",
        "pass_straight",
        "pass_miscommunication",
    ]

    @pytest.mark.parametrize("flag_name", BOOLEAN_FLAGS)
    def test_boolean_flag_not_null(self, cursor, flag_name):
        """Test that boolean flags are not NULL (should default to false)."""
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM events 
            WHERE {flag_name} IS NULL;
        """)
        null_count = cursor.fetchone()[0]
        assert null_count == 0, (
            f"Found {null_count} events with NULL {flag_name} (should default to false)"
        )


class TestMatchScores:
    """Test that match scores are valid."""

    def test_home_score_non_negative(self, cursor):
        """Test that home_score is non-negative."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches 
            WHERE home_score IS NOT NULL AND home_score < 0;
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} matches with negative home_score"
        )

    def test_away_score_non_negative(self, cursor):
        """Test that away_score is non-negative."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches 
            WHERE away_score IS NOT NULL AND away_score < 0;
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} matches with negative away_score"
        )

    def test_scores_are_integers(self, cursor):
        """Test that scores are integers (not floats)."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches 
            WHERE home_score IS NOT NULL 
                AND home_score != CAST(home_score AS INTEGER);
        """)
        invalid_home = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches 
            WHERE away_score IS NOT NULL 
                AND away_score != CAST(away_score AS INTEGER);
        """)
        invalid_away = cursor.fetchone()[0]
        
        assert invalid_home == 0, f"Found {invalid_home} matches with non-integer home_score"
        assert invalid_away == 0, f"Found {invalid_away} matches with non-integer away_score"


class TestEventTiming:
    """Test that event timing fields are valid."""

    def test_period_valid(self, cursor):
        """Test that period values are positive integers."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE period IS NOT NULL 
                AND (period < 1 OR period != CAST(period AS INTEGER));
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with invalid period values"
        )

    def test_minute_valid(self, cursor):
        """Test that minute values are non-negative integers."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE minute IS NOT NULL 
                AND (minute < 0 OR minute != CAST(minute AS INTEGER));
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with invalid minute values"
        )

    def test_second_valid(self, cursor):
        """Test that second values are non-negative integers."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE second IS NOT NULL 
                AND (second < 0 OR second >= 60);
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with invalid second values (should be 0-59)"
        )

    def test_index_num_valid(self, cursor):
        """Test that index_num values are non-negative integers."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE index_num IS NOT NULL 
                AND (index_num < 0 OR index_num != CAST(index_num AS INTEGER));
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with invalid index_num values"
        )


class TestJSONFields:
    """Test that JSON fields contain valid JSON or are NULL."""

    JSON_FIELDS = [
        "location",
        "shot_end_location",
        "shot_freeze_frame",
        "pass_end_location",
        "carry_end_location",
    ]

    @pytest.mark.parametrize("field_name", JSON_FIELDS)
    def test_json_field_valid(self, cursor, field_name):
        """Test that JSON fields contain valid JSON or are NULL."""
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM events 
            WHERE {field_name} IS NOT NULL 
                AND {field_name} != 'null'
                AND json_valid({field_name}) = false;
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} events with invalid JSON in {field_name}"
        )


class TestPassLength:
    """Test that pass length values are reasonable."""

    def test_pass_length_non_negative(self, cursor):
        """Test that pass_length is non-negative."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE pass_length IS NOT NULL AND pass_length < 0;
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} passes with negative pass_length"
        )

    def test_pass_length_reasonable_max(self, cursor):
        """Test that pass_length is not unreasonably large (max ~200 yards)."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE pass_length IS NOT NULL AND pass_length > 200;
        """)
        invalid_count = cursor.fetchone()[0]
        assert invalid_count == 0, (
            f"Found {invalid_count} passes with pass_length > 200 yards (unreasonably large)"
        )

