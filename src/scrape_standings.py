import pandas as pd
import numpy as np

# --- Configuration ---
# ==============================================================================
FBref_INPUT_FILE = 'player_stats_top5_leagues_2005_to_2024.csv'
UNDERSTAT_INPUT_FILE = 'understat_standings_2005_to_2024.csv'
FINAL_OUTPUT_FILE = 'processed_ballon_dor_dataset_2005_to_2024.csv'
# ==============================================================================

def load_data(fbref_path, understat_path):
    """Loads the two raw datasets from CSV files."""
    print("[INFO] Loading raw datasets...")
    try:
        df_fbref = pd.read_csv(fbref_path)
        df_understat = pd.read_csv(understat_path)
        print(f"  -> Loaded {len(df_fbref)} player records from FBref.")
        print(f"  -> Loaded {len(df_understat)} team records from Understat.")
        return df_fbref, df_understat
    except FileNotFoundError as e:
        print(f"[ERROR] Could not find a required file: {e}. Please ensure both CSVs are in the correct directory.")
        return None, None

def clean_fbref_data(df):
    """Cleans and preprocesses the player statistics data from FBref."""
    print("[INFO] Cleaning FBref player data...")
    
    # Select essential columns (you can add more if needed)
    performance_cols = [
        'Player', 'Nation', 'Pos', 'Age', '90s', 'Gls', 'Ast', 'G+A', 'G-PK',
        'PK', 'PKatt', 'CrdY', 'CrdR', 'xG', 'npxG', 'xAG', 'npxG+xAG'
    ]
    context_cols = ['Season', 'League', 'Team']
    df = df[context_cols + performance_cols]
    
    # Convert relevant columns to numeric, coercing errors to NaN
    numeric_cols = ['Age', '90s', 'Gls', 'Ast', 'G+A', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR', 'xG', 'npxG', 'xAG', 'npxG+xAG']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Fill NaN values in numeric columns with 0, as it usually means the player had zero of that stat
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Remove players with very few minutes played (e.g., less than five full games)
    df = df[df['90s'] >= 5.0].reset_index(drop=True)
    
    print(f"  -> FBref data cleaned. Kept {len(df)} player records with substantial game time.")
    return df

def clean_understat_data(df):
    """Cleans and preprocesses the team performance data from Understat."""
    print("[INFO] Cleaning Understat team data...")
    
    # Rename columns for clarity and to avoid clashes after merging
    df = df.rename(columns={
        'wins': 'team_wins', 'draws': 'team_draws', 'loses': 'team_loses',
        'scored': 'team_goals_scored', 'missed': 'team_goals_conceded',
        'pts': 'team_points', 'xG': 'team_xG', 'xGA': 'team_xGA', 'xpts': 'team_xpts'
    })
    
    # Create a 'Season' column in the 'YYYY-YYYY' format to match FBref
    df['Season'] = df['season_start_year'].astype(str) + '-' + (df['season_start_year'] + 1).astype(str)
    
    # Standardize team names: This is a critical and often manual step.
    # We create a mapping from Understat names to FBref names.
    team_name_mapping = {
        'Manchester City': 'Manchester City',
        'Manchester United': 'Manchester Utd',
        'Tottenham': 'Tottenham',
        'West Bromwich Albion': 'West Brom',
        'Stoke': 'Stoke City',
        'Bolton': 'Bolton',
        'Blackburn': 'Blackburn',
        'Wigan Athletic': 'Wigan Athletic',
        'Huddersfield': 'Huddersfield',
        'Brighton': 'Brighton',
        'Leicester': 'Leicester City',
        'Schalke 04': 'Schalke 04',
        'Hertha BSC': 'Hertha BSC',
        'Borussia M.Gladbach': 'Monchengladbach',
        'Koeln': 'FC Koln',
        'Hoffenheim': 'Hoffenheim',
        'Nurnberg': 'Nurnberg',
        'Fortuna Duesseldorf': 'Dusseldorf',
        'Athletic Club': 'Athletic Club',
        'Atletico Madrid': 'Atletico Madrid',
        'Malaga': 'Malaga',
        'Deportivo La Coruna': 'La Coruna',
        'Sporting Gijon': 'Sporting Gijon',
        'Real Betis': 'Betis',
        'Celta Vigo': 'Celta Vigo',
        'Paris Saint Germain': 'Paris S-G',
        'Marseille': 'Marseille',
    }
    df['Team'] = df['team'].replace(team_name_mapping)
    
    # Create the team's final league rank for that season
    df['team_rank'] = df.groupby(['Season', 'league'])['team_points'].rank(method='first', ascending=False).astype(int)
    
    # Select final columns
    final_cols = ['Team', 'Season', 'team_rank', 'team_points', 'team_wins', 'team_draws', 'team_loses',
                  'team_goals_scored', 'team_goals_conceded', 'team_xG', 'team_xGA', 'team_xpts']
    df = df[final_cols]
    
    print(f"  -> Understat data cleaned and team ranks calculated.")
    return df

def merge_and_engineer_features(df_players, df_teams):
    """Merges the two dataframes and creates new, insightful features."""
    print("[INFO] Merging player and team data...")
    
    # Merge the dataframes on the common 'Team' and 'Season' columns
    df_merged = pd.merge(df_players, df_teams, on=['Team', 'Season'], how='left')
    
    # Handle cases where a team name didn't match (these will have NaN in team_rank)
    unmatched_teams = df_merged[df_merged['team_rank'].isna()]['Team'].unique()
    if len(unmatched_teams) > 0:
        print(f"  [WARN] Could not find team data for: {unmatched_teams}. These player records will have missing team stats.")
    df_merged = df_merged.dropna(subset=['team_rank']) # Drop players whose teams couldn't be matched
    
    print("[INFO] Engineering new features...")
    
    # --- Feature Engineering ---
    # 1. Per 90 Minutes Stats
    df_merged['Gls_per90'] = df_merged['Gls'] / df_merged['90s']
    df_merged['Ast_per90'] = df_merged['Ast'] / df_merged['90s']
    df_merged['G+A_per90'] = df_merged['G+A'] / df_merged['90s']
    df_merged['xG_per90'] = df_merged['xG'] / df_merged['90s']
    df_merged['xAG_per90'] = df_merged['xAG'] / df_merged['90s']
    
    # 2. Player's contribution to team goals
    # To avoid division by zero, replace 0 team goals with 1
    safe_team_goals = df_merged['team_goals_scored'].replace(0, 1)
    df_merged['goal_contribution_pct'] = (df_merged['Gls'] + df_merged['Ast']) / safe_team_goals
    
    # 3. Performance vs. Expected Models
    df_merged['xG_overperformance'] = df_merged['Gls'] - df_merged['xG']
    df_merged['xAG_overperformance'] = df_merged['Ast'] - df_merged['xAG']
    
    # 4. Positional Grouping (simplifying 'Pos' column)
    def map_position(pos):
        if pd.isna(pos): return 'Other'
        if 'FW' in pos or 'ST' in pos: return 'Forward'
        if 'MF' in pos or 'AM' in pos or 'DM' in pos: return 'Midfielder'
        if 'DF' in pos or 'CB' in pos: return 'Defender'
        if 'GK' in pos: return 'Goalkeeper'
        return 'Other'
    df_merged['Pos_Group'] = df_merged['Pos'].apply(map_position)
    
    print(f"  -> Feature engineering complete. Final dataset has {len(df_merged)} records and {len(df_merged.columns)} columns.")
    return df_merged

# --- Main Execution Block ---
if __name__ == "__main__":
    df_fbref, df_understat = load_data(FBref_INPUT_FILE, UNDERSTAT_INPUT_FILE)
    
    if df_fbref is not None and df_understat is not None:
        df_fbref_clean = clean_fbref_data(df_fbref)
        df_understat_clean = clean_understat_data(df_understat)
        
        final_dataset = merge_and_engineer_features(df_fbref_clean, df_understat_clean)
        
        # Save the final, processed dataset
        print(f"\n[INFO] Saving final processed dataset to '{FINAL_OUTPUT_FILE}'...")
        final_dataset.to_csv(FINAL_OUTPUT_FILE, index=False)
        print(f"\n✅ SUCCESS! Your model-ready dataset is saved.")