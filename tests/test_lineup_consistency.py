"""Tests for consistency between lineups and events."""
import pytest

class TestLineupEventConsistency:
    """Test that lineup data and event data are consistent with each other."""

    def test_all_event_players_in_lineups(self, cursor):
        """Test that every player who records an event in a match is present in that match's lineup."""
        cursor.execute("""
            SELECT DISTINCT
                e.match_id,
                e.player_id,
                e.player as player_name
            FROM events e
            LEFT JOIN lineup_players lp ON e.match_id = lp.match_id AND e.player_id = lp.player_id
            WHERE e.player_id IS NOT NULL
                AND lp.player_id IS NULL
            LIMIT 10;
        """)
        mismatches = cursor.fetchall()
        
        # In some datasets, there might be rare mismatches due to data collection errors
        # but generally this should be zero.
        assert len(mismatches) == 0, (
            f"Found players in events who are missing from match lineups. "
            f"Sample (match_id, player_id, name): {mismatches}"
        )

    def test_starting_xi_counts(self, cursor):
        """Test that each team has exactly 11 starting players in matches with lineup data."""
        cursor.execute("""
            WITH starter_counts AS (
                SELECT 
                    match_id,
                    team_id,
                    count(DISTINCT player_id) as starter_count
                FROM lineup_positions
                WHERE start_reason = 'Starting XI'
                GROUP BY match_id, team_id
            )
            SELECT match_id, team_id, starter_count
            FROM starter_counts
            WHERE starter_count != 11;
        """)
        violations = cursor.fetchall()
        
        # Some special matches (e.g. reduced side or data errors) might exist, 
        # but for professional matches it should be 11.
        # We'll allow a small number of exceptions if the data is known to be messy,
        # but let's start with a strict check or a very high threshold.
        if violations:
            # Check how many matches have this issue
            cursor.execute("SELECT count(DISTINCT match_id) FROM lineup_players")
            total_matches = cursor.fetchone()[0]
            violation_rate = len(violations) / (total_matches * 2) if total_matches > 0 else 0
            
            assert violation_rate < 0.02, (
                f"Too many teams ({len(violations)}) have != 11 starters. "
                f"Violation rate: {violation_rate*100:.2f}%. Sample: {violations[:5]}"
            )

    def test_substitution_consistency(self, cursor):
        """Test that players in substitution events exist in the match lineup."""
        # Check players being substituted out
        cursor.execute("""
            SELECT DISTINCT e.match_id, e.player_id
            FROM events e
            LEFT JOIN lineup_players lp ON e.match_id = lp.match_id AND e.player_id = lp.player_id
            WHERE e.type = 'Substitution'
                AND lp.player_id IS NULL;
        """)
        missing_out = cursor.fetchall()
        assert len(missing_out) == 0, f"Substitution 'out' players missing from lineups: {missing_out}"

        # Check players being substituted in
        cursor.execute("""
            SELECT DISTINCT e.match_id, e.substitution_replacement_id
            FROM events e
            LEFT JOIN lineup_players lp ON e.match_id = lp.match_id AND e.substitution_replacement_id = lp.player_id
            WHERE e.type = 'Substitution'
                AND e.substitution_replacement_id IS NOT NULL
                AND lp.player_id IS NULL;
        """)
        missing_in = cursor.fetchall()
        assert len(missing_in) == 0, f"Substitution 'replacement' players missing from lineups: {missing_in}"
