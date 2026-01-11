"""Tests for database schema validation."""

import pytest

# Expected table schemas based on schema.py
EXPECTED_TABLES = {
    "competitions": {
        "competition_id": "INTEGER",
        "season_id": "INTEGER",
        "name": "TEXT",
        "gender": "TEXT",
        "is_youth": "BOOLEAN",
        "is_international": "BOOLEAN",
        "country_name": "TEXT",
        "season_name": "TEXT",
        "match_updated": "TEXT",
        "match_available_360": "TEXT",
    },
    "teams": {
        "id": "INTEGER",
        "name": "TEXT",
        "gender": "TEXT",
    },
    "matches": {
        "match_id": "INTEGER",
        "match_date": "TEXT",
        "match_week": "INTEGER",
        "match_status": "TEXT",
        "match_status_360": "TEXT",
        "kickoff": "TEXT",
        "home_score": "INTEGER",
        "away_score": "INTEGER",
        "competition_id": "INTEGER",
        "competition": "TEXT",
        "competition_stage": "TEXT",
        "season_id": "INTEGER",
        "season": "TEXT",
        "home_team_id": "INTEGER",
        "home_team": "TEXT",
        "home_managers": "TEXT",
        "away_team_id": "INTEGER",
        "away_team": "TEXT",
        "away_managers": "TEXT",
        "stadium_id": "INTEGER",
        "stadium": "TEXT",
        "referee_id": "INTEGER",
        "referee": "TEXT",
        "last_updated": "TEXT",
        "last_updated_360": "TEXT",
        "data_version": "TEXT",
        "shot_fidelity_version": "TEXT",
        "xy_fidelity_version": "TEXT",
    },
    "event_types": {
        "id": "INTEGER",
        "name": "TEXT",
    },
    "players": {
        "id": "INTEGER",
        "name": "TEXT",
    },
    "positions": {
        "id": "INTEGER",
        "name": "TEXT",
    },
    "play_patterns": {
        "id": "INTEGER",
        "name": "TEXT",
    },
    "countries": {
        "id": "INTEGER",
        "name": "TEXT",
    },
    "events": {
        "id": "TEXT",
        "index_num": "INTEGER",
        "period": "INTEGER",
        "minute": "INTEGER",
        "second": "INTEGER",
        "timestamp": "TEXT",
        "duration": "DOUBLE",
        "location": "TEXT",
        "location_x": "DOUBLE",
        "location_y": "DOUBLE",
        "possession": "INTEGER",
        "possession_team_id": "INTEGER",
        "possession_team": "TEXT",
        "out": "BOOLEAN",
        "off_camera": "BOOLEAN",
        "counterpress": "BOOLEAN",
        "under_pressure": "BOOLEAN",
        "type_id": "INTEGER",
        "type": "TEXT",
        "match_id": "INTEGER",
        "team_id": "INTEGER",
        "team": "TEXT",
        "player_id": "INTEGER",
        "player": "TEXT",
        "position_id": "INTEGER",
        "position": "TEXT",
        "play_pattern_id": "INTEGER",
        "play_pattern": "TEXT",
        "shot_end_location": "TEXT",
        "shot_end_location_x": "DOUBLE",
        "shot_end_location_y": "DOUBLE",
        "shot_end_location_z": "DOUBLE",
        "shot_statsbomb_xg": "DOUBLE",
        "shot_outcome": "TEXT",
        "shot_technique": "TEXT",
        "shot_body_part": "TEXT",
        "shot_type": "TEXT",
        "shot_key_pass_id": "TEXT",
        "shot_freeze_frame": "TEXT",
        "shot_first_time": "BOOLEAN",
        "shot_deflected": "BOOLEAN",
        "shot_aerial_won": "BOOLEAN",
        "shot_follows_dribble": "BOOLEAN",
        "shot_one_on_one": "BOOLEAN",
        "shot_open_goal": "BOOLEAN",
        "shot_redirect": "BOOLEAN",
        "shot_saved_off_target": "BOOLEAN",
        "shot_saved_to_post": "BOOLEAN",
        "pass_end_location": "TEXT",
        "pass_end_location_x": "DOUBLE",
        "pass_end_location_y": "DOUBLE",
        "pass_recipient_id": "INTEGER",
        "pass_recipient": "TEXT",
        "pass_length": "DOUBLE",
        "pass_angle": "DOUBLE",
        "pass_height": "TEXT",
        "pass_body_part": "TEXT",
        "pass_type": "TEXT",
        "pass_outcome": "TEXT",
        "pass_technique": "TEXT",
        "pass_assisted_shot_id": "TEXT",
        "pass_goal_assist": "BOOLEAN",
        "pass_shot_assist": "BOOLEAN",
        "pass_cross": "BOOLEAN",
        "pass_switch": "BOOLEAN",
        "pass_through_ball": "BOOLEAN",
        "pass_aerial_won": "BOOLEAN",
        "pass_deflected": "BOOLEAN",
        "pass_inswinging": "BOOLEAN",
        "pass_outswinging": "BOOLEAN",
        "pass_no_touch": "BOOLEAN",
        "pass_cut_back": "BOOLEAN",
        "pass_straight": "BOOLEAN",
        "pass_miscommunication": "BOOLEAN",
        "carry_end_location": "TEXT",
        "carry_end_location_x": "DOUBLE",
        "carry_end_location_y": "DOUBLE",
        "dribble_outcome": "TEXT",
        "dribble_nutmeg": "BOOLEAN",
        "dribble_overrun": "BOOLEAN",
        "dribble_no_touch": "BOOLEAN",
        "duel_type": "TEXT",
        "duel_outcome": "TEXT",
        "foul_committed_card": "TEXT",
        "foul_committed_type": "TEXT",
        "foul_committed_offensive": "BOOLEAN",
        "foul_committed_advantage": "BOOLEAN",
        "foul_committed_penalty": "BOOLEAN",
        "foul_won_defensive": "BOOLEAN",
        "foul_won_advantage": "BOOLEAN",
        "foul_won_penalty": "BOOLEAN",
        "goalkeeper_type": "TEXT",
        "goalkeeper_outcome": "TEXT",
        "goalkeeper_technique": "TEXT",
        "goalkeeper_position": "TEXT",
        "goalkeeper_body_part": "TEXT",
        "goalkeeper_end_location": "TEXT",
        "goalkeeper_end_location_x": "DOUBLE",
        "goalkeeper_end_location_y": "DOUBLE",
        "clearance_body_part": "TEXT",
        "clearance_aerial_won": "BOOLEAN",
        "clearance_head": "BOOLEAN",
        "clearance_left_foot": "BOOLEAN",
        "clearance_right_foot": "BOOLEAN",
        "interception_outcome": "TEXT",
        "block_deflection": "BOOLEAN",
        "block_offensive": "BOOLEAN",
        "block_save_block": "BOOLEAN",
        "ball_recovery_offensive": "BOOLEAN",
        "ball_recovery_failure": "BOOLEAN",
        "miscontrol_aerial_won": "BOOLEAN",
        "substitution_replacement_id": "INTEGER",
        "substitution_replacement_name": "TEXT",
        "substitution_outcome": "TEXT",
        "fifty_fifty_outcome": "TEXT",
        "bad_behaviour_card": "TEXT",
        "injury_stoppage_in_chain": "BOOLEAN",
    },
    "lineups": {
        "match_id": "INTEGER",
        "team_id": "INTEGER",
        "team_name": "TEXT",
    },
    "lineup_players": {
        "match_id": "INTEGER",
        "team_id": "INTEGER",
        "player_id": "INTEGER",
        "player_name": "TEXT",
        "player_nickname": "TEXT",
        "jersey_number": "INTEGER",
        "country_id": "INTEGER",
        "country_name": "TEXT",
    },
    "lineup_positions": {
        "id": "INTEGER",
        "match_id": "INTEGER",
        "team_id": "INTEGER",
        "player_id": "INTEGER",
        "position_id": "INTEGER",
        "position_name": "TEXT",
        "from_time": "TEXT",
        "to_time": "TEXT",
        "from_period": "INTEGER",
        "to_period": "INTEGER",
        "start_reason": "TEXT",
        "end_reason": "TEXT",
    },
    "lineup_cards": {
        "id": "INTEGER",
        "match_id": "INTEGER",
        "team_id": "INTEGER",
        "player_id": "INTEGER",
        "card_time": "TEXT",
        "card_type": "TEXT",
        "reason": "TEXT",
        "period": "INTEGER",
    },
    "three_sixty_frames": {
        "event_uuid": "TEXT",
        "match_id": "INTEGER",
        "visible_area": "TEXT",
    },
    "three_sixty_positions": {
        "id": "INTEGER",
        "event_uuid": "TEXT",
        "teammate": "BOOLEAN",
        "actor": "BOOLEAN",
        "keeper": "BOOLEAN",
        "location_x": "DOUBLE",
        "location_y": "DOUBLE",
    },
}

EXPECTED_INDEXES = [
    "idx_events_match",
    "idx_events_player",
    "idx_events_type",
    "idx_events_team",
    "idx_events_possession",
    "idx_matches_competition",
    "idx_matches_home_team",
    "idx_matches_away_team",
    "idx_matches_date",
    "idx_lineup_players_player",
    "idx_lineup_players_match",
    "idx_lineup_positions_player",
    "idx_lineup_positions_match",
    "idx_lineup_cards_player",
    "idx_lineup_cards_match",
    "idx_360_frames_match",
    "idx_360_positions_event",
]



def get_table_columns(cursor, table_name):
    """Get column information for a table."""
    cursor.execute(
        f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;
        """
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def get_indexes(cursor):
    """Get all index names from the database."""
    cursor.execute(
        """
        SELECT name as index_name
        FROM sqlite_master
        WHERE type = 'index' AND name IS NOT NULL;
        """
    )
    return {row[0] for row in cursor.fetchall()}


def get_tables(cursor):
    """Get all table names from the database."""
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main' AND table_type = 'BASE TABLE';
        """
    )
    return {row[0] for row in cursor.fetchall()}


class TestTableExistence:
    """Test that all required tables exist."""

    def test_all_tables_exist(self, cursor):
        """Verify all 8 expected tables exist."""
        tables = get_tables(cursor)
        expected_table_names = set(EXPECTED_TABLES.keys())
        assert tables == expected_table_names, (
            f"Missing tables: {expected_table_names - tables}. "
            f"Unexpected tables: {tables - expected_table_names}"
        )

    @pytest.mark.parametrize("table_name", EXPECTED_TABLES.keys())
    def test_table_exists(self, cursor, table_name):
        """Test that each expected table exists."""
        tables = get_tables(cursor)
        assert table_name in tables, f"Table {table_name} does not exist"


class TestTableColumns:
    """Test that tables have correct columns and types."""

    @pytest.mark.parametrize("table_name", EXPECTED_TABLES.keys())
    def test_table_has_expected_columns(self, cursor, table_name):
        """Test that each table has all expected columns."""
        columns = get_table_columns(cursor, table_name)
        expected_columns = set(EXPECTED_TABLES[table_name].keys())
        actual_columns = set(columns.keys())

        assert actual_columns == expected_columns, (
            f"Table {table_name}: Missing columns: {expected_columns - actual_columns}. "
            f"Unexpected columns: {actual_columns - expected_columns}"
        )

    @pytest.mark.parametrize(
        "table_name,column_name,expected_type",
        [
            (table, col, EXPECTED_TABLES[table][col])
            for table in EXPECTED_TABLES
            for col in EXPECTED_TABLES[table]
        ],
    )
    def test_column_type(self, cursor, table_name, column_name, expected_type):
        """Test that each column has the correct type."""
        columns = get_table_columns(cursor, table_name)
        actual_type = columns.get(column_name)

        # DuckDB uses different type names, so we normalize them
        type_mapping = {
            "INTEGER": ["INTEGER", "BIGINT"],
            "TEXT": ["VARCHAR", "TEXT"],
            "DOUBLE": ["DOUBLE", "REAL", "FLOAT"],
            "BOOLEAN": ["BOOLEAN", "BOOL"],
        }

        # Check if actual type matches expected (accounting for DuckDB variations)
        type_matches = False
        for base_type, variants in type_mapping.items():
            if expected_type.upper() == base_type:
                type_matches = actual_type.upper() in variants
                break

        assert type_matches, (
            f"Table {table_name}, column {column_name}: "
            f"Expected type {expected_type}, got {actual_type}"
        )


class TestIndexes:
    """Test that all expected indexes are created."""

    def test_all_indexes_exist(self, cursor):
        """Verify all 7 expected indexes exist."""
        indexes = get_indexes(cursor)
        expected_index_names = set(EXPECTED_INDEXES)

        # Check that all expected indexes exist
        missing_indexes = expected_index_names - indexes
        assert not missing_indexes, f"Missing indexes: {missing_indexes}"

    @pytest.mark.parametrize("index_name", EXPECTED_INDEXES)
    def test_index_exists(self, cursor, index_name):
        """Test that each expected index exists."""
        indexes = get_indexes(cursor)
        assert index_name in indexes, f"Index {index_name} does not exist"
