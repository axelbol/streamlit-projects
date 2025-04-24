import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import os
import re
import unicodedata
from urllib.parse import urlparse
from fuzzywuzzy import fuzz

def normalize_team_name(name):
    """Normalize team name by removing accents and standardizing format"""
    # Convert to lowercase
    name = name.lower()

    # Remove accents
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')

    # Remove non-alphanumeric characters and standardize spaces
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name

def create_team_mapping(h_team, a_team, known_aliases=None):
    """Create a mapping dictionary for home and away teams with their possible variations"""
    if known_aliases is None:
        known_aliases = {}

    # Normalize the official team names
    norm_h = normalize_team_name(h_team)
    norm_a = normalize_team_name(a_team)

    # Create a mapping with the full names and their normalized versions
    mapping = {
        normalize_team_name(h_team): 'h',
        normalize_team_name(a_team): 'a'
    }

    # Add known aliases from the dictionary
    for team_name, aliases in known_aliases.items():
        if normalize_team_name(team_name) == norm_h:
            for alias in aliases:
                mapping[normalize_team_name(alias)] = 'h'
        elif normalize_team_name(team_name) == norm_a:
            for alias in aliases:
                mapping[normalize_team_name(alias)] = 'a'

    return mapping

def match_team_exact(team_name, mapping):
    """Match team_name to either h_team or a_team based on exact match after normalization"""
    norm_team = normalize_team_name(team_name)

    # Try exact match
    if norm_team in mapping:
        return mapping[norm_team]

    # If no match, return None (to be handled separately)
    return None

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

    # Variables to add to DF
    matchRound = int(json_fotmob['props']['pageProps']['general']['matchRound'])
    h_team = json_fotmob['props']['pageProps']['general']['homeTeam']['name']
    a_team = json_fotmob['props']['pageProps']['general']['awayTeam']['name']

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

    # Add match round to shots DF
    df_shots['matchRound'] = matchRound

    # Map team names to shots data
    df_shots['teamName'] = df_shots['playerId'].map(new_df.set_index('player_id')['teamName'])

    # Set up any known team aliases (add more as needed)
    team_aliases = {
        # "Terminal": ["Script"],
        "Botafogo RJ": ["Botafogo", "Botafogo de Futebol e Regatas"],
        "Club Atletico Penarol": ["Penarol", "Peñarol", "CA Penarol"],
        "Atletico Nacional": ["Atlético Nacional", "Atletico Nacional Medellin"],
        "Nacional": ["Club Nacional", "Nacional de Montevideo"],
        "Talleres": ["Talleres de Córdoba"],
        "Estudiantes": ["Estudiantes de La Plata"],
        "Central Cordoba de Santiago": ["Central Córdoba (Santiago del Estero)"],
        "LDU de Quito": ["LDU Quito"],
        "Bucaramanga": ["Atlético Bucaramanga"],
        "Colo Colo": ["Colo-Colo"],
        "Fortaleza": ["Fortaleza EC"],
        "Barcelona SC": ["Barcelona de Guayaquil"],
        # Add more teams and their aliases as needed
    }

    # Create the mapping dictionary
    team_mapping = create_team_mapping(h_team, a_team, team_aliases)

    # Apply the exact matching function
    df_shots['h_a'] = df_shots['teamName'].apply(
        lambda x: match_team_exact(x, team_mapping) if pd.notna(x) else 'unknown'
    )

    # Handle any 'unknown' matches (could prompt for manual resolution)
    if 'unknown' in df_shots['h_a'].values:
        print(f"Unmatched team names: {df_shots.loc[df_shots['h_a'] == 'unknown', 'teamName'].unique()}")
        # Could add code here to handle unknowns

    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Save to CSV
    full_path = os.path.join(output_path, output_filename)
    df_shots.to_csv(full_path, index=False)
    print(f"Data successfully saved to {full_path}")
    print(f"Match slug: {match_slug}")
    print(f"Home team: {h_team}, Away team: {a_team}")

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
