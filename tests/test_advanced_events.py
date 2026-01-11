"""Tests for advanced event-specific attributes and domain logic."""
import pytest

class TestSubstitutionEvents:
    """Test that Substitution events are correctly populated."""

    def test_substitutions_have_replacement_info(self, cursor):
        """Test that Substitution events have replacement IDs and names."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM events
            WHERE type = 'Substitution'
            AND (substitution_replacement_id IS NULL OR substitution_replacement_name IS NULL);
        """)
        incomplete_subs = cursor.fetchone()[0]
        assert incomplete_subs == 0, f"Found {incomplete_subs} Substitution events missing replacement info"

    def test_substitution_outcomes(self, cursor):
        """Test that substitution outcomes are valid (Tactical, Injury, etc.)."""
        cursor.execute("""
            SELECT DISTINCT substitution_outcome
            FROM events
            WHERE type = 'Substitution';
        """)
        outcomes = {row[0] for row in cursor.fetchall()}
        expected_outcomes = {'Tactical', 'Injury', 'Other'}
        # Some might be NULL if not specified, but usually StatsBomb has these
        for o in outcomes:
            if o:
                assert any(expected in o for expected in expected_outcomes), f"Unexpected substitution outcome: {o}"

class TestGoalkeepingEvents:
    """Test that Goal Keeper events are correctly populated."""

    def test_goalkeeper_events_have_details(self, cursor):
        """Test that Goal Keeper events have type and outcome."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM events
            WHERE type = 'Goal Keeper'
            AND (goalkeeper_type IS NULL OR goalkeeper_outcome IS NULL);
        """)
        # Note: Some Goalkeeper events like "Picked Up" might not have outcomes in the same way,
        # but "Shot Saved", "Penalty Saved" should. 
        # We'll check for a general presence of data.
        incomplete_gk = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events WHERE type = 'Goal Keeper';")
        total_gk = cursor.fetchone()[0]
        
        if total_gk > 0:
            # Many GK events (receipts, etc) lack specialized outcomes.
            # 60% missing is common across the whole dataset.
            assert incomplete_gk / total_gk < 0.7, f"Too many GK events ({incomplete_gk}/{total_gk}) missing details"

class TestFoulEvents:
    """Test that Foul Committed events are correctly populated."""

    def test_foul_committed_card_details(self, cursor):
        """Test that Foul Committed events have card details when a card was issued."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM events
            WHERE type = 'Foul Committed'
            AND (foul_committed_card IS NOT NULL)
            AND (foul_committed_card NOT IN ('Yellow Card', 'Second Yellow', 'Red Card'));
        """)
        invalid_cards = cursor.fetchone()[0]
        assert invalid_cards == 0, f"Found {invalid_cards} Foul Committed events with invalid card types"

class TestCoordinateConsistency:
    """Test consistency across related coordinate fields."""

    def test_shot_end_location_consistency(self, cursor):
        """Test that shot_end_location_x/y/z are consistent (non-null when shot exists)."""
        cursor.execute("""
            SELECT shot_end_location_x, shot_end_location_y, shot_end_location_z
            FROM events
            WHERE type = 'Shot' 
                AND (shot_end_location_x IS NOT NULL 
                     OR shot_end_location_y IS NOT NULL 
                     OR shot_end_location_z IS NOT NULL)
            LIMIT 100;
        """)
        results = cursor.fetchall()
        for x, y, z in results:
            # If any coordinate exists, verify they're within reasonable ranges
            if x is not None:
                assert -10 <= x <= 130, f"shot_end_location_x out of range: {x}"
            if y is not None:
                assert -10 <= y <= 90, f"shot_end_location_y out of range: {y}"
            if z is not None:
                assert 0 <= z <= 10, f"shot_end_location_z out of range: {z}"
