# StatsBomb DuckDB Database Specification

## Overview

This document provides a comprehensive specification for the StatsBomb DuckDB database (`stats.duckdb`), which contains football/soccer event data from [StatsBomb Open Data](https://github.com/statsbomb/open-data) in a normalized, queryable format.

### Database Details

- **Format**: DuckDB
- **Database File**: `stats.duckdb` (created by `build.py`)
- **Data Source**: StatsBomb Open Data repository
- **License**: CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial)
- **Schema Version**: Defined in `schema/tables.py`

## Database Schema

### Core Tables

#### 1. `competitions` - Competition Metadata

**Purpose**: Stores competition and season information

| Column                | Type    | Constraints                    | Description                    |
| --------------------- | ------- | ------------------------------ | ------------------------------ |
| `competition_id`      | INTEGER | PRIMARY KEY                    | Unique competition identifier  |
| `season_id`           | INTEGER | PRIMARY KEY                    | Unique season identifier       |
| `name`                | TEXT    |                                | Competition name               |
| `gender`              | TEXT    |                                | Competition gender (male/female) |
| `is_youth`            | BOOLEAN |                                | Youth competition flag         |
| `is_international`    | BOOLEAN |                                | International competition flag |
| `country_name`        | TEXT    |                                | Country name                   |
| `season_name`         | TEXT    |                                | Season name (e.g. "2023/2024") |
| `match_updated`       | TEXT    |                                | Last competition update time   |
| `match_available_360` | TEXT    |                                | Availability of 360 tracking data |

**Primary Key**: (`competition_id`, `season_id`)

#### 2. `matches` - Match Metadata

**Purpose**: Stores match information and results

| Column                  | Type    | Constraints | Description                  |
| ----------------------- | ------- | ----------- | ---------------------------- |
| `match_id`              | INTEGER | PRIMARY KEY | Unique match identifier      |
| `match_date`            | TEXT    |             | Match date (YYYY-MM-DD)      |
| `match_week`            | INTEGER |             | Match week number            |
| `match_status`          | TEXT    |             | Data availability status     |
| `match_status_360`      | TEXT    |             | 360° data availability       |
| `kickoff`               | TEXT    |             | Kick-off time (HH:MM:SS.sss) |
| `home_score`            | INTEGER |             | Final home team score        |
| `away_score`            | INTEGER |             | Final away team score        |
| `competition_id`        | INTEGER | FOREIGN KEY | References competitions      |
| `competition`           | TEXT    |             | Competition name             |
| `competition_stage`     | TEXT    |             | Competition stage            |
| `season_id`             | INTEGER | FOREIGN KEY | References competitions      |
| `season`                | TEXT    |             | Season identifier            |
| `home_team_id`          | INTEGER | FOREIGN KEY | References teams            |
| `home_team`             | TEXT    |             | Home team name               |
| `home_managers`         | TEXT    |             | Home team managers (JSON)    |
| `away_team_id`          | INTEGER | FOREIGN KEY | References teams            |
| `away_team`             | TEXT    |             | Away team name               |
| `away_managers`         | TEXT    |             | Away team managers (JSON)    |
| `stadium_id`            | INTEGER |             | Stadium identifier           |
| `stadium`               | TEXT    |             | Stadium name                 |
| `referee_id`            | INTEGER |             | Referee identifier           |
| `referee`               | TEXT    |             | Referee name                 |
| `last_updated`          | TEXT    |             | Last data update timestamp   |
| `last_updated_360`      | TEXT    |             | Last 360° data update        |
| `data_version`          | TEXT    |             | StatsBomb data version       |
| `shot_fidelity_version` | TEXT    |             | Shot data version            |
| `xy_fidelity_version`   | TEXT    |             | Position data version        |

**Foreign Keys**: 
- (`competition_id`, `season_id`) → `competitions`
- `home_team_id` → `teams`
- `away_team_id` → `teams`

#### 3. `teams` - Team Information

**Purpose**: Stores team metadata

| Column | Type    | Constraints | Description |
| ------ | ------- | ----------- | ----------- |
| `id`   | INTEGER | PRIMARY KEY | Team ID     |
| `name` | TEXT    |             | Team name   |
| `gender` | TEXT  |             | Team gender |

#### 4. `event_types` - Event Type Lookup

**Purpose**: Maps event type IDs to names

| Column | Type    | Constraints | Description           |
| ------ | ------- | ----------- | --------------------- |
| `id`   | INTEGER | PRIMARY KEY | Event type ID         |
| `name` | TEXT    |             | Event type name       |

Common event types include: Pass, Shot, Carry, Dribble, Pressure, Ball Recovery, Duel, Clearance, Block, Goal Keeper, etc.

#### 5. `players` - Player Information

**Purpose**: Stores player metadata

| Column | Type    | Constraints | Description |
| ------ | ------- | ----------- | ----------- |
| `id`   | INTEGER | PRIMARY KEY | Player ID   |
| `name` | TEXT    |             | Player name |

#### 6. `positions` - Position Lookup

**Purpose**: Maps position IDs to names

| Column | Type    | Constraints | Description     |
| ------ | ------- | ----------- | --------------- |
| `id`   | INTEGER | PRIMARY KEY | Position ID     |
| `name` | TEXT    |             | Position name   |

#### 7. `play_patterns` - Play Pattern Lookup

**Purpose**: Maps play pattern IDs to names

| `id`   | INTEGER | PRIMARY KEY | Play pattern ID    |
| `name` | TEXT    |             | Play pattern name   |

#### 8. `countries` - Country Lookup

**Purpose**: Maps country IDs to names

| Column | Type    | Constraints | Description |
| ------ | ------- | ----------- | ----------- |
| `id`   | INTEGER | PRIMARY KEY | Country ID  |
| `name` | TEXT    |             | Country name |

#### 9. `events` - Match Events

**Purpose**: Detailed event data for all matches (passes, shots, tackles, etc.)

##### Core Event Fields

| Column               | Type    | Constraints | Description                                 |
| -------------------- | ------- | ----------- | ------------------------------------------- |
| `id`                 | TEXT    | PRIMARY KEY | Unique event identifier                     |
| `index_num`          | INTEGER |             | Event sequence number in match              |
| `period`             | INTEGER |             | Match period (1=1st half, 2=2nd half, etc.) |
| `minute`             | INTEGER |             | Minute of occurrence                        |
| `second`             | INTEGER |             | Second of occurrence                        |
| `timestamp`          | TEXT    |             | Precise timestamp (MM:SS.sss)               |
| `duration`           | REAL    |             | Event duration (seconds)                    |
| `location`           | TEXT    |             | Event coordinates [x, y] (JSON)            |
| `location_x`         | REAL    |             | X coordinate (yards)                        |
| `location_y`         | REAL    |             | Y coordinate (yards)                        |
| `possession`         | INTEGER |             | Possession sequence number                  |
| `possession_team_id` | INTEGER | FOREIGN KEY | Team ID in possession                       |
| `possession_team`    | TEXT    |             | Team name in possession                     |
| `out`                | BOOLEAN |             | Ball out of play flag                       |
| `off_camera`         | BOOLEAN |             | Event off camera flag                       |
| `counterpress`       | BOOLEAN |             | Counterpress flag                           |
| `under_pressure`     | BOOLEAN |             | Under pressure flag                         |
| `type_id`            | INTEGER | FOREIGN KEY | References event_types                      |
| `type`               | TEXT    |             | Event type name                             |
| `match_id`           | INTEGER | FOREIGN KEY | References matches                          |
| `team_id`            | INTEGER | FOREIGN KEY | References teams                            |
| `team`               | TEXT    |             | Team performing action                      |
| `player_id`          | INTEGER | FOREIGN KEY | References players                          |
| `player`             | TEXT    |             | Player name                                 |
| `position_id`        | INTEGER | FOREIGN KEY | References positions                        |
| `position`           | TEXT    |             | Player position                             |
| `play_pattern_id`    | INTEGER | FOREIGN KEY | References play_patterns                     |
| `play_pattern`       | TEXT    |             | Play pattern name                           |

##### Shot-Specific Fields

| Column                  | Type        | Description                              |
| ----------------------- | ----------- | ---------------------------------------- |
| `shot_end_location_x`   | REAL        | Shot end X coordinate                    |
| `shot_end_location_y`   | REAL        | Shot end Y coordinate                    |
| `shot_end_location_z`   | REAL        | Shot end Z coordinate                    |
| `shot_statsbomb_xg`     | REAL        | Expected goals value (0.0-1.0)           |
| `shot_outcome`          | ENUM        | Shot result (Goal, Saved, Blocked, etc.) - see `shot_outcome_enum` |
| `shot_technique`        | TEXT        | Shot technique (Normal, Volley, etc.)    |
| `shot_body_part`        | TEXT        | Body part used                           |
| `shot_type`             | TEXT        | Shot type (Open Play, Penalty, etc.)     |
| `shot_key_pass_id`      | TEXT        | Key pass ID                              |
| `shot_freeze_frame`     | TEXT (JSON) | Player positions at shot moment          |
| `shot_first_time`       | BOOLEAN     | First time shot flag                     |
| `shot_deflected`        | BOOLEAN     | Deflection flag                          |
| `shot_aerial_won`       | BOOLEAN     | Aerial duel won flag                     |
| `shot_follows_dribble`  | BOOLEAN     | Follows dribble flag                     |
| `shot_one_on_one`       | BOOLEAN     | One-on-one situation flag                |
| `shot_open_goal`        | BOOLEAN     | Open goal flag                           |
| `shot_redirect`         | BOOLEAN     | Redirect flag                            |
| `shot_saved_off_target` | BOOLEAN     | Saved off target flag                     |
| `shot_saved_to_post`    | BOOLEAN     | Saved to post flag                       |

##### Pass-Specific Fields

| Column                  | Type        | Description                                        |
| ----------------------- | ----------- | -------------------------------------------------- |
| `pass_end_location_x`   | REAL        | Pass end X coordinate                              |
| `pass_end_location_y`   | REAL        | Pass end Y coordinate                              |
| `pass_recipient_id`     | INTEGER     | Receiving player ID                                |
| `pass_recipient`        | TEXT        | Receiving player name                              |
| `pass_length`           | REAL        | Pass distance (yards)                              |
| `pass_angle`            | REAL        | Pass angle (radians)                               |
| `pass_height`           | TEXT        | Pass height (Ground Pass, High Pass, Low Pass)     |
| `pass_body_part`        | TEXT        | Body part used (Left Foot, Right Foot, Head, etc.) |
| `pass_type`             | TEXT        | Pass type (Corner, Throw-in, Free Kick, etc.)      |
| `pass_outcome`          | ENUM        | Pass result (Incomplete, Out, etc.) - see `pass_outcome_enum` |
| `pass_technique`        | TEXT        | Pass technique (Inswinging, Outswinging, etc.)     |
| `pass_assisted_shot_id` | TEXT        | Linked shot ID if assist                           |
| `pass_goal_assist`      | BOOLEAN     | Goal assist flag                                   |
| `pass_shot_assist`      | BOOLEAN     | Shot assist flag                                   |
| `pass_cross`            | BOOLEAN     | Cross flag                                         |
| `pass_switch`           | BOOLEAN     | Switch play flag                                   |
| `pass_through_ball`     | BOOLEAN     | Through ball flag                                  |
| `pass_aerial_won`       | BOOLEAN     | Aerial duel won flag                               |
| `pass_deflected`        | BOOLEAN     | Deflection flag                                    |
| `pass_inswinging`       | BOOLEAN     | Inswinging flag                                    |
| `pass_outswinging`      | BOOLEAN     | Outswinging flag                                   |
| `pass_no_touch`         | BOOLEAN     | No touch flag                                      |
| `pass_cut_back`         | BOOLEAN     | Cut back flag                                      |
| `pass_straight`         | BOOLEAN     | Straight pass flag                                 |
| `pass_miscommunication` | BOOLEAN    | Miscommunication flag                              |

##### Carry-Specific Fields

| Column                  | Type        | Description                 |
| ----------------------- | ----------- | --------------------------- |
| `carry_end_location_x`  | REAL        | Carry end X coordinate      |
| `carry_end_location_y`  | REAL        | Carry end Y coordinate      |

##### Dribble Attributes
| Column | Type | Description |
| --- | --- | --- |
| `dribble_overrun` | BOOLEAN | Dribbled ball too far flag |
| `dribble_nutmeg` | BOOLEAN | Nutmeg flag |
| `dribble_outcome` | TEXT | Result (Complete, Incomplete) |
| `dribble_no_touch` | BOOLEAN | Dribbled without touching ball flag |

##### Duel Attributes
| Column | Type | Description |
| --- | --- | --- |
| `duel_type` | TEXT | Duel type (Tackle, Aerial Lost, etc.) |
| `duel_outcome` | TEXT | Duel result (Won, Lost, Neutral, etc.) |

##### Foul Attributes
| Column | Type | Description |
| --- | --- | --- |
| `foul_committed_offensive` | BOOLEAN | Offensive foul flag |
| `foul_committed_type` | TEXT | Foul type (Handball, Professional, etc.) |
| `foul_committed_advantage` | BOOLEAN | Advantage played flag |
| `foul_committed_penalty` | BOOLEAN | Penalty conceded flag |
| `foul_committed_card` | TEXT | Card issued (Yellow, Red, etc.) |
| `foul_won_advantage` | BOOLEAN | Advantage won flag |
| `foul_won_penalty` | BOOLEAN | Penalty won flag |
| `foul_won_defensive` | BOOLEAN | Defensive foul won flag |

##### Goalkeeper Attributes
| Column | Type | Description |
| --- | --- | --- |
| `goalkeeper_type` | TEXT | Action type (Save, Punch, etc.) |
| `goalkeeper_outcome` | TEXT | Action result (Success, Failure, etc.) |
| `goalkeeper_body_part` | TEXT | Body part used |
| `goalkeeper_technique` | TEXT | Technique (Diving, Standing, etc.) |
| `goalkeeper_position` | TEXT | GK position (Set, Moving, etc.) |
| `goalkeeper_end_location_x` | REAL | Action end X coordinate |
| `goalkeeper_end_location_y` | REAL | Action end Y coordinate |

##### Other Event Attributes
| Column | Category | Type | Description |
| --- | --- | --- | --- |
| `clearance_aerial_won` | Clearance | BOOLEAN | Aerial duel won during clearance |
| `clearance_body_part` | Clearance | TEXT | Body part used for clearance |
| `clearance_head` | Clearance | BOOLEAN | Headed clearance flag |
| `clearance_left_foot` | Clearance | BOOLEAN | Left foot used flag |
| `clearance_right_foot` | Clearance | BOOLEAN | Right foot used flag |
| `interception_outcome` | Interception | TEXT | Interception result |
| `block_deflection` | Block | BOOLEAN | Shot deflection flag |
| `block_offensive` | Block | BOOLEAN | Offensive block flag |
| `block_save_block` | Block | BOOLEAN | Save block flag |
| `ball_recovery_offensive` | Ball Recovery | BOOLEAN | Offensive recovery flag |
| `ball_recovery_failure` | Ball Recovery | BOOLEAN | Recovery failure flag |
| `miscontrol_aerial_won` | Miscontrol | BOOLEAN | Aerial duel won during miscontrol |
| `substitution_replacement_id` | Substitution | INTEGER | Replacement player ID |
| `substitution_replacement_name` | Substitution | TEXT | Replacement player name |
| `substitution_outcome` | Substitution | TEXT | Substitution result |
| `fifty_fifty_outcome` | 50/50 | TEXT | 50/50 result |
| `bad_behaviour_card` | Bad Behaviour | TEXT | Card for bad behaviour |
| `injury_stoppage_in_chain` | Injury Stoppage | BOOLEAN | In-possession injury flag |

**Foreign Keys**:
- `type_id` → `event_types(id)`
- `match_id` → `matches(match_id)`
- `team_id` → `teams(id)`
- `player_id` → `players(id)`
- `position_id` → `positions(id)`
- `possession_team_id` → `teams(id)`
- `pass_recipient_id` → `players(id)`

### Lineup Tables

#### 10. `lineups` - Match-Team Lineup Relationships
**Purpose**: Links teams to matches for roster tracking.
| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `match_id` | INTEGER | PRIMARY KEY, FK | Reference to matches |
| `team_id` | INTEGER | PRIMARY KEY, FK | Reference to teams |
| `team_name` | TEXT | | Team name |

#### 11. `lineup_players` - Match-Team Player Rosters
**Purpose**: Individual player entries for each match lineup.
| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `match_id` | INTEGER | PRIMARY KEY, FK | Reference to lineups |
| `team_id` | INTEGER | PRIMARY KEY, FK | Reference to lineups |
| `player_id` | INTEGER | PRIMARY KEY | Player ID |
| `player_name` | TEXT | | Full player name |
| `player_nickname`| TEXT | | Player nickname |
| `jersey_number` | INTEGER | | Match jersey number |
| `country_id` | INTEGER | | Country ID |
| `country_name` | TEXT | | Country name |

#### 12. `lineup_positions` - Dynamic Position Changes
**Purpose**: Tracks where players actually played during a match.
| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary Key (Auto-increment) |
| `match_id` | INTEGER | Reference to lineups |
| `team_id` | INTEGER | Reference to lineups |
| `player_id` | INTEGER | Player ID |
| `position_id` | INTEGER | Position ID |
| `position_name` | TEXT | Position name |
| `from_time` | TEXT | Start time (MM:SS) |
| `to_time` | TEXT | End time (MM:SS) |
| `from_period` | INTEGER | Start period |
| `to_period` | INTEGER | End period |
| `start_reason` | TEXT | Reason for starting position |
| `end_reason` | TEXT | Reason for ending position |

#### 13. `lineup_cards` - Match Discipline
**Purpose**: Record of cards issued during a match.
| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary Key (Auto-increment) |
| `match_id` | INTEGER | Reference to lineups |
| `team_id` | INTEGER | Reference to lineups |
| `player_id` | INTEGER | Player ID |
| `card_time` | TEXT | Time of card |
| `card_type` | TEXT | Yellow, Red, etc. |
| `reason` | TEXT | Reason for card |
| `period` | INTEGER | Match period |

### 360 Tracking Data Tables

#### 14. `three_sixty_frames` - Frame Metadata
**Purpose**: Metadata for 360 tracking frames.
| Column | Type | Description |
| --- | --- | --- |
| `event_uuid` | TEXT | PRIMARY KEY, FK | Reference to events |
| `match_id` | INTEGER | | Match ID |
| `visible_area` | TEXT (JSON) | Polygon coordinates of camera view |

#### 15. `three_sixty_positions` - Player Tracking Positions
**Purpose**: High-resolution spatial data for players at moment of event.
| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary Key (Auto-increment) |
| `event_uuid` | TEXT | FK | Reference to three_sixty_frames |
| `teammate` | BOOLEAN | Is teammate of event actor |
| `actor` | BOOLEAN | Is event actor |
| `keeper` | BOOLEAN | Is goalkeeper |
| `location_x` | REAL | Player X coordinate |
| `location_y` | REAL | Player Y coordinate |

## Data Types and Conventions

### Coordinate System

- **Field Dimensions**: 120 yards (width) × 80 yards (height)
- **Origin**: Bottom-left corner (0, 0)
- **Goals**: Located at x=0 (left goal) and x=120 (right goal)
- **Storage Format**: Coordinates are stored as separate REAL columns (`location_x`, `location_y`, etc.) for optimal query performance
- **Coordinate Columns**: Use `location_x`, `location_y` for event locations; `shot_end_location_x/y/z` for shot targets; similar patterns for passes, carries, and goalkeeper actions

### Location Coordinates

**Note**: Redundant JSON location columns have been removed for storage efficiency. Use the extracted coordinate columns directly:

- `location_x`, `location_y` - Event location coordinates
- `shot_end_location_x`, `shot_end_location_y`, `shot_end_location_z` - Shot end coordinates
- `pass_end_location_x`, `pass_end_location_y` - Pass end coordinates
- `carry_end_location_x`, `carry_end_location_y` - Carry end coordinates
- `goalkeeper_end_location_x`, `goalkeeper_end_location_y` - Goalkeeper action end coordinates

The only JSON fields remaining are:
- `shot_freeze_frame` - Player positions at shot moment (complex nested structure)
- `visible_area` - Polygon coordinates for 360° tracking (in `three_sixty_frames` table)

### ENUM Types

The database uses ENUM types for low-cardinality categorical columns to improve storage efficiency and query performance:

- **`shot_outcome_enum`**: 8 distinct values
  - Values: `'Blocked'`, `'Goal'`, `'Off T'`, `'Post'`, `'Saved'`, `'Saved Off Target'`, `'Saved to Post'`, `'Wayward'`
  - Used in: `events.shot_outcome`

- **`pass_outcome_enum`**: 5 distinct values
  - Values: `'Incomplete'`, `'Injury Clearance'`, `'Out'`, `'Pass Offside'`, `'Unknown'`
  - Used in: `events.pass_outcome`

When querying ENUM columns, use the exact string values (case-sensitive). ENUM types provide better compression and faster comparisons than TEXT columns.

### Boolean Fields

All boolean values are stored as BOOLEAN type:
- `0` or `NULL` = False/No
- `1` = True/Yes

## Indexes

The database includes 21 indexes created by `schema/indexes.py` to optimize query performance:

### Events Table Indexes

#### Single-Column Indexes
| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_events_match` | `match_id` | Fast filtering by match |
| `idx_events_player` | `player_id` | Fast player-based queries |
| `idx_events_type` | `type_id` | Fast filtering by event type |
| `idx_events_team` | `team_id` | Fast team-based queries |
| `idx_events_possession` | `possession_team_id` | Rapid possession sequence retrieval |

#### Composite Indexes (Optimized for Common Query Patterns)
| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_events_match_type` | `match_id`, `type_id` | Fast filtering by match and event type |
| `idx_events_match_player` | `match_id`, `player_id` | Fast player actions per match queries |
| `idx_events_player_type` | `player_id`, `type_id` | Fast player-specific event type queries |
| `idx_events_type_shot_outcome` | `type_id`, `shot_outcome` | Optimized shot outcome analysis |

### Matches Table Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_matches_competition` | `competition_id`, `season_id` | Fast filtering by competition/season |
| `idx_matches_home_team` | `home_team_id` | Fast home team lookups |
| `idx_matches_away_team` | `away_team_id` | Fast away team lookups |
| `idx_matches_date` | `match_date` | Fast sorting and filtering by match date |

### Lineup Table Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_lineup_players_match` | `match_id` | Fast roster retrieval per match |
| `idx_lineup_players_player`| `player_id` | Track player history across matches |
| `idx_lineup_positions_match`| `match_id` | Fast position history lookup |
| `idx_lineup_positions_player`| `player_id` | Track player position history |
| `idx_lineup_cards_match` | `match_id` | Disciplinary analysis per match |
| `idx_lineup_cards_player`| `player_id` | Track player discipline history |

### 360 Tracking Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_360_frames_match` | `match_id` | Fast tracking data retrieval per match |
| `idx_360_positions_event` | `event_uuid` | Rapid retrieval of freeze frames per event |

These indexes are automatically created during the database build process and significantly improve query performance for common access patterns.

## Player Canonicalization

To ensure consistency in player names across the database, certain player names are canonicalized during the build process. This handles cases where StatsBomb data may have inconsistent name formatting or special characters.

### Canonicalized Players

The following player IDs have standardized names applied:

| Player ID | Canonicalized Name |
|-----------|-------------------|
| 4354 | Philip Foden |
| 25742 | Karly Roestbakken |
| 25546 | Cheyna Lee Matthews |
| 4951 | Quinn |
| 5082 | Marta Vieira da Silva |
| 18617 | Mykola Matviyenko |
| 3961 | N'Golo Kanté |
| 5659 | Khadim N'Diaye |
| 401453 | David Ngog |
| 184468 | Álvaro Zamora |

### Implementation

Canonicalization is applied in two places during `build.py`:

1. **Players table**: When inserting into the `players` table, player names are normalized using a CASE statement that maps player IDs to their canonical names.

2. **Events table**: When inserting events, the `player` field (denormalized name) is also canonicalized to match the players table.

This ensures that:
- Player names are consistent across all tables
- Queries filtering by player name will work correctly
- Player aggregations will not be split due to name variations

The canonicalization mapping is defined in `build.py` and can be extended as needed when new name inconsistencies are discovered.

## Query Examples

### Basic Queries

#### Get match information

```sql
SELECT home_team, away_team, home_score, away_score, match_date, competition, season
FROM matches
ORDER BY match_date;
```

#### Count events by type

```sql
SELECT type, COUNT(*) as count
FROM events
GROUP BY type
ORDER BY count DESC;
```

#### Find all goals

```sql
SELECT player, team, minute, second, shot_statsbomb_xg
FROM events
WHERE type = 'Shot' AND shot_outcome = 'Goal'
ORDER BY match_id, minute, second;
```

### Advanced Analytics

#### Top goal scorers

```sql
SELECT
    player,
    team,
    COUNT(*) as goals,
    AVG(shot_statsbomb_xg) as avg_xg
FROM events
WHERE type = 'Shot' AND shot_outcome = 'Goal'
GROUP BY player, team
ORDER BY goals DESC, avg_xg DESC;
```

#### Pass completion rates by team

```sql
SELECT
    team,
    COUNT(*) as total_passes,
    SUM(CASE WHEN pass_outcome IS NULL THEN 1 ELSE 0 END) as completed_passes,
    ROUND(SUM(CASE WHEN pass_outcome IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_rate
FROM events
WHERE type = 'Pass'
GROUP BY team
ORDER BY completion_rate DESC;
```

#### Heat map data for a player

```sql
SELECT
    location_x as x,
    location_y as y,
    COUNT(*) as event_count
FROM events
WHERE player = 'Player Name'
AND location_x IS NOT NULL
AND location_y IS NOT NULL
GROUP BY x, y
ORDER BY event_count DESC;
```

## Performance Optimizations

### ETL Performance

The database build process has been optimized with a **single-pass ETL** approach:

- **Staging Table Pattern**: Events JSON files are loaded once into a staging table, then reference tables (event_types, positions, players, play_patterns) are extracted from the staging table
- **Result**: 3-4x faster build times compared to multiple JSON scans
- **Schema Handling**: Uses `union_by_name=true` to handle varying JSON schemas across different event types

### Query Optimization

- **Use indexes**: The database includes 21 indexes including composite indexes for common query patterns (see [Indexes](#indexes) section above). Filter on indexed columns (`match_id`, `type_id`, `player_id`, `team_id`) when possible
- **Composite indexes**: Take advantage of composite indexes like `(match_id, type_id)` for queries filtering on multiple columns
- **Filter early**: Apply WHERE clauses before JOINs and aggregations
- **Coordinate efficiency**: Use extracted coordinate columns (`location_x`, `location_y`) directly - JSON location columns have been removed for better performance
- **ENUM types**: Categorical columns (`shot_outcome`, `pass_outcome`) use ENUM types for better storage efficiency
- **Consider query result caching**: For complex analytics that are run repeatedly

### Memory Usage

- DuckDB loads database pages into memory as needed
- Large result sets may require chunking
- JSON extraction can be memory intensive for large datasets
- Consider using LIMIT clauses for exploration queries

## Data Quality and Validation

### Data Integrity Checks

```sql
-- Check for orphaned events
SELECT COUNT(*) FROM events e
LEFT JOIN matches m ON e.match_id = m.match_id
WHERE m.match_id IS NULL;

-- Validate coordinate ranges
SELECT COUNT(*) FROM events
WHERE location_x < 0 OR location_x > 120
   OR location_y < 0 OR location_y > 80;

-- Check xG value ranges
SELECT MIN(shot_statsbomb_xg), MAX(shot_statsbomb_xg), AVG(shot_statsbomb_xg)
FROM events
WHERE shot_statsbomb_xg IS NOT NULL;
```

## Usage Guidelines

### Best Practices

1. **Always use indexes**: Filter on indexed columns (match_id, type_id, player_id) when possible. Use composite indexes for multi-column filters
2. **Coordinate efficiency**: Use `location_x` and `location_y` columns directly - JSON location columns have been removed
3. **ENUM types**: When filtering by `shot_outcome` or `pass_outcome`, use the exact ENUM values (case-sensitive)
4. **Coordinate validation**: Check coordinate bounds (0-120, 0-80) for spatial analysis
5. **Time analysis**: Combine minute and second for precise timing
6. **Memory management**: Use LIMIT clauses for large queries
7. **Data validation**: Always check for NULL values in optional fields

### Common Pitfalls

1. **Boolean interpretation**: Remember boolean encoding for flag fields
2. **NULL handling**: Many optional fields are NULL, not empty strings
3. **Team consistency**: Team names are consistent but check for exact matches
4. **Coordinate system**: StatsBomb coordinates differ from other providers
5. **Event ordering**: Use `index_num` for proper event sequence

## License and Attribution

- **Data Source**: StatsBomb Open Data
- **License**: CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial)
- **Usage**: Non-commercial use only, attribution required
- **Citation**: "StatsBomb Open Data"

## Building the Database

The database is built using `build.py`, which follows an optimized build process:

1. **Creates ENUM types** for categorical columns (`shot_outcome_enum`, `pass_outcome_enum`)
2. **Creates all tables** with normalized schemas and foreign key relationships
3. **Loads core data**: competitions, teams, matches
4. **Optimized single-pass ETL**: 
   - Loads events JSON files once into a staging table
   - Extracts reference tables (event_types, positions, players, play_patterns) from staging
   - Transforms and inserts events from staging table
   - This approach reduces JSON file scans from 5+ to 1, resulting in 3-4x faster builds
5. **Loads lineup data** and 360° tracking data
6. **Creates indexes**: 21 indexes including composite indexes for common query patterns
7. Outputs `stats.duckdb` in the root directory

**Build Performance**: Typical build time is ~2.5 minutes for ~12M events and ~15M 360 positions.

See the main [README.md](README.md) for setup and build instructions.
