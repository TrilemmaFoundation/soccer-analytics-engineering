import os
import json
import glob
from .utils import _get_player_name_case


def _get_valid_json_files(pattern):
    """Filter out malformed JSON files from a glob pattern."""
    valid_files = []
    for f in glob.glob(pattern, recursive=True):
        try:
            with open(f, 'r') as file:
                json.load(file)
            valid_files.append(f)
        except:
            continue
    return valid_files


def load_competitions(c):
    """Load competitions with extended fields."""
    c.execute("""
        INSERT INTO competitions 
        SELECT 
            competition_id,
            season_id,
            competition_name as name,
            competition_gender as gender,
            competition_youth as is_youth,
            competition_international as is_international,
            country_name,
            season_name,
            match_updated,
            match_available_360
        FROM read_json_auto('./open-data/data/competitions.json');
    """)
    return c.execute("SELECT COUNT(*) FROM competitions").fetchone()[0]


def load_teams(c):
    """Load teams from match files."""
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
    """Load match data."""
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
    """Load event type reference data."""
    c.execute("""
        INSERT INTO event_types
        SELECT DISTINCT 
            type.id,
            type.name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE type.id IS NOT NULL;
    """)


def load_positions(c):
    """Load position reference data."""
    c.execute("""
        INSERT INTO positions
        SELECT DISTINCT 
            position.id,
            position.name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE position.id IS NOT NULL;
    """)


def load_play_patterns(c):
    """Load play pattern reference data."""
    c.execute("""
        INSERT INTO play_patterns
        SELECT DISTINCT 
            play_pattern.id,
            play_pattern.name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE play_pattern.id IS NOT NULL;
    """)


def load_players(c):
    """Load player reference data with canonicalized names."""
    case_stmt = _get_player_name_case()
    c.execute(f"""
        INSERT INTO players
        SELECT DISTINCT 
            player.id,
            {case_stmt} as name
        FROM read_json_auto('./open-data/data/events/*.json', format='array')
        WHERE player.id IS NOT NULL;
    """)


def load_countries(c):
    """Load country reference data from lineups."""
    c.execute("""
        INSERT INTO countries
        SELECT DISTINCT 
            player.country.id,
            player.country.name
        FROM (
            SELECT UNNEST(lineup) as player
            FROM read_json_auto('./open-data/data/lineups/*.json', format='array')
        )
        WHERE player.country.id IS NOT NULL;
    """)
    return c.execute("SELECT COUNT(*) FROM countries").fetchone()[0]


def load_events(c):
    """Load events with comprehensive field extraction for all event types."""
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
            -- Location
            CASE 
                WHEN location IS NOT NULL THEN json(location)
                ELSE NULL
            END as location,
            location[1]::DOUBLE as location_x,
            location[2]::DOUBLE as location_y,
            -- Possession
            possession,
            possession_team.id as possession_team_id,
            possession_team.name as possession_team,
            -- Flags
            COALESCE("out", false) as out,
            COALESCE(off_camera, false) as off_camera,
            COALESCE(counterpress, false) as counterpress,
            COALESCE(under_pressure, false) as under_pressure,
            -- Type and match info
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
            
            -- Shot fields
            CASE 
                WHEN shot.end_location IS NOT NULL THEN json(shot.end_location)
                ELSE NULL
            END as shot_end_location,
            shot.end_location[1]::DOUBLE as shot_end_location_x,
            shot.end_location[2]::DOUBLE as shot_end_location_y,
            shot.end_location[3]::DOUBLE as shot_end_location_z,
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
            -- Shot flags
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
            -- Pass flags
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
            carry.end_location[2]::DOUBLE as carry_end_location_y,
            
            -- Dribble fields
            dribble.outcome.name as dribble_outcome,
            CASE WHEN dribble IS NOT NULL THEN COALESCE(json_extract(json(dribble), '$.nutmeg')::BOOLEAN, false) ELSE false END as dribble_nutmeg,
            CASE WHEN dribble IS NOT NULL THEN COALESCE(json_extract(json(dribble), '$.overrun')::BOOLEAN, false) ELSE false END as dribble_overrun,
            CASE WHEN dribble IS NOT NULL THEN COALESCE(json_extract(json(dribble), '$.no_touch')::BOOLEAN, false) ELSE false END as dribble_no_touch,
            
            -- Duel fields
            duel.type.name as duel_type,
            duel.outcome.name as duel_outcome,
            
            -- Foul Committed fields
            foul_committed.card.name as foul_committed_card,
            foul_committed.type.name as foul_committed_type,
            CASE WHEN foul_committed IS NOT NULL THEN COALESCE(json_extract(json(foul_committed), '$.offensive')::BOOLEAN, false) ELSE false END as foul_committed_offensive,
            CASE WHEN foul_committed IS NOT NULL THEN COALESCE(json_extract(json(foul_committed), '$.advantage')::BOOLEAN, false) ELSE false END as foul_committed_advantage,
            CASE WHEN foul_committed IS NOT NULL THEN COALESCE(json_extract(json(foul_committed), '$.penalty')::BOOLEAN, false) ELSE false END as foul_committed_penalty,
            
            -- Foul Won fields
            CASE WHEN foul_won IS NOT NULL THEN COALESCE(json_extract(json(foul_won), '$.defensive')::BOOLEAN, false) ELSE false END as foul_won_defensive,
            CASE WHEN foul_won IS NOT NULL THEN COALESCE(json_extract(json(foul_won), '$.advantage')::BOOLEAN, false) ELSE false END as foul_won_advantage,
            CASE WHEN foul_won IS NOT NULL THEN COALESCE(json_extract(json(foul_won), '$.penalty')::BOOLEAN, false) ELSE false END as foul_won_penalty,
            
            -- Goalkeeper fields
            goalkeeper.type.name as goalkeeper_type,
            goalkeeper.outcome.name as goalkeeper_outcome,
            goalkeeper.technique.name as goalkeeper_technique,
            goalkeeper.position.name as goalkeeper_position,
            goalkeeper.body_part.name as goalkeeper_body_part,
            CASE 
                WHEN goalkeeper.end_location IS NOT NULL THEN json(goalkeeper.end_location)
                ELSE NULL
            END as goalkeeper_end_location,
            goalkeeper.end_location[1]::DOUBLE as goalkeeper_end_location_x,
            goalkeeper.end_location[2]::DOUBLE as goalkeeper_end_location_y,
            
            -- Clearance fields
            clearance.body_part.name as clearance_body_part,
            CASE WHEN clearance IS NOT NULL THEN COALESCE(json_extract(json(clearance), '$.aerial_won')::BOOLEAN, false) ELSE false END as clearance_aerial_won,
            CASE WHEN clearance IS NOT NULL THEN COALESCE(json_extract(json(clearance), '$.head')::BOOLEAN, false) ELSE false END as clearance_head,
            CASE WHEN clearance IS NOT NULL THEN COALESCE(json_extract(json(clearance), '$.left_foot')::BOOLEAN, false) ELSE false END as clearance_left_foot,
            CASE WHEN clearance IS NOT NULL THEN COALESCE(json_extract(json(clearance), '$.right_foot')::BOOLEAN, false) ELSE false END as clearance_right_foot,
            
            -- Interception fields
            interception.outcome.name as interception_outcome,
            
            -- Block fields
            CASE WHEN block IS NOT NULL THEN COALESCE(json_extract(json(block), '$.deflection')::BOOLEAN, false) ELSE false END as block_deflection,
            CASE WHEN block IS NOT NULL THEN COALESCE(json_extract(json(block), '$.offensive')::BOOLEAN, false) ELSE false END as block_offensive,
            CASE WHEN block IS NOT NULL THEN COALESCE(json_extract(json(block), '$.save_block')::BOOLEAN, false) ELSE false END as block_save_block,
            
            -- Ball Recovery fields
            CASE WHEN ball_recovery IS NOT NULL THEN COALESCE(json_extract(json(ball_recovery), '$.offensive')::BOOLEAN, false) ELSE false END as ball_recovery_offensive,
            CASE WHEN ball_recovery IS NOT NULL THEN COALESCE(json_extract(json(ball_recovery), '$.recovery_failure')::BOOLEAN, false) ELSE false END as ball_recovery_failure,
            
            -- Miscontrol fields
            CASE WHEN miscontrol IS NOT NULL THEN COALESCE(json_extract(json(miscontrol), '$.aerial_won')::BOOLEAN, false) ELSE false END as miscontrol_aerial_won,
            
            -- Substitution fields
            substitution.replacement.id as substitution_replacement_id,
            substitution.replacement.name as substitution_replacement_name,
            substitution.outcome.name as substitution_outcome,
            
            -- 50/50 fields
            "50_50".outcome.name as fifty_fifty_outcome,
            
            -- Bad Behaviour fields
            bad_behaviour.card.name as bad_behaviour_card,
            
            -- Injury Stoppage fields
            CASE WHEN injury_stoppage IS NOT NULL THEN COALESCE(json_extract(json(injury_stoppage), '$.in_chain')::BOOLEAN, false) ELSE false END as injury_stoppage_in_chain
            
        FROM read_json_auto('./open-data/data/events/*.json', format='array', filename=true);
    """)
    return c.execute("SELECT COUNT(*) FROM events").fetchone()[0]


# =============================================================================
# Lineup Loaders
# =============================================================================

def load_lineups(c):
    """Load lineup team-level data."""
    c.execute("""
        INSERT INTO lineups
        SELECT DISTINCT
            CAST(regexp_extract(filename, '([0-9]+)\\.json$', 1) AS INTEGER) as match_id,
            team_id,
            team_name
        FROM read_json_auto('./open-data/data/lineups/*.json', format='array', filename=true);
    """)
    return c.execute("SELECT COUNT(*) FROM lineups").fetchone()[0]


def load_lineup_players(c):
    """Load individual player entries for each match lineup."""
    c.execute("""
        INSERT INTO lineup_players
        SELECT DISTINCT
            CAST(regexp_extract(filename, '([0-9]+)\\.json$', 1) AS INTEGER) as match_id,
            team_id,
            player.player_id,
            player.player_name,
            player.player_nickname,
            player.jersey_number,
            player.country.id as country_id,
            player.country.name as country_name
        FROM (
            SELECT filename, team_id, UNNEST(lineup) as player
            FROM read_json_auto('./open-data/data/lineups/*.json', format='array', filename=true)
        );
    """)
    return c.execute("SELECT COUNT(*) FROM lineup_players").fetchone()[0]


def load_lineup_positions(c):
    """Load dynamic position changes throughout matches."""
    c.execute("""
        INSERT INTO lineup_positions (match_id, team_id, player_id, position_id, position_name, 
                                       from_time, to_time, from_period, to_period, start_reason, end_reason)
        SELECT
            CAST(regexp_extract(filename, '([0-9]+)\\.json$', 1) AS INTEGER) as match_id,
            team_id,
            player_id,
            pos.position_id,
            pos.position as position_name,
            pos."from" as from_time,
            pos."to" as to_time,
            pos.from_period,
            pos.to_period,
            pos.start_reason,
            pos.end_reason
        FROM (
            SELECT filename, team_id, player.player_id, UNNEST(player.positions) as pos
            FROM (
                SELECT filename, team_id, UNNEST(lineup) as player
                FROM read_json_auto('./open-data/data/lineups/*.json', format='array', filename=true)
            )
        )
        WHERE pos.position_id IS NOT NULL;
    """)
    return c.execute("SELECT COUNT(*) FROM lineup_positions").fetchone()[0]


def load_lineup_cards(c):
    """Load cards issued during matches."""
    c.execute("""
        INSERT INTO lineup_cards (match_id, team_id, player_id, card_time, card_type, reason, period)
        SELECT
            CAST(regexp_extract(filename, '([0-9]+)\\.json$', 1) AS INTEGER) as match_id,
            team_id,
            player_id,
            card.time as card_time,
            card.card_type,
            card.reason,
            card.period
        FROM (
            SELECT filename, team_id, player.player_id, UNNEST(player.cards) as card
            FROM (
                SELECT filename, team_id, UNNEST(lineup) as player
                FROM read_json_auto('./open-data/data/lineups/*.json', format='array', filename=true)
            )
        )
        WHERE card.card_type IS NOT NULL;
    """)
    return c.execute("SELECT COUNT(*) FROM lineup_cards").fetchone()[0]


# =============================================================================
# 360 Data Loaders
# =============================================================================

def load_three_sixty_frames(c):
    """Load 360 frame-level metadata."""
    valid_files = _get_valid_json_files('./open-data/data/three-sixty/*.json')
    if not valid_files:
        return 0
        
    c.execute(f"""
        INSERT INTO three_sixty_frames
        SELECT
            event_uuid,
            CAST(regexp_extract(filename, '([0-9]+)\\.json$', 1) AS INTEGER) as match_id,
            CASE 
                WHEN visible_area IS NOT NULL THEN json(visible_area)
                ELSE NULL
            END as visible_area
        FROM read_json_auto({valid_files}, format='array', filename=true);
    """)
    return c.execute("SELECT COUNT(*) FROM three_sixty_frames").fetchone()[0]


def load_three_sixty_positions(c):
    """Load individual player positions within 360 frames."""
    valid_files = _get_valid_json_files('./open-data/data/three-sixty/*.json')
    if not valid_files:
        return 0
        
    c.execute(f"""
        INSERT INTO three_sixty_positions (event_uuid, teammate, actor, keeper, location_x, location_y)
        SELECT
            event_uuid,
            pos.teammate,
            pos.actor,
            pos.keeper,
            pos.location[1]::DOUBLE as location_x,
            pos.location[2]::DOUBLE as location_y
        FROM (
            SELECT event_uuid, UNNEST(freeze_frame) as pos
            FROM read_json_auto({valid_files}, format='array', filename=true)
        );
    """)
    return c.execute("SELECT COUNT(*) FROM three_sixty_positions").fetchone()[0]
