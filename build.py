import schema
import duckdb
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting database build process")
    db = None
    try:
        db = duckdb.connect("stats.duckdb")
        c = db.cursor()
        logger.info("Connected to DuckDB database: stats.duckdb")

        start_time = time.time()
        setup_tables(c)
        db.commit()
        total_time = time.time() - start_time
        logger.info(f"Database build completed successfully in {total_time:.2f}s")
    except Exception as e:
        logger.error(f"Error during database build: {e}", exc_info=True)
        raise
    finally:
        if db:
            db.close()
            logger.info("Database connection closed")


def setup_tables(c):
    # =========================================================================
    # Phase 1: Create all tables
    # =========================================================================
    logger.info("Creating database tables")
    
    # Create ENUM types first (before tables that use them)
    schema._create_enum_types(c)
    
    # Core tables
    schema.make_competitions(c)
    schema.make_teams(c)
    schema.make_matches(c)
    schema.make_event_types(c)
    schema.make_players(c)
    schema.make_positions(c)
    schema.make_play_patterns(c)
    schema.make_countries(c)
    schema.make_events(c)
    
    # Lineup tables
    schema.make_lineups(c)
    schema.make_lineup_players(c)
    schema.make_lineup_positions(c)
    schema.make_lineup_cards(c)
    
    # 360 data tables
    schema.make_three_sixty_frames(c)
    schema.make_three_sixty_positions(c)
    
    logger.info("All tables created successfully")

    # =========================================================================
    # Phase 2: Load core data
    # =========================================================================
    
    # Load competitions
    logger.info("Loading competitions")
    comp_start = time.time()
    competition_count = schema.load_competitions(c)
    logger.info(f"Loaded {competition_count} competitions in {time.time() - comp_start:.2f}s")

    # Load teams from matches (deduplicated)
    logger.info("Loading teams from matches")
    teams_start = time.time()
    team_count = schema.load_teams(c)
    logger.info(f"Loaded {team_count} teams in {time.time() - teams_start:.2f}s")

    # Load matches
    logger.info("Loading matches")
    matches_start = time.time()
    match_count = schema.load_matches(c)
    logger.info(f"Loaded {match_count} matches in {time.time() - matches_start:.2f}s")

    # =========================================================================
    # Phase 3: Load reference tables and events (optimized single-pass)
    # =========================================================================
    logger.info("Loading reference tables and events (optimized single-pass ETL)")
    ref_start = time.time()
    
    # Countries (from lineups - separate data source, load independently)
    countries_count = schema.load_countries(c)
    logger.info(f"  - Loaded {countries_count} countries")
    
    # Load events - this now handles event_types, positions, play_patterns, and players
    # via a staging table approach (single JSON scan instead of 5 separate scans)
    logger.info("Loading events with extended fields (this may take a few minutes)")
    events_start = time.time()
    event_count = schema.load_events(c)
    logger.info(f"Loaded {event_count} events in {time.time() - events_start:.2f}s")
    
    # Verify reference tables were populated
    event_types_count = c.execute("SELECT COUNT(*) FROM event_types").fetchone()[0]
    positions_count = c.execute("SELECT COUNT(*) FROM positions").fetchone()[0]
    players_count = c.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    play_patterns_count = c.execute("SELECT COUNT(*) FROM play_patterns").fetchone()[0]
    logger.info(f"Reference tables populated: {event_types_count} event types, {positions_count} positions, {players_count} players, {play_patterns_count} play patterns")
    
    logger.info(f"Reference tables and events loaded in {time.time() - ref_start:.2f}s")

    # =========================================================================
    # Phase 5: Load lineup data
    # =========================================================================
    logger.info("Loading lineup data")
    lineup_start = time.time()
    
    lineup_count = schema.load_lineups(c)
    logger.info(f"  - Loaded {lineup_count} lineup records")
    
    lineup_players_count = schema.load_lineup_players(c)
    logger.info(f"  - Loaded {lineup_players_count} lineup player records")
    
    lineup_positions_count = schema.load_lineup_positions(c)
    logger.info(f"  - Loaded {lineup_positions_count} lineup position records")
    
    lineup_cards_count = schema.load_lineup_cards(c)
    logger.info(f"  - Loaded {lineup_cards_count} lineup card records")
    
    logger.info(f"Lineup data loaded in {time.time() - lineup_start:.2f}s")

    # =========================================================================
    # Phase 6: Load 360 data
    # =========================================================================
    logger.info("Loading 360 tracking data")
    threesixty_start = time.time()
    
    frames_count = schema.load_three_sixty_frames(c)
    logger.info(f"  - Loaded {frames_count} 360 frame records")
    
    positions_count = schema.load_three_sixty_positions(c)
    logger.info(f"  - Loaded {positions_count} 360 position records")
    
    logger.info(f"360 data loaded in {time.time() - threesixty_start:.2f}s")

    # =========================================================================
    # Phase 7: Create indexes
    # =========================================================================
    logger.info("Creating indexes")
    idx_start = time.time()
    schema.create_indexes(c)
    logger.info(f"Indexes created successfully in {time.time() - idx_start:.2f}s")


if __name__ == "__main__":
    main()
