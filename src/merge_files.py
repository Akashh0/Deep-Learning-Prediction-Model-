import pandas as pd

try:
    # --- Step 1: Load the datasets from your local files ---
    ucl_player_stats = pd.read_csv('all_ucl_player_stats_2011-2025_CLEAN.csv')
    ucl_team_performance = pd.read_csv('all_ucl_team_performance_and_progress.csv')
    league_standings = pd.read_csv('combined_league_standings_2011-2025.csv')
    player_stats = pd.read_csv('combined_player_stats_2011-2025_CLEAN.csv')

    print("All files loaded successfully.")

    # --- Step 2: Prepare the dataframes for merging ---

    # Add a 'Competition' column to distinguish between UCL and domestic league stats
    ucl_player_stats['Competition'] = 'Champions League'
    player_stats['Competition'] = 'Domestic League'
    ucl_team_performance['Competition'] = 'Champions League'
    league_standings['Competition'] = 'Domestic League'

    # Combine the player and team dataframes respectively
    combined_player_stats = pd.concat([ucl_player_stats, player_stats], ignore_index=True)
    combined_team_performance = pd.concat([ucl_team_performance, league_standings], ignore_index=True)

    print("Dataframes have been combined.")

    # --- Step 3: Merge the combined data ---
    # Merge the player stats with team performance on 'Squad', 'Season', and 'Competition'
    merged_data = pd.merge(combined_player_stats, combined_team_performance, on=['Squad', 'Season', 'Competition'], how='left')

    print("Merging complete.")

    # --- Step 4: Rename columns for clarity ---
    merged_data.rename(columns={
        'Rk_x': 'Player_Rank',
        'Player': 'Player_Name',
        'Nation': 'Player_Nationality',
        'Pos': 'Position',
        'Squad': 'Team',
        'Age': 'Player_Age',
        'Born': 'Year_of_Birth',
        'MP_x': 'Matches_Played_by_Player',
        'Starts': 'Games_Started',
        'Min': 'Minutes_Played',
        '90s': 'Matches_in_90s',
        'Gls': 'Goals',
        'Ast': 'Assists',
        'G+A': 'Goals_and_Assists',
        'G-PK': 'Non_Penalty_Goals',
        'PK': 'Penalty_Kicks_Made',
        'PKatt': 'Penalty_Kicks_Attempted',
        'CrdY': 'Yellow_Cards',
        'CrdR': 'Red_Cards',
        'xG': 'Expected_Goals',
        'npxG': 'Non_Penalty_xG',
        'xAG': 'Expected_Assisted_Goals',
        'npxG+xAG': 'npxG_plus_xAG',
        'PrgC': 'Progressive_Carries',
        'PrgP': 'Progressive_Passes',
        'PrgR': 'Progressive_Passes_Received',
        'Rk_y': 'Team_Rank',
        'MP_y': 'Matches_Played_by_Team',
        'W': 'Wins',
        'D': 'Draws',
        'L': 'Losses',
        'GF': 'Goals_For',
        'GA': 'Goals_Against',
        'GD': 'Goal_Difference',
        'Pts': 'Points',
        'Attendance': 'Average_Attendance',
        'Top Team Scorer': 'Top_Scorer',
        'Goalkeeper': 'Main_Goalkeeper'
    }, inplace=True)

    print("Columns renamed.")

    # --- Step 5: Save the final merged dataset ---
    output_filename = 'final_merged_dataset.csv'
    merged_data.to_csv(output_filename, index=False)

    print(f"\nSuccessfully created the merged file: '{output_filename}'")

except FileNotFoundError as e:
    print(f"Error: {e}. Please make sure all four CSV files are in the same folder as this script.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")