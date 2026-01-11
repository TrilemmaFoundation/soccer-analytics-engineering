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
    # Create all tables
    logger.info("Creating database tables")
    schema.make_competitions(c)
    schema.make_teams(c)
    schema.make_matches(c)
    schema.make_event_types(c)
    schema.make_players(c)
    schema.make_positions(c)
    schema.make_play_patterns(c)
    schema.make_events(c)

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

    # Load reference tables from events
    logger.info("Loading reference tables (event_types, players, etc.) from events")
    ref_start = time.time()
    
    # Event types
    schema.load_event_types(c)
    
    # Positions
    schema.load_positions(c)
    
    # Play patterns
    schema.load_play_patterns(c)
    
    # Players (with canonicalization)
    schema.load_players(c)
    
    logger.info(f"Loaded reference tables in {time.time() - ref_start:.2f}s")

    # Load events
    logger.info("Loading events (this may take a minute)")
    events_start = time.time()
    # Use read_json_auto but handle optional fields by checking parent struct exists first
    event_count = schema.load_events(c)
    logger.info(f"Loaded {event_count} events in {time.time() - events_start:.2f}s")

    # Create indexes
    logger.info("Creating indexes")
    idx_start = time.time()
    schema.create_indexes(c)
    logger.info(f"Indexes created successfully in {time.time() - idx_start:.2f}s")


if __name__ == "__main__":
    main()
