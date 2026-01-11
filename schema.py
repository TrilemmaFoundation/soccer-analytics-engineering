def make_competitions(c):
    c.execute(
        """
        DROP TABLE IF EXISTS competitions;
        CREATE TABLE competitions (
            competition_id      INTEGER,
            season_id           INTEGER,
            name                TEXT,
            gender              TEXT,
            is_youth            BOOL,
            is_international    BOOL,

            PRIMARY KEY (competition_id, season_id)
        );
        """
    )


def make_matches(c):
    c.execute(
        """
        DROP TABLE IF EXISTS matches;
        CREATE TABLE matches (
            match_id                INTEGER PRIMARY KEY,
            match_date              TEXT,
            match_week              INTEGER,
            match_status            TEXT,
            match_status_360        TEXT,
            kickoff                 TEXT,
            home_score              INTEGER,
            away_score              INTEGER,

            -- Competitions
            competition_id          INTEGER,
            competition             TEXT,
            competition_stage       TEXT,
            season_id               INTEGER,
            season                  TEXT,

            -- Teams
            home_team_id            INTEGER,
            home_team               TEXT,
            home_managers           TEXT,
            away_team_id            INTEGER,
            away_team               TEXT,
            away_managers           TEXT,

            -- Stadium
            stadium_id              INTEGER,
            stadium                 TEXT,

            -- Referees
            referee_id              INTEGER,
            referee                 TEXT,

            -- Metadata
            last_updated            TEXT,
            last_updated_360        TEXT,
            data_version            TEXT,
            shot_fidelity_version   TEXT,
            xy_fidelity_version     TEXT,

            FOREIGN KEY (competition_id, season_id) REFERENCES competitions (competition_id, season_id),
            FOREIGN KEY (home_team_id)              REFERENCES teams(id),
            FOREIGN KEY (away_team_id)              REFERENCES teams(id)
        );
        """
    )


def make_teams(c):
    c.execute(
        """
        DROP TABLE IF EXISTS teams;
        CREATE TABLE teams (
            id      INTEGER PRIMARY KEY,
            name    TEXT,
            gender  TEXT
        );
        """
    )


def make_event_types(c):
    c.execute(
        """
        DROP TABLE IF EXISTS event_types;
        CREATE TABLE event_types (
            id      INTEGER PRIMARY KEY,
            name    TEXT
        );
        """
    )


def make_players(c):
    c.execute(
        """
        DROP TABLE IF EXISTS players;
        CREATE TABLE players (
            id      INTEGER PRIMARY KEY,
            name    TEXT
        );
        """
    )


def make_positions(c):
    c.execute(
        """
        DROP TABLE IF EXISTS positions;
        CREATE TABLE positions (
            id      INTEGER PRIMARY KEY,
            name    TEXT
        );
        """
    )


def make_play_patterns(c):
    c.execute(
        """
        DROP TABLE IF EXISTS play_patterns;
        CREATE TABLE play_patterns (
            id      INTEGER PRIMARY KEY,
            name    TEXT
        );
        """
    )


def make_events(c):
    c.execute(
        """
        DROP TABLE IF EXISTS events;
        CREATE TABLE events (
            -- Core Attributes
                id                      TEXT PRIMARY KEY,
                index_num               INTEGER,

                -- Time
                period                  INTEGER,
                minute                  INTEGER,
                second                  INTEGER,
                timestamp               TEXT,
                duration                REAL,

                -- Location
                location                TEXT,
                location_x              REAL,
                location_y              REAL,

                -- Possession
                possession              INTEGER,
                possession_team_id      INTEGER,
                possession_team         TEXT,

                -- Flags
                out                     BOOL,
                off_camera              BOOL,
                counterpress            BOOL,
                under_pressure          BOOL,

                -- Enums
                type_id                 INTEGER,
                type                    TEXT,
                match_id                INTEGER,
                team_id                 INTEGER,
                team                    TEXT,
                player_id               INTEGER,
                player                  TEXT,
                position_id             INTEGER,
                position                TEXT,
                play_pattern_id         INTEGER,
                play_pattern            TEXT,

            -- Custom Attributes
                -- Shot
                shot_end_location       TEXT,
                shot_statsbomb_xg       REAL,
                shot_outcome            TEXT,
                shot_technique          TEXT,
                shot_body_part          TEXT,
                shot_type               TEXT,
                shot_key_pass_id        TEXT,
                shot_freeze_frame       TEXT,

                -- Shot Flags
                shot_first_time         BOOL,
                shot_deflected          BOOL,
                shot_aerial_won         BOOL,
                shot_follows_dribble    BOOL,
                shot_one_on_one         BOOL,
                shot_open_goal          BOOL,
                shot_redirect           BOOL,
                shot_saved_off_target   BOOL,
                shot_saved_to_post      BOOL,

                -- Pass
                pass_end_location       TEXT,
                pass_end_location_x     REAL,
                pass_end_location_y     REAL,

                -- TODO: This should ideally be upserted, since it's a player.
                pass_recipient_id       INTEGER,
                pass_recipient          TEXT,

                pass_length             REAL,
                pass_angle              REAL,
                pass_height             TEXT,
                pass_body_part          TEXT,
                pass_type               TEXT,
                pass_outcome            TEXT,
                pass_technique          TEXT,
                pass_assisted_shot_id   TEXT,

                -- Pass Flags
                pass_goal_assist        BOOL,
                pass_shot_assist        BOOL,
                pass_cross              BOOL,
                pass_switch             BOOL,
                pass_through_ball       BOOL,
                pass_aerial_won         BOOL,
                pass_deflected          BOOL,
                pass_inswinging         BOOL,
                pass_outswinging        BOOL,
                pass_no_touch           BOOL,
                pass_cut_back           BOOL,
                pass_straight           BOOL,
                pass_miscommunication   BOOL,

                -- Carry
                carry_end_location      TEXT,
                carry_end_location_x    REAL,
                carry_end_location_y    REAL,
            
            FOREIGN KEY (type_id)               REFERENCES event_types(id),
            FOREIGN KEY (match_id)              REFERENCES matches(match_id),
            FOREIGN KEY (team_id)               REFERENCES teams(id),
            FOREIGN KEY (player_id)             REFERENCES players(id),
            FOREIGN KEY (position_id)           REFERENCES positions(id),
            FOREIGN KEY (possession_team_id)    REFERENCES teams(id),
            FOREIGN KEY (pass_recipient_id)     REFERENCES players(id)
        );
        """
    )


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


# Data Loading Functions

def start_loading(c, table_name, file_pattern, columns, json_format='array', distinct=False, extra_clauses=""):
    """Generic helper might be too complex given the strict SQL.
    We will stick to explicit functions for clarity as per user request for "succinct" but "organized".
    """
    pass

def load_competitions(c):
    c.execute("""
        INSERT INTO competitions 
        SELECT 
            competition_id,
            season_id,
            competition_name as name,
            competition_gender as gender,
            competition_youth as is_youth,
            competition_international as is_international
        FROM read_json_auto('./open-data/data/competitions.json');
    """)
    return c.execute("SELECT COUNT(*) FROM competitions").fetchone()[0]


def load_teams(c):
    c.execute("""
        INSERT INTO teams
        SELECT DISTINCT 
            home_team.home_team_id as id,
            home_team.home_team_name as name,
            home_team.home_team_gender as gender
        FROM read_json_auto('./open-data/data/matches/**/*.json', format='array')
        WHERE home_team.home_team_id IS NOT NULL
        
        UNION
        
        SELECT DISTINCT 
            away_team.away_team_id as id,
            away_team.away_team_name as name,
            away_team.away_team_gender as gender
        FROM read_json_auto('./open-data/data/matches/**/*.json', format='array')
        WHERE away_team.away_team_id IS NOT NULL;
    """)
    return c.execute("SELECT COUNT(*) FROM teams").fetchone()[0]


def load_matches(c):
    c.execute("""
        INSERT INTO matches
        SELECT 
            match_id,
            match_date,
            match_week,
            match_status,
            match_status_360,
            kick_off as kickoff,
            home_score,
            away_score,
            competition.competition_id,
            competition.competition_name as competition,
            competition_stage.name as competition_stage,
            season.season_id,
            season.season_name as season,
            home_team.home_team_id as home_team_id,
            home_team.home_team_name as home_team,
            CASE 
                WHEN home_team.managers IS NOT NULL THEN json(home_team.managers)
                ELSE NULL
            END as home_managers,
            away_team.away_team_id as away_team_id,
            away_team.away_team_name as away_team,
            CASE 
                WHEN away_team.managers IS NOT NULL THEN json(away_team.managers)
                ELSE NULL
            END as away_managers,
            stadium.id as stadium_id,
            stadium.name as stadium,
            referee.id as referee_id,
            referee.name as referee,
            last_updated,
            last_updated_360,
            metadata.data_version as data_version,
            metadata.shot_fidelity_version as shot_fidelity_version,
            metadata.xy_fidelity_version as xy_fidelity_version
        FROM read_json_auto('./open-data/data/matches/**/*.json', format='array');
    """)
    return c.execute("SELECT COUNT(*) FROM matches").fetchone()[0]


def load_event_types(c):
    c.execute("""
        INSERT INTO event_types
        SELECT DISTINCT 
            type.id,
            type.name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE type.id IS NOT NULL;
    """)


def load_positions(c):
    c.execute("""
        INSERT INTO positions
        SELECT DISTINCT 
            position.id,
            position.name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE position.id IS NOT NULL;
    """)


def load_play_patterns(c):
    c.execute("""
        INSERT INTO play_patterns
        SELECT DISTINCT 
            play_pattern.id,
            play_pattern.name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE play_pattern.id IS NOT NULL;
    """)


def _get_player_name_case():
    return """
        CASE player.id
            WHEN 4354 THEN 'Philip Foden'
            WHEN 25742 THEN 'Karly Roestbakken'
            WHEN 25546 THEN 'Cheyna Lee Matthews'
            WHEN 4951 THEN 'Quinn'
            WHEN 5082 THEN 'Marta Vieira da Silva'
            WHEN 18617 THEN 'Mykola Matviyenko'
            WHEN 3961 THEN 'N''Golo Kanté'
            WHEN 5659 THEN 'Khadim N''Diaye'
            WHEN 401453 THEN 'David Ngog'
            WHEN 184468 THEN 'Álvaro Zamora'
            ELSE player.name
        END
    """


def load_players(c):
    case_stmt = _get_player_name_case()
    c.execute(f"""
        INSERT INTO players
        SELECT DISTINCT 
            player.id,
            {case_stmt} as name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE player.id IS NOT NULL;
    """)


def load_events(c):
    case_stmt = _get_player_name_case()
    c.execute(f"""
        INSERT INTO events
        SELECT 
            id,
            "index" as index_num,
            period,
            minute,
            second,
            timestamp,
            duration,
            CASE 
                WHEN location IS NOT NULL THEN json(location)
                ELSE NULL
            END as location,
            location[1]::DOUBLE as location_x,
            location[2]::DOUBLE as location_y,
            possession,
            possession_team.id as possession_team_id,
            possession_team.name as possession_team,
            COALESCE("out", false) as out,
            COALESCE(off_camera, false) as off_camera,
            COALESCE(counterpress, false) as counterpress,
            COALESCE(under_pressure, false) as under_pressure,
            type.id as type_id,
            type.name as type,
            CAST(regexp_extract(filename, '([0-9]+)\\.json$', 1) AS INTEGER) as match_id,
            team.id as team_id,
            team.name as team,
            player.id as player_id,
            {case_stmt} as player,
            position.id as position_id,
            position.name as position,
            play_pattern.id as play_pattern_id,
            play_pattern.name as play_pattern,
            -- Shot fields (check if shot exists before accessing optional fields)
            CASE 
                WHEN shot.end_location IS NOT NULL THEN json(shot.end_location)
                ELSE NULL
            END as shot_end_location,
            shot.statsbomb_xg as shot_statsbomb_xg,
            shot.outcome.name as shot_outcome,
            shot.technique.name as shot_technique,
            shot.body_part.name as shot_body_part,
            shot.type.name as shot_type,
            shot.key_pass_id as shot_key_pass_id,
            CASE 
                WHEN shot.freeze_frame IS NOT NULL THEN json(shot.freeze_frame)
                ELSE NULL
            END as shot_freeze_frame,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.first_time')::BOOLEAN, false) ELSE false END as shot_first_time,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.deflected')::BOOLEAN, false) ELSE false END as shot_deflected,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.aerial_won')::BOOLEAN, false) ELSE false END as shot_aerial_won,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.follows_dribble')::BOOLEAN, false) ELSE false END as shot_follows_dribble,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.one_on_one')::BOOLEAN, false) ELSE false END as shot_one_on_one,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.open_goal')::BOOLEAN, false) ELSE false END as shot_open_goal,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.redirect')::BOOLEAN, false) ELSE false END as shot_redirect,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.saved_off_target')::BOOLEAN, false) ELSE false END as shot_saved_off_target,
            CASE WHEN shot IS NOT NULL THEN COALESCE(json_extract(json(shot), '$.saved_to_post')::BOOLEAN, false) ELSE false END as shot_saved_to_post,
            -- Pass fields
            CASE 
                WHEN pass.end_location IS NOT NULL THEN json(pass.end_location)
                ELSE NULL
            END as pass_end_location,
            pass.end_location[1]::DOUBLE as pass_end_location_x,
            pass.end_location[2]::DOUBLE as pass_end_location_y,
            pass.recipient.id as pass_recipient_id,
            pass.recipient.name as pass_recipient,
            pass.length as pass_length,
            pass.angle as pass_angle,
            pass.height.name as pass_height,
            pass.body_part.name as pass_body_part,
            pass.type.name as pass_type,
            pass.outcome.name as pass_outcome,
            pass.technique.name as pass_technique,
            pass.assisted_shot_id as pass_assisted_shot_id,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.goal_assist')::BOOLEAN, false) ELSE false END as pass_goal_assist,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.shot_assist')::BOOLEAN, false) ELSE false END as pass_shot_assist,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.cross')::BOOLEAN, false) ELSE false END as pass_cross,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.switch')::BOOLEAN, false) ELSE false END as pass_switch,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.through_ball')::BOOLEAN, false) ELSE false END as pass_through_ball,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.aerial_won')::BOOLEAN, false) ELSE false END as pass_aerial_won,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.deflected')::BOOLEAN, false) ELSE false END as pass_deflected,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.inswinging')::BOOLEAN, false) ELSE false END as pass_inswinging,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.outswinging')::BOOLEAN, false) ELSE false END as pass_outswinging,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.no_touch')::BOOLEAN, false) ELSE false END as pass_no_touch,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.cut_back')::BOOLEAN, false) ELSE false END as pass_cut_back,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.straight')::BOOLEAN, false) ELSE false END as pass_straight,
            CASE WHEN pass IS NOT NULL THEN COALESCE(json_extract(json(pass), '$.miscommunication')::BOOLEAN, false) ELSE false END as pass_miscommunication,
            -- Carry fields
            CASE 
                WHEN carry.end_location IS NOT NULL THEN json(carry.end_location)
                ELSE NULL
            END as carry_end_location,
            carry.end_location[1]::DOUBLE as carry_end_location_x,
            carry.end_location[2]::DOUBLE as carry_end_location_y
        FROM read_json_auto('./open-data/data/events/*.json', format='array', filename=true);
    """)
    return c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
