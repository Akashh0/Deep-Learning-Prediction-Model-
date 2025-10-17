# src/process_data.py

import pandas as pd
import os

def process_local_standings():
    """
    Reads individual league CSV files from the /data folder, combines them,
    and saves a new unified CSV.
    """
    print("Processing local data files...")
    
    files_to_process = {
        "Premier League": "premier_league_2024.csv",
        "La Liga": "laliga_2024.csv",
        "Serie A": "serieA_2024.csv",
        "Bundesliga": "Bundesliga_2024.csv",
        "Ligue 1": "ligue1_2024.csv"
    }
    
    all_standings = []
    
    for league, filename in files_to_process.items():
        try:
            file_path = os.path.join("data", filename)
            
            # Read the CSV. The copy-paste method from FBref often includes
            # the header as the first row, so we can read it directly.
            standings_df = pd.read_csv(file_path)
            
            standings_df['League'] = league
            all_standings.append(standings_df)
            print(f"Successfully processed: {filename}")

        except FileNotFoundError:
            print(f"Error: Could not find '{filename}'. Please check the file name and location.")
        except Exception as e:
            print(f"An error occurred with {filename}: {e}")

    if all_standings:
        combined_df = pd.concat(all_standings, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    final_standings = process_local_standings()
    
    if not final_standings.empty:
        output_path = os.path.join("data", "combined_standings_2024.csv")
        final_standings.to_csv(output_path, index=False)
        
        print("\nProcessing complete!")
        print(f"Combined data saved successfully to: {output_path}")
        print("\nFirst 5 rows of the combined data:")
        print(final_standings.head())
    else:
        print("\nProcessing failed. No data was saved.")