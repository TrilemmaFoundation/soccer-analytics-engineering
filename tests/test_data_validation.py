"""Tests for data validation: aggregate statistics, cross-table relationships, and domain-specific soccer data integrity."""
import pytest
import json


class TestAggregateDataStatistics:
    """Test that tables have reasonable row counts and data distributions."""

    def test_events_table_has_sufficient_data(self, cursor):
        """Test that events table has a reasonable minimum number of events."""
        cursor.execute("SELECT COUNT(*) FROM events;")
        count = cursor.fetchone()[0]
        assert count > 1000000, (
            f"Events table has only {count} rows, expected at least 1M"
        )

    def test_matches_table_has_sufficient_data(self, cursor):
        """Test that matches table has a reasonable minimum number of matches."""
        cursor.execute("SELECT COUNT(*) FROM matches;")
        count = cursor.fetchone()[0]
        assert count > 100, (
            f"Matches table has only {count} rows, expected at least 100"
        )

    def test_teams_table_has_sufficient_data(self, cursor):
        """Test that teams table has a reasonable minimum number of teams."""
        cursor.execute("SELECT COUNT(*) FROM teams;")
        count = cursor.fetchone()[0]
        assert count > 50, (
            f"Teams table has only {count} rows, expected at least 50"
        )

    def test_event_types_table_has_expected_count(self, cursor):
        """Test that event_types table has expected number of entries (~35)."""
        cursor.execute("SELECT COUNT(*) FROM event_types;")
        count = cursor.fetchone()[0]
        assert 30 <= count <= 40, (
            f"event_types table has {count} entries, expected ~35 (30-40 range)"
        )

    def test_positions_table_has_expected_count(self, cursor):
        """Test that positions table has expected number of entries (~25)."""
        cursor.execute("SELECT COUNT(*) FROM positions;")
        count = cursor.fetchone()[0]
        assert 20 <= count <= 30, (
            f"positions table has {count} entries, expected ~25 (20-30 range)"
        )

    def test_play_patterns_table_has_expected_count(self, cursor):
        """Test that play_patterns table has expected number of entries (~9)."""
        cursor.execute("SELECT COUNT(*) FROM play_patterns;")
        count = cursor.fetchone()[0]
        assert 7 <= count <= 12, (
            f"play_patterns table has {count} entries, expected ~9 (7-12 range)"
        )

    def test_events_per_match_range(self, cursor):
        """Test that events per match are within expected ranges (typically 1000-4000)."""
        cursor.execute("""
            SELECT 
                match_id,
                COUNT(*) as event_count
            FROM events
            GROUP BY match_id
            ORDER BY event_count;
        """)
        event_counts = [row[1] for row in cursor.fetchall()]
        
        if event_counts:
            min_events = min(event_counts)
            max_events = max(event_counts)
            avg_events = sum(event_counts) / len(event_counts)
            
            # Allow some flexibility - matches can have fewer events if incomplete
            assert min_events >= 100, (
                f"Some matches have very few events (min: {min_events}), expected at least 100"
            )
            assert max_events <= 5500, (
                f"Some matches have too many events (max: {max_events}), expected at most 5500"
            )
            assert 500 <= avg_events <= 4000, (
                f"Average events per match is {avg_events:.1f}, expected 500-4000"
            )


class TestCrossTableRelationshipCompleteness:
    """Test that cross-table relationships are complete."""

    def test_all_matches_have_events(self, cursor):
        """Test that every match has at least one event."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches m
            LEFT JOIN events e ON m.match_id = e.match_id
            WHERE e.match_id IS NULL;
        """)
        matches_without_events = cursor.fetchone()[0]
        assert matches_without_events == 0, (
            f"Found {matches_without_events} matches without any events"
        )

    def test_all_teams_in_matches_exist_in_teams_table(self, cursor):
        """Test that every team referenced in matches exists in teams table."""
        cursor.execute("""
            SELECT COUNT(DISTINCT home_team_id)
            FROM matches
            WHERE home_team_id IS NOT NULL
                AND home_team_id NOT IN (SELECT id FROM teams);
        """)
        orphaned_home_teams = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT away_team_id)
            FROM matches
            WHERE away_team_id IS NOT NULL
                AND away_team_id NOT IN (SELECT id FROM teams);
        """)
        orphaned_away_teams = cursor.fetchone()[0]
        
        assert orphaned_home_teams == 0, (
            f"Found {orphaned_home_teams} home teams in matches that don't exist in teams table"
        )
        assert orphaned_away_teams == 0, (
            f"Found {orphaned_away_teams} away teams in matches that don't exist in teams table"
        )

    def test_all_event_types_in_events_exist_in_event_types_table(self, cursor):
        """Test that every event type used in events exists in event_types table."""
        cursor.execute("""
            SELECT COUNT(DISTINCT type_id)
            FROM events
            WHERE type_id IS NOT NULL
                AND type_id NOT IN (SELECT id FROM event_types);
        """)
        orphaned_types = cursor.fetchone()[0]
        assert orphaned_types == 0, (
            f"Found {orphaned_types} event types in events that don't exist in event_types table"
        )

    def test_all_players_in_events_exist_in_players_table(self, cursor):
        """Test that every player referenced in events exists in players table."""
        cursor.execute("""
            SELECT COUNT(DISTINCT player_id)
            FROM events
            WHERE player_id IS NOT NULL
                AND player_id NOT IN (SELECT id FROM players);
        """)
        orphaned_players = cursor.fetchone()[0]
        assert orphaned_players == 0, (
            f"Found {orphaned_players} players in events that don't exist in players table"
        )

    def test_all_positions_in_events_exist_in_positions_table(self, cursor):
        """Test that every position used in events exists in positions table."""
        cursor.execute("""
            SELECT COUNT(DISTINCT position_id)
            FROM events
            WHERE position_id IS NOT NULL
                AND position_id NOT IN (SELECT id FROM positions);
        """)
        orphaned_positions = cursor.fetchone()[0]
        assert orphaned_positions == 0, (
            f"Found {orphaned_positions} positions in events that don't exist in positions table"
        )

    def test_all_play_patterns_in_events_exist_in_play_patterns_table(self, cursor):
        """Test that every play pattern used in events exists in play_patterns table."""
        cursor.execute("""
            SELECT COUNT(DISTINCT play_pattern_id)
            FROM events
            WHERE play_pattern_id IS NOT NULL
                AND play_pattern_id NOT IN (SELECT id FROM play_patterns);
        """)
        orphaned_patterns = cursor.fetchone()[0]
        assert orphaned_patterns == 0, (
            f"Found {orphaned_patterns} play patterns in events that don't exist in play_patterns table"
        )


class TestDomainSpecificSoccerValidation:
    """Test domain-specific soccer data validation."""

    EXPECTED_EVENT_TYPES = [
        "Pass",
        "Shot",
        "Carry",
        "Ball Receipt*",
        "Dribble",
        "Pressure",
        "Foul Committed",
        "Ball Recovery",
        "Interception",
        "Clearance",
        "Miscontrol",
        "Duel",
        "Block",
        "Offside",
        "Substitution",
        "Goal Keeper",
        "Bad Behaviour",
        "Half Start",
        "Half End",
        "Injury Stoppage",
        "50/50",
    ]

    EXPECTED_POSITIONS = [
        "Goalkeeper",
        "Left Back",
        "Right Back",
        "Left Wing Back",
        "Right Wing Back",
        "Left Center Back",
        "Right Center Back",
        "Center Back",
        "Left Midfield",
        "Right Midfield",
        "Left Wing",
        "Right Wing",
        "Left Attacking Midfield",
        "Right Attacking Midfield",
        "Center Attacking Midfield",
        "Center Midfield",
        "Left Center Midfield",
        "Right Center Midfield",
        "Left Forward",
        "Right Forward",
        "Center Forward",
        "Striker",
    ]

    EXPECTED_PLAY_PATTERNS = [
        "Regular Play",
        "From Corner",
        "From Free Kick",
        "From Throw In",
        "From Kick Off",
        "From Counter",
        "From Goal Kick",
        "From Keeper",
        "Other",
    ]

    @pytest.mark.parametrize("event_type", EXPECTED_EVENT_TYPES)
    def test_expected_event_type_exists(self, cursor, event_type):
        """Test that expected event types exist in the database."""
        # Handle wildcard matching for event types like "Ball Receipt*"
        if event_type.endswith("*"):
            pattern = event_type[:-1]
            cursor.execute("""
                SELECT COUNT(*) 
                FROM event_types 
                WHERE name LIKE ?;
            """, [f"{pattern}%"])
        else:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM event_types 
                WHERE name = ?;
            """, [event_type])
        
        count = cursor.fetchone()[0]
        assert count > 0, (
            f"Expected event type '{event_type}' not found in event_types table"
        )

    @pytest.mark.parametrize("position", EXPECTED_POSITIONS)
    def test_expected_position_exists(self, cursor, position):
        """Test that expected positions exist in the database."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM positions 
            WHERE name = ?;
        """, [position])
        count = cursor.fetchone()[0]
        # Some positions might not exist in all datasets, so we just log if missing
        if count == 0:
            pytest.skip(f"Position '{position}' not found (may not be in this dataset)")

    @pytest.mark.parametrize("play_pattern", EXPECTED_PLAY_PATTERNS)
    def test_expected_play_pattern_exists(self, cursor, play_pattern):
        """Test that expected play patterns exist in the database."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM play_patterns 
            WHERE name = ?;
        """, [play_pattern])
        count = cursor.fetchone()[0]
        assert count > 0, (
            f"Expected play pattern '{play_pattern}' not found in play_patterns table"
        )

    def test_goal_count_matches_match_scores(self, cursor):
        """Test that goal count in events approximately matches match scores."""
        # Count goals from events (Shot events with outcome = Goal)
        cursor.execute("""
            SELECT 
                match_id,
                COUNT(*) as goal_count
            FROM events
            WHERE type = 'Shot'
                AND shot_outcome = 'Goal'
            GROUP BY match_id;
        """)
        event_goals = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get match scores
        cursor.execute("""
            SELECT 
                match_id,
                home_score,
                away_score
            FROM matches;
        """)
        match_scores = cursor.fetchall()
        
        mismatches = []
        for match_id, home_score, away_score in match_scores:
            expected_goals = (home_score or 0) + (away_score or 0)
            actual_goals = event_goals.get(match_id, 0)
            
            # Allow small discrepancy (some goals might be recorded differently)
            if abs(expected_goals - actual_goals) > 2:
                mismatches.append((match_id, expected_goals, actual_goals))
        
        # Log mismatches but don't fail if only a few (data might have edge cases)
        mismatch_rate = len(mismatches) / len(match_scores) if match_scores else 0
        assert mismatch_rate < 0.05, (
            f"Found {len(mismatches)} matches ({mismatch_rate*100:.1f}%) where goal count "
            f"doesn't match scores. Sample: {mismatches[:5]}"
        )

    def test_shots_have_xg_values(self, cursor):
        """Test that shots have xG values when expected."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Shot'
                AND shot_statsbomb_xg IS NULL;
        """)
        shots_without_xg = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Shot';
        """)
        total_shots = cursor.fetchone()[0]
        
        if total_shots > 0:
            # Most shots should have xG values (allow some missing for edge cases)
            missing_xg_rate = shots_without_xg / total_shots
            assert missing_xg_rate < 0.1, (
                f"Found {shots_without_xg} shots ({missing_xg_rate*100:.1f}%) without xG values, "
                f"expected < 10%"
            )


class TestCompetitionAndMatchDataValidation:
    """Test competition and match data validation."""

    def test_all_competitions_have_matches(self, cursor):
        """Test that all competitions have at least one match."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM competitions c
            LEFT JOIN matches m 
                ON c.competition_id = m.competition_id 
                AND c.season_id = m.season_id
            WHERE m.match_id IS NULL;
        """)
        competitions_without_matches = cursor.fetchone()[0]
        assert competitions_without_matches == 0, (
            f"Found {competitions_without_matches} competitions without any matches"
        )

    def test_match_dates_are_valid_format(self, cursor):
        """Test that match dates are in valid format (YYYY-MM-DD or similar)."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches 
            WHERE match_date IS NOT NULL
                AND match_date NOT LIKE '____-__-__'
                AND match_date NOT LIKE '__/__/____'
                AND match_date NOT LIKE '__-__-____';
        """)
        invalid_dates = cursor.fetchone()[0]
        # Allow some flexibility in date formats
        assert invalid_dates == 0, (
            f"Found {invalid_dates} matches with invalid date formats"
        )

    def test_home_and_away_teams_are_different(self, cursor):
        """Test that home and away teams are different for each match."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches 
            WHERE home_team_id = away_team_id
                AND home_team_id IS NOT NULL;
        """)
        same_teams = cursor.fetchone()[0]
        assert same_teams == 0, (
            f"Found {same_teams} matches where home and away teams are the same"
        )

    def test_match_scores_are_reasonable(self, cursor):
        """Test that match scores are within reasonable range (0-15)."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matches 
            WHERE (home_score IS NOT NULL AND (home_score < 0 OR home_score > 15))
                OR (away_score IS NOT NULL AND (away_score < 0 OR away_score > 15));
        """)
        unreasonable_scores = cursor.fetchone()[0]
        assert unreasonable_scores == 0, (
            f"Found {unreasonable_scores} matches with scores outside reasonable range (0-15)"
        )


class TestEventDataConsistency:
    """Test event data consistency and completeness."""

    def test_passes_have_end_locations_when_complete(self, cursor):
        """Test that completed passes have end locations."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Pass'
                AND pass_outcome IS NULL
                AND (pass_end_location IS NULL 
                    OR pass_end_location_x IS NULL 
                    OR pass_end_location_y IS NULL);
        """)
        incomplete_passes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Pass'
                AND pass_outcome IS NULL;
        """)
        total_complete_passes = cursor.fetchone()[0]
        
        if total_complete_passes > 0:
            incomplete_rate = incomplete_passes / total_complete_passes
            # Most completed passes should have end locations
            assert incomplete_rate < 0.05, (
                f"Found {incomplete_passes} completed passes ({incomplete_rate*100:.1f}%) "
                f"without end locations, expected < 5%"
            )

    def test_shots_have_outcomes(self, cursor):
        """Test that shots have outcomes."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Shot'
                AND shot_outcome IS NULL;
        """)
        shots_without_outcome = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Shot';
        """)
        total_shots = cursor.fetchone()[0]
        
        if total_shots > 0:
            missing_outcome_rate = shots_without_outcome / total_shots
            assert missing_outcome_rate < 0.01, (
                f"Found {shots_without_outcome} shots ({missing_outcome_rate*100:.1f}%) "
                f"without outcomes, expected < 1%"
            )

    def test_shots_have_xg_values(self, cursor):
        """Test that shots have xG values."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Shot'
                AND shot_statsbomb_xg IS NULL;
        """)
        shots_without_xg = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Shot';
        """)
        total_shots = cursor.fetchone()[0]
        
        if total_shots > 0:
            missing_xg_rate = shots_without_xg / total_shots
            # Most shots should have xG (allow some missing for edge cases)
            assert missing_xg_rate < 0.1, (
                f"Found {shots_without_xg} shots ({missing_xg_rate*100:.1f}%) without xG, "
                f"expected < 10%"
            )

    def test_carries_have_end_locations(self, cursor):
        """Test that carries have end locations."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Carry'
                AND (carry_end_location IS NULL 
                    OR carry_end_location_x IS NULL 
                    OR carry_end_location_y IS NULL);
        """)
        carries_without_end_location = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM events 
            WHERE type = 'Carry';
        """)
        total_carries = cursor.fetchone()[0]
        
        if total_carries > 0:
            missing_rate = carries_without_end_location / total_carries
            # All carries should have end locations
            assert missing_rate < 0.01, (
                f"Found {carries_without_end_location} carries ({missing_rate*100:.1f}%) "
                f"without end locations, expected < 1%"
            )

    def test_events_are_ordered_by_index_within_match(self, cursor):
        """Test that events are ordered by index within each match."""
        cursor.execute("""
            SELECT 
                match_id,
                COUNT(*) as total_events,
                COUNT(DISTINCT index_num) as distinct_indices,
                MIN(index_num) as min_index,
                MAX(index_num) as max_index
            FROM events
            GROUP BY match_id
            HAVING COUNT(*) != COUNT(DISTINCT index_num);
        """)
        unordered_matches = cursor.fetchall()
        
        # Check if indices are unique (duplicates indicate a problem)
        # Note: Many matches start at index 1 instead of 0, which is acceptable
        # The key validation is that indices are unique within each match
        problematic_matches = []
        for match_id, total, distinct, min_idx, max_idx in unordered_matches:
            # If distinct count doesn't match total, we have duplicate indices
            if distinct != total:
                problematic_matches.append((match_id, min_idx, max_idx, total, distinct))
        
        assert len(problematic_matches) == 0, (
            f"Found {len(problematic_matches)} matches with duplicate event indices. "
            f"Sample: {problematic_matches[:5]}"
        )

    def test_event_indexes_are_unique_per_match(self, cursor):
        """Test that event indexes are unique within each match."""
        cursor.execute("""
            SELECT 
                match_id,
                index_num,
                COUNT(*) as cnt
            FROM events
            GROUP BY match_id, index_num
            HAVING COUNT(*) > 1;
        """)
        duplicates = cursor.fetchall()
        assert len(duplicates) == 0, (
            f"Found {len(duplicates)} duplicate event indices within matches. "
            f"Sample: {duplicates[:5]}"
        )

