import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import os

def scrape_shots_data(url, output_filename, output_path):
    # Make request and parse HTML
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')

    # Extract JSON data from the script tag
    json_fotmob = json.loads(soup.find('script', attrs={'id': '__NEXT_DATA__'}).contents[0])

    # Create player stats dataframe
    df = pd.DataFrame(json_fotmob['props']['pageProps']['content']['playerStats'])
    df = df.T
    df['player_id'] = df.index
    df.reset_index(drop=True, inplace=True)

    # Create mapping dataframe with team names and player IDs
    new_df = df[['teamName', 'player_id']].copy()
    new_df['player_id'] = new_df['player_id'].astype(int)

    # Extract shots data
    df_shots = pd.DataFrame(json_fotmob['props']['pageProps']['content']['shotmap']['shots'])

    # Map team names to shots data
    df_shots['teamName'] = df_shots['playerId'].map(new_df.set_index('player_id')['teamName'])

    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Save to CSV
    full_path = os.path.join(output_path, output_filename)
    df_shots.to_csv(full_path, index=False)
    print(f"Data successfully saved to {full_path}")

if __name__ == "__main__":
    # Interactive prompts
    print("FotMob Shots Data Scraper")
    print("-----------------------")

    # Get URL input
    url = input("Enter the URL of the FotMob match page to scrape: ")

    # Get CSV filename input
    output_filename = input("Enter the CSV filename (without path): ")

    # Add .csv extension if not provided
    if not output_filename.endswith('.csv'):
        output_filename += '.csv'

    # Fixed output path
    output_path = '/home/axel/Code/Python/axel/streamlit/csv/'

    # Run the scraper
    try:
        scrape_shots_data(url, output_filename, output_path)
    except Exception as e:
        print(f"An error occurred: {e}")
