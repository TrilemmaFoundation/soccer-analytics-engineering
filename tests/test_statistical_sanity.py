"""Tests for statistical sanity and domain-specific valid ranges."""
import pytest

class TestXGCalibration:
    """Test that xG values broadly align with outcomes."""

    def test_xg_correlation(self, cursor):
        """Test that high xG shots result in more goals than low xG shots.
        This is a 'sanity check' for the data distribution.
        """
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN shot_statsbomb_xg >= 0.5 THEN 'High xG'
                    WHEN shot_statsbomb_xg <= 0.1 THEN 'Low xG'
                    ELSE 'Medium xG'
                END as bin,
                COUNT(*) as shot_count,
                SUM(CASE WHEN shot_outcome = 'Goal' THEN 1 ELSE 0 END) as goal_count
            FROM events
            WHERE type = 'Shot' AND shot_statsbomb_xg IS NOT NULL
            GROUP BY bin;
        """)
        results = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        
        if 'High xG' in results and 'Low xG' in results:
            high_rate = results['High xG'][1] / results['High xG'][0]
            low_rate = results['Low xG'][1] / results['Low xG'][0]
            
            assert high_rate > low_rate, (
                f"Statistical anomaly: Low xG shots resulted in higher goal rate ({low_rate:.2%}) "
                f"than High xG shots ({high_rate:.2%})"
            )

class TestSpatialSanity:
    """Test that events occur in physically plausible locations."""

    def test_no_own_half_shots(self, cursor):
        """Test that shots are rarely taken from the absolute defensive half (distinguished from long range).
        StatsBomb uses 0-120x, where 120 is the opponent's goal.
        """
        cursor.execute("""
            SELECT COUNT(*)
            FROM events
            WHERE type = 'Shot'
            AND location_x < 40; -- Very defensive half
        """)
        weird_shots = cursor.fetchone()[0]
        # In millions of events, we might have a few half-way line shots, but < 40 is extreme.
        # However, data might have a few outliers. We check for 'reasonable' count.
        assert weird_shots < 100, f"Found {weird_shots} shots from defensive deep half, likely location error"

class TestScoreConsistency:
    """Test that event-derived goals match match-level scores."""

    def test_event_goals_sum_matches_score(self, cursor):
        """Verify that 'Goal' events sum to match the scores in the matches table."""
        cursor.execute("""
            WITH event_goals AS (
                SELECT 
                    match_id, 
                    team_id,
                    COUNT(*) as goals
                FROM events
                WHERE type = 'Shot' AND shot_outcome = 'Goal'
                GROUP BY match_id, team_id
            ),
            match_scores AS (
                SELECT 
                    match_id, 
                    home_team_id, 
                    home_score, 
                    away_team_id, 
                    away_score
                FROM matches
            )
            SELECT 
                m.match_id,
                m.home_score,
                COALESCE(h_eg.goals, 0) as home_event_goals,
                m.away_score,
                COALESCE(a_eg.goals, 0) as away_event_goals
            FROM match_scores m
            LEFT JOIN event_goals h_eg ON m.match_id = h_eg.match_id AND m.home_team_id = h_eg.team_id
            LEFT JOIN event_goals a_eg ON m.match_id = a_eg.match_id AND m.away_team_id = a_eg.team_id
            WHERE m.home_score != home_event_goals OR m.away_score != away_event_goals;
        """)
        mismatches = cursor.fetchall()
        # In open data, own goals or penalty shootout goals might cause discrepancies.
        # We allow a small percentage of mismatch.
        cursor.execute("SELECT COUNT(*) FROM matches;")
        total_matches = cursor.fetchone()[0]
        
        if total_matches > 0:
            mismatch_rate = len(mismatches) / total_matches
            # Open data often has mismatches due to own goals or penalty shootouts not being standard shots.
            assert mismatch_rate < 0.15, f"Too many match score mismatches ({len(mismatches)}/{total_matches})"
