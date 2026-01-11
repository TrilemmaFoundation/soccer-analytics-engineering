def create_indexes(c):
    """Create indexes for improved query performance."""
    indexes = [
        # Core event indexes
        "CREATE INDEX IF NOT EXISTS idx_events_match ON events(match_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_player ON events(player_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_type ON events(type_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_team ON events(team_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_possession ON events(possession_team_id);",
        
        # Match indexes
        "CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition_id, season_id);",
        "CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id);",
        "CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id);",
        "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);",
        
        # Lineup indexes
        "CREATE INDEX IF NOT EXISTS idx_lineup_players_player ON lineup_players(player_id);",
        "CREATE INDEX IF NOT EXISTS idx_lineup_players_match ON lineup_players(match_id);",
        "CREATE INDEX IF NOT EXISTS idx_lineup_positions_player ON lineup_positions(player_id);",
        "CREATE INDEX IF NOT EXISTS idx_lineup_positions_match ON lineup_positions(match_id);",
        "CREATE INDEX IF NOT EXISTS idx_lineup_cards_player ON lineup_cards(player_id);",
        "CREATE INDEX IF NOT EXISTS idx_lineup_cards_match ON lineup_cards(match_id);",
        
        # 360 data indexes
        "CREATE INDEX IF NOT EXISTS idx_360_frames_match ON three_sixty_frames(match_id);",
        "CREATE INDEX IF NOT EXISTS idx_360_positions_event ON three_sixty_positions(event_uuid);",
    ]

    for index_sql in indexes:
        c.execute(index_sql)
