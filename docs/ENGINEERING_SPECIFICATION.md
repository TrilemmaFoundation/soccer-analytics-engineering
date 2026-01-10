# Engineering Specification

This document provides technical details on data sources, assumptions, modeling choices, and data quality considerations for the Soccer Analytics Engineering repository.

## Data Sources

### StatsBomb Open Data

**Source**: [StatsBomb Open Data](https://github.com/statsbomb/open-data)

**License**: CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial)

**Description**: Comprehensive event-level football/soccer data including:
- Match metadata (teams, scores, dates, venues)
- Detailed event data (passes, shots, carries, tackles, etc.)
- Player positions and formations
- Expected goals (xG) values
- 360° tracking data (where available)

**Data Format**: JSON files organized by competition, season, and match

**Coverage**: Multiple competitions including:
- Premier League
- La Liga
- Serie A
- Bundesliga
- Ligue 1
- Champions League
- World Cups
- Women's competitions

**Data Quality Notes**:
- Event data is manually tagged by StatsBomb analysts
- Coordinate system: 120 yards × 80 yards pitch (origin at bottom-left)
- xG values range from 0.0 to 1.0
- Some matches may have incomplete 360° tracking data
- Player names may have minor inconsistencies (handled in `schema.py`)

**Usage**: Data is cloned from the StatsBomb repository and processed by `build.py` to create `stats.duckdb`

### Capology Financial Data

**Source**: Capology (club-level financial data)

**Description**: Financial metrics for European football clubs including:
- Revenue data
- Assets
- Personnel costs
- Other financial indicators

**Data Format**: CSV files processed and cleaned in `Economic_Metrics/` notebooks

**Coverage**: Top European leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)

**Data Quality Notes**:
- Data may have missing values for some clubs/seasons
- Financial reporting standards vary by league/country
- Currency conversions may be required for cross-league analysis

**Usage**: Processed in `Economic_Metrics/FPEI.ipynb` and stored as cleaned CSV files

### FBref Performance Data

**Source**: FBref (Football Reference)

**Description**: Performance indicators for clubs including:
- Points
- Goal difference
- League position
- Other performance metrics

**Data Format**: CSV files processed and cleaned in `Economic_Metrics/` notebooks

**Coverage**: Top European leagues

**Data Quality Notes**:
- Data is scraped/exported from FBref
- May require cleaning and standardization
- Season formats may vary (e.g., "2015/2016" vs "2015-16")

**Usage**: Processed in `Economic_Metrics/FPEI.ipynb` and merged with financial data

## Modeling Methodology

### Expected Threat (xT)

**Purpose**: Quantify the threat value of different pitch locations based on the probability of scoring from that location and the value of moving the ball forward.

**Methodology** (as implemented in `threat_surface.ipynb`):

1. **Pitch Discretization**: Divide the pitch into a 16×12 grid (192 zones)

2. **Orientation Normalization**: 
   - Infer attacking direction per team from average shot locations
   - Flip coordinates so all teams attack left-to-right (toward x=120)

3. **Shoot/Move Probabilities**:
   - For each zone, compute probability of shooting vs. moving
   - Based on historical event data (Pass, Shot, Dribble, Carry events)

4. **Expected Goals per Zone**:
   - Compute mean xG conditional on shooting from each zone
   - Uses StatsBomb's `shot_statsbomb_xg` values

5. **Transition Matrix**:
   - Build zone-to-zone transition probabilities from movement events
   - Apply smoothing (alpha=0.5) and forward-only constraints
   - Normalize to probability distributions

6. **Iterative Value Calculation**:
   - Initialize: V₀ = 0 for all zones
   - Iterate: Vₙ₊₁ = s × g + m × T × Vₙ
     - `s` = shoot probability vector
     - `g` = expected goals vector
     - `m` = move probability vector
     - `T` = transition matrix
   - Converge to stable xT values (typically 5 iterations)

7. **xT Attribution**:
   - For each movement action (pass, carry, dribble), compute:
     - xT gain = xT(end_zone) - xT(start_zone)
   - Aggregate by team/player for analysis

**Assumptions**:
- Forward movements are more valuable than backward movements
- Transition probabilities are stable across teams/leagues
- Shot probability and xG are sufficient proxies for zone threat

**Limitations**:
- Grid discretization may lose spatial nuance
- Assumes homogeneous transition probabilities
- Doesn't account for defensive pressure or game state

### Financial Performance Efficiency Index (FPEI)

**Purpose**: Measure how efficiently clubs convert financial resources into on-field performance.

**Methodology** (as implemented in `Economic_Metrics/FPEI_Model_RollingWindow.ipynb`):

1. **Data Integration**:
   - Merge financial data (Capology) with performance data (FBref)
   - Align by club, league, and season
   - Handle missing values and outliers

2. **Expected Revenue Estimation**:
   - Use rolling expanding-window forecasting
   - Model revenue as a function of historical performance and financial metrics
   - Account for league-specific effects

3. **Efficiency Calculation**:
   - FPEI = (Actual Performance) / (Expected Performance given Revenue)
   - Higher FPEI indicates better efficiency (more performance per unit revenue)
   - Can be computed at club-level or league-level

4. **Rolling Window Framework**:
   - Expand training window over time
   - Re-estimate model parameters for each season
   - Generate out-of-sample predictions

**Assumptions**:
- Revenue is a reasonable proxy for financial resources
- Performance metrics (points, goal difference) capture on-field success
- Historical relationships are predictive of future performance

**Limitations**:
- Financial data quality varies by league
- Doesn't account for non-financial factors (coaching, youth development)
- Revenue may lag performance (chicken-and-egg problem)

## Data Quality Considerations

### StatsBomb Data

**Strengths**:
- High-quality manual tagging
- Consistent coordinate system
- Comprehensive event coverage
- Regular updates

**Challenges**:
- Large dataset size (requires efficient processing)
- JSON parsing overhead
- Some competitions have incomplete coverage
- Player name inconsistencies

**Mitigation Strategies**:
- Use `ijson` for streaming JSON parsing
- Buffer events for batch insertion
- **Player name canonicalization**: Player names are normalized during the build process to handle inconsistencies. A mapping of 10 known problematic player IDs to their canonical names is applied in `build.py` (see [DATABASE_SPECIFICATION.md](DATABASE_SPECIFICATION.md) for the full list). This ensures consistent player names across the `players` table and the denormalized `player` field in the `events` table. The canonicalization handles special characters (e.g., apostrophes in "N'Golo Kanté"), name variations, and encoding issues.
- Extract coordinates to numeric columns for performance

### Economic Data

**Strengths**:
- Comprehensive coverage of top leagues
- Multiple seasons available
- Standardized financial metrics

**Challenges**:
- Missing values for some clubs/seasons
- Currency and reporting standard differences
- Data collection timing variations
- Potential outliers

**Mitigation Strategies**:
- Robust data cleaning pipelines
- Outlier detection and handling
- Imputation strategies for missing values
- Validation against multiple sources

## Technical Architecture

### Database Schema

The DuckDB database (`stats.duckdb`) uses a normalized schema with:
- Lookup tables for entities (teams, players, positions, event types)
- Fact table (`events`) with denormalized fields for query performance
- Foreign key relationships for data integrity
- Extracted coordinate columns for spatial queries

See [DATABASE_SPECIFICATION.md](DATABASE_SPECIFICATION.md) for detailed schema documentation.

### Build Process

1. Clone StatsBomb open data repository
2. Process competitions.json for metadata
3. Process match files (nested by competition/season)
4. Process event files (one per match)
5. Create normalized tables with foreign keys
6. Buffer and batch insert events for performance

**Performance Optimizations**:
- DuckDB's built-in columnar storage and query optimization
- Batch inserts with configurable chunk size
- Deduplication of lookup table entries

### Notebook Workflows

**xT Analysis** (`threat_surface.ipynb`):
1. Load events from database
2. Filter by competition/season/team
3. Normalize coordinates (flip for attacking direction)
4. Compute xT surface
5. Export surfaces and team/player metrics

**FPEI Analysis** (`Economic_Metrics/FPEI*.ipynb`):
1. Load and clean financial data
2. Load and clean performance data
3. Merge datasets
4. Estimate expected revenues
5. Compute FPEI scores
6. Generate visualizations and reports

### Testing Infrastructure

The project includes a comprehensive test suite to validate database schema, data integrity, and data quality. The test suite consists of 5 test modules with approximately 100 test cases covering:

- **Schema validation**: Table structure, column types, indexes
- **Data integrity**: Primary keys, foreign keys, referential integrity
- **Data quality**: Coordinate ranges, xG values, boolean flags, timing fields
- **Data validation**: Aggregate statistics, domain-specific soccer validation
- **Business logic**: Player canonicalization, JSON field transformations

Tests are written using `pytest` and require the `stats.duckdb` database to be built before execution. The test suite uses fixtures defined in `tests/conftest.py` to manage database connections.

See [TESTING.md](TESTING.md) for detailed documentation on running tests and adding new test cases.

## Version History

- **v1.0**: Initial repository structure
- **v1.1**: Added Economic Metrics workstream
- **v1.2**: Unified documentation and cleanup

## References

- [StatsBomb Open Data Documentation](https://github.com/statsbomb/open-data)
- [Expected Threat Methodology](https://karun.in/blog/expected-threat.html) (Karun Singh)
- Capology financial data (proprietary source)
- FBref performance data

## License

This project is licensed under the MIT License. Note that StatsBomb data is licensed under CC BY-NC 4.0 (non-commercial use only).

