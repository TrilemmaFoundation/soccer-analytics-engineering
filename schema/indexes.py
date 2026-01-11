def create_indexes(c):
    """Create indexes for improved query performance."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_events_match ON events(match_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_player ON events(player_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_type ON events(type_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_team ON events(team_id);",
        "CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition_id, season_id);",
        "CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id);",
        "CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id);",
    ]

    for index_sql in indexes:
        c.execute(index_sql)
