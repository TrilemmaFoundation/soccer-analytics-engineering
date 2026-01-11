from .utils import _get_player_name_case

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
