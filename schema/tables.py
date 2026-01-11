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
