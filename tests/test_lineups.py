"""Tests for lineup data and match consistency."""
import pytest

class TestLineupConsistency:
    """Test that lineup data is consistent with matches and teams."""

    def test_all_matches_have_lineups(self, cursor):
        """Test that every match in the matches table has entries in lineups."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM matches m
            LEFT JOIN lineups l ON m.match_id = l.match_id
            WHERE l.match_id IS NULL;
        """)
        matches_without_lineups = cursor.fetchone()[0]
        # Allow a few samples if data is known to be incomplete, 
        # but locally we expect high coverage.
        assert matches_without_lineups == 0, f"Found {matches_without_lineups} matches without lineups"

    def test_lineup_players_match_teams(self, cursor):
        """Test that players in lineup_players belong to one of the teams in that match."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM lineup_players lp
            JOIN matches m ON lp.match_id = m.match_id
            WHERE lp.team_id != m.home_team_id AND lp.team_id != m.away_team_id;
        """)
        mismatches = cursor.fetchone()[0]
        assert mismatches == 0, f"Found {mismatches} players assigned to teams not playing in the match"

    def test_all_lineup_players_exist_in_players_table(self, cursor):
        """Test that lineup players exist in the global players table.
        Note: Many players in lineups are substitutes who never enter the field,
        and our players table is built from event actors. 
        So we expect a substantial number of orphans if we only look at event actors.
        """
        cursor.execute("""
            SELECT COUNT(DISTINCT lp.player_id)
            FROM lineup_players lp
            LEFT JOIN players p ON lp.player_id = p.id
            WHERE p.id IS NULL;
        """)
        orphans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT player_id) FROM lineup_players;")
        total_players = cursor.fetchone()[0]
        
        # We expect a significant percentage to be non-event actors (bench players)
        if total_players > 0:
            assert orphans / total_players < 0.25, f"Too many lineup players ({orphans}/{total_players}) missing from players table"

class TestLineupTemporalIntegrity:
    """Test temporal integrity of lineup position changes."""

    def test_position_time_order(self, cursor):
        """Test that from_time is before to_time in lineup_positions."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM lineup_positions
            WHERE from_time IS NOT NULL AND to_time IS NOT NULL
            AND from_time > to_time;
        """)
        invalid_times = cursor.fetchone()[0]
        assert invalid_times == 0, f"Found {invalid_times} position records where from_time > to_time"

    def test_position_period_order(self, cursor):
        """Test that from_period is <= to_period in lineup_positions.
        Note: We observed significant noise in this field in StatsBomb data.
        """
        cursor.execute("""
            SELECT COUNT(*)
            FROM lineup_positions
            WHERE from_period IS NOT NULL AND to_period IS NOT NULL
            AND from_period > to_period;
        """)
        invalid_periods = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM lineup_positions;")
        total_positions = cursor.fetchone()[0]
        
        if total_positions > 0:
            # Allow some noise in the dataset for this specific field
            assert invalid_periods / total_positions < 0.05, f"Too many invalid period sequences ({invalid_periods}/{total_positions})"

class TestLineupCards:
    """Test consistency of cards in lineups."""

    def test_cards_have_valid_player(self, cursor):
        """Test that cards link to valid players in that match's lineup."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM lineup_cards lc
            LEFT JOIN lineup_players lp ON lc.match_id = lp.match_id 
                AND lc.player_id = lp.player_id
            WHERE lp.player_id IS NULL;
        """)
        orphans = cursor.fetchone()[0]
        assert orphans == 0, f"Found {orphans} cards for players not in the match lineup"

    def test_card_types_are_valid(self, cursor):
        """Test that card types are reasonable (Yellow Card, Red Card, etc.)."""
        cursor.execute("""
            SELECT DISTINCT card_type FROM lineup_cards;
        """)
        types = {row[0] for row in cursor.fetchall()}
        expected_types = {'Yellow Card', 'Second Yellow', 'Red Card'}
        # Some datasets might have variations, so we check if they are subset or similar
        for t in types:
            assert any(expected in t for expected in expected_types), f"Unexpected card type: {t}"
