import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import os
from urllib.parse import urlparse

def extract_match_slug(url):
    # Parse the URL and extract the match slug (team1-vs-team2)
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    if len(path_parts) >= 3 and 'matches' in path_parts:
        match_index = path_parts.index('matches') + 1
        if match_index < len(path_parts):
            return path_parts[match_index]
    return None

def scrape_shots_data(url, output_path):
    # Extract match slug for filename
    match_slug = extract_match_slug(url)
    if not match_slug:
        raise ValueError("Could not extract match slug from URL. Please check the URL format.")

    output_filename = f"{match_slug}.csv"

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
    print(f"Match slug: {match_slug}")

    return full_path

if __name__ == "__main__":
    # Interactive prompts
    print("FotMob Shots Data Scraper")
    print("-----------------------")

    # Get URL input
    url = input("Enter the URL of the FotMob match page to scrape: ")

    # Fixed output path
    output_path = '/home/axel/Code/Python/axel/streamlit/csv/'

    # Run the scraper
    try:
        saved_path = scrape_shots_data(url, output_path)
        print(f"Scraping completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
