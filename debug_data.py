import duckdb
import json

db = duckdb.connect("stats.duckdb")
c = db.cursor()

print("--- Temporal violations sample (decreasing timestamp) ---")
c.execute("""
    WITH next AS (
        SELECT match_id, period, index_num, timestamp, 
               LEAD(timestamp) OVER (PARTITION BY match_id, period ORDER BY index_num) as next_ts 
        FROM events
    ) 
    SELECT match_id, period, index_num, timestamp, next_ts 
    FROM next 
    WHERE next_ts < timestamp 
    LIMIT 5;
""")
print(c.fetchall())

print("\n--- Red card violations sample ---")
c.execute("""
    WITH card AS (
        SELECT match_id, player_id, period, index_num 
        FROM events 
        WHERE (foul_committed_card IN ('Red Card', 'Second Yellow') 
           OR bad_behaviour_card IN ('Red Card', 'Second Yellow'))
    ) 
    SELECT e.match_id, e.player_id, e.type, e.index_num, c.index_num as card_idx 
    FROM events e 
    JOIN card c ON e.match_id = c.match_id AND e.player_id = c.player_id 
    WHERE (e.period > c.period) OR (e.period = c.period AND e.index_num > c.index_num) 
    LIMIT 5;
""")
print(c.fetchall())

print("\n--- Score mismatches sample ---")
c.execute("""
    WITH event_goals AS (
        SELECT match_id, team_id, COUNT(*) as goals
        FROM events
        WHERE type = 'Shot' AND shot_outcome = 'Goal'
        GROUP BY match_id, team_id
    ),
    match_scores AS (
        SELECT match_id, home_team_id, home_score, away_team_id, away_score
        FROM matches
    )
    SELECT m.match_id, m.home_score, COALESCE(h_eg.goals, 0), m.away_score, COALESCE(a_eg.goals, 0)
    FROM match_scores m
    LEFT JOIN event_goals h_eg ON m.match_id = h_eg.match_id AND m.home_team_id = h_eg.team_id
    LEFT JOIN event_goals a_eg ON m.match_id = a_eg.match_id AND m.away_team_id = a_eg.team_id
    WHERE m.home_score != COALESCE(h_eg.goals,0) OR m.away_score != COALESCE(a_eg.goals,0)
    LIMIT 5;
""")
print(c.fetchall())

print("\n--- DuckDB constraints ---")
c.execute("SELECT * FROM duckdb_constraints();")
print(c.fetchall())

db.close()
