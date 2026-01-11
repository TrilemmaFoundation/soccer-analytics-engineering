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
            country_name        TEXT,
            season_name         TEXT,
            match_updated       TEXT,
            match_available_360 TEXT,

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


def make_countries(c):
    """Reference table for countries."""
    c.execute(
        """
        DROP TABLE IF EXISTS countries;
        CREATE TABLE countries (
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

            -- Shot Attributes
                shot_end_location       TEXT,
                shot_end_location_x     REAL,
                shot_end_location_y     REAL,
                shot_end_location_z     REAL,
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

            -- Pass Attributes
                pass_end_location       TEXT,
                pass_end_location_x     REAL,
                pass_end_location_y     REAL,
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

            -- Carry Attributes
                carry_end_location      TEXT,
                carry_end_location_x    REAL,
                carry_end_location_y    REAL,

            -- Dribble Attributes
                dribble_outcome         TEXT,
                dribble_nutmeg          BOOL,
                dribble_overrun         BOOL,
                dribble_no_touch        BOOL,

            -- Duel Attributes
                duel_type               TEXT,
                duel_outcome            TEXT,

            -- Foul Committed Attributes
                foul_committed_card     TEXT,
                foul_committed_type     TEXT,
                foul_committed_offensive    BOOL,
                foul_committed_advantage    BOOL,
                foul_committed_penalty      BOOL,

            -- Foul Won Attributes
                foul_won_defensive      BOOL,
                foul_won_advantage      BOOL,
                foul_won_penalty        BOOL,

            -- Goalkeeper Attributes
                goalkeeper_type             TEXT,
                goalkeeper_outcome          TEXT,
                goalkeeper_technique        TEXT,
                goalkeeper_position         TEXT,
                goalkeeper_body_part        TEXT,
                goalkeeper_end_location     TEXT,
                goalkeeper_end_location_x   REAL,
                goalkeeper_end_location_y   REAL,

            -- Clearance Attributes
                clearance_body_part         TEXT,
                clearance_aerial_won        BOOL,
                clearance_head              BOOL,
                clearance_left_foot         BOOL,
                clearance_right_foot        BOOL,

            -- Interception Attributes
                interception_outcome        TEXT,

            -- Block Attributes
                block_deflection            BOOL,
                block_offensive             BOOL,
                block_save_block            BOOL,

            -- Ball Recovery Attributes
                ball_recovery_offensive     BOOL,
                ball_recovery_failure       BOOL,

            -- Miscontrol Attributes
                miscontrol_aerial_won       BOOL,

            -- Substitution Attributes
                substitution_replacement_id     INTEGER,
                substitution_replacement_name   TEXT,
                substitution_outcome            TEXT,

            -- 50/50 Attributes
                fifty_fifty_outcome         TEXT,

            -- Bad Behaviour Attributes
                bad_behaviour_card          TEXT,

            -- Injury Stoppage Attributes
                injury_stoppage_in_chain    BOOL,
            
            FOREIGN KEY (type_id)               REFERENCES event_types(id),
            FOREIGN KEY (match_id)              REFERENCES matches(match_id),
            FOREIGN KEY (team_id)               REFERENCES teams(id),
            FOREIGN KEY (player_id)             REFERENCES players(id),
            FOREIGN KEY (position_id)           REFERENCES positions(id),
            FOREIGN KEY (possession_team_id)    REFERENCES teams(id),
            FOREIGN KEY (pass_recipient_id)     REFERENCES players(id)
            -- Note: substitution_replacement_id intentionally has no FK constraint
            -- because replacement players may not appear as event actors in the players table
        );
        """
    )


# =============================================================================
# Lineup Tables
# =============================================================================

def make_lineups(c):
    """Match-team lineup relationship table."""
    c.execute(
        """
        DROP TABLE IF EXISTS lineups;
        CREATE TABLE lineups (
            match_id    INTEGER,
            team_id     INTEGER,
            team_name   TEXT,
            
            PRIMARY KEY (match_id, team_id),
            FOREIGN KEY (match_id) REFERENCES matches(match_id),
            FOREIGN KEY (team_id)  REFERENCES teams(id)
        );
        """
    )


def make_lineup_players(c):
    """Individual player entries for each match lineup."""
    c.execute(
        """
        DROP TABLE IF EXISTS lineup_players;
        CREATE TABLE lineup_players (
            match_id        INTEGER,
            team_id         INTEGER,
            player_id       INTEGER,
            player_name     TEXT,
            player_nickname TEXT,
            jersey_number   INTEGER,
            country_id      INTEGER,
            country_name    TEXT,
            
            PRIMARY KEY (match_id, team_id, player_id),
            FOREIGN KEY (match_id, team_id) REFERENCES lineups(match_id, team_id)
            -- Note: player_id and country_id intentionally have no FK constraints
            -- because lineup players may not appear as event actors
        );
        """
    )


def make_lineup_positions(c):
    """Dynamic position changes throughout a match."""
    c.execute(
        """
        DROP SEQUENCE IF EXISTS lineup_positions_seq;
        CREATE SEQUENCE lineup_positions_seq START 1;
        
        DROP TABLE IF EXISTS lineup_positions;
        CREATE TABLE lineup_positions (
            id              INTEGER PRIMARY KEY DEFAULT nextval('lineup_positions_seq'),
            match_id        INTEGER,
            team_id         INTEGER,
            player_id       INTEGER,
            position_id     INTEGER,
            position_name   TEXT,
            from_time       TEXT,
            to_time         TEXT,
            from_period     INTEGER,
            to_period       INTEGER,
            start_reason    TEXT,
            end_reason      TEXT,
            
            FOREIGN KEY (match_id, team_id) REFERENCES lineups(match_id, team_id)
        );
        """
    )


def make_lineup_cards(c):
    """Cards issued during matches."""
    c.execute(
        """
        DROP SEQUENCE IF EXISTS lineup_cards_seq;
        CREATE SEQUENCE lineup_cards_seq START 1;
        
        DROP TABLE IF EXISTS lineup_cards;
        CREATE TABLE lineup_cards (
            id              INTEGER PRIMARY KEY DEFAULT nextval('lineup_cards_seq'),
            match_id        INTEGER,
            team_id         INTEGER,
            player_id       INTEGER,
            card_time       TEXT,
            card_type       TEXT,
            reason          TEXT,
            period          INTEGER,
            
            FOREIGN KEY (match_id, team_id) REFERENCES lineups(match_id, team_id)
        );
        """
    )


# =============================================================================
# 360 Data Tables
# =============================================================================

def make_three_sixty_frames(c):
    """Frame-level metadata with visible area polygon."""
    c.execute(
        """
        DROP TABLE IF EXISTS three_sixty_frames;
        CREATE TABLE three_sixty_frames (
            event_uuid      TEXT PRIMARY KEY,
            match_id        INTEGER,
            visible_area    TEXT,
            
            FOREIGN KEY (event_uuid) REFERENCES events(id),
            FOREIGN KEY (match_id)   REFERENCES matches(match_id)
        );
        """
    )


def make_three_sixty_positions(c):
    """Individual player positions within each 360 frame."""
    c.execute(
        """
        DROP SEQUENCE IF EXISTS three_sixty_positions_seq;
        CREATE SEQUENCE three_sixty_positions_seq START 1;
        
        DROP TABLE IF EXISTS three_sixty_positions;
        CREATE TABLE three_sixty_positions (
            id              INTEGER PRIMARY KEY DEFAULT nextval('three_sixty_positions_seq'),
            event_uuid      TEXT,
            teammate        BOOL,
            actor           BOOL,
            keeper          BOOL,
            location_x      REAL,
            location_y      REAL,
            
            FOREIGN KEY (event_uuid) REFERENCES three_sixty_frames(event_uuid)
        );
        """
    )
