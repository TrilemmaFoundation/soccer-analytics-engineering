import duckdb
import os

def export_to_parquet():
    # Define paths
    db_path = 'stats.duckdb'
    output_dir = 'parq_output'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    
    print("Starting export...")

    # 1. matches.parquet (matches + competitions)
    print("Exporting matches.parquet...")
    con.execute(f"""
        COPY (
            SELECT m.*, c.name as competition_name, c.gender, c.is_youth, c.is_international, 
                   c.country_name, c.season_name, c.match_updated, c.match_available_360
            FROM matches m
            JOIN competitions c ON m.competition_id = c.competition_id AND m.season_id = c.season_id
        ) TO '{output_dir}/matches.parquet' (FORMAT PARQUET);
    """)

    # 2. events.parquet (already denormalized)
    print("Exporting events.parquet...")
    con.execute(f"COPY events TO '{output_dir}/events.parquet' (FORMAT PARQUET);")

    # 3. lineups.parquet (lineups + players + positions + cards)
    print("Exporting lineups.parquet...")
    # Using LEFT JOINs to ensure we don't lose players who might not have cards or position changes recorded
    con.execute(f"""
        COPY (
            SELECT 
                lp.*,
                l.team_name,
                pos.position_name, pos.from_time, pos.to_time, pos.from_period, pos.to_period,
                c.card_time, c.card_type, c.reason as card_reason
            FROM lineup_players lp
            JOIN lineups l ON lp.match_id = l.match_id AND lp.team_id = l.team_id
            LEFT JOIN lineup_positions pos ON lp.match_id = pos.match_id AND lp.team_id = pos.team_id AND lp.player_id = pos.player_id
            LEFT JOIN lineup_cards c ON lp.match_id = c.match_id AND lp.team_id = c.team_id AND lp.player_id = c.player_id
        ) TO '{output_dir}/lineups.parquet' (FORMAT PARQUET);
    """)

    # 4. three_sixty.parquet (frames + positions)
    print("Exporting three_sixty.parquet...")
    con.execute(f"""
        COPY (
            SELECT f.match_id, p.*, f.visible_area
            FROM three_sixty_positions p
            JOIN three_sixty_frames f ON p.event_uuid = f.event_uuid
        ) TO '{output_dir}/three_sixty.parquet' (FORMAT PARQUET);
    """)

    # 5. reference.parquet (consolidated lookups)
    print("Exporting reference.parquet...")
    con.execute(f"""
        COPY (
            SELECT 'team' as table_name, id, name, gender as extra_info FROM teams
            UNION ALL
            SELECT 'player' as table_name, id, name, NULL as extra_info FROM players
            UNION ALL
            SELECT 'position' as table_name, id, name, NULL as extra_info FROM positions
            UNION ALL
            SELECT 'event_type' as table_name, id, name, NULL as extra_info FROM event_types
            UNION ALL
            SELECT 'play_pattern' as table_name, id, name, NULL as extra_info FROM play_patterns
            UNION ALL
            SELECT 'country' as table_name, id, name, NULL as extra_info FROM countries
        ) TO '{output_dir}/reference.parquet' (FORMAT PARQUET);
    """)

    print(f"Export completed. Files are in '{output_dir}/'")
    con.close()

if __name__ == "__main__":
    export_to_parquet()
