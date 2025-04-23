import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Libertadores 2025 Shot Map", layout="centered", initial_sidebar_state="expanded")

# Add this at the beginning of your script
st.markdown(
    """
    <style>
    .stApp {
        background-color: #3A3A3C;  /* 30323d */
    }
    .stSelectbox label, h1, h2, h3 {
        color: white !important;
    }
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Libertadores 2025 Shot Map')
st.header('Filter by any team/player to see all their shots taken')

# Colors
back_color = '#2C3E50'
clean_white = '#FFFFFF'
clean_dark = '#000000'
neon_green = '#06D6A0'

df = pd.read_csv('concat_files/concat_shots.csv')

# Shots Team A(8)
team_shot_counts = df['teamName'].value_counts()
team_display = [f"{team} ({count})" for team, count in team_shot_counts.items()]

# Create a mapping from display name back to team name
display_to_team = {f"{team} ({count})": team for team, count in team_shot_counts.items()}

# Streamlit team selectbox
team_display_selected = st.selectbox('Select a team', team_display, index=None, placeholder='Select a team')

# Convert display name back to actual team name
team = display_to_team.get(team_display_selected, None)

# First version | YT
# player = st.selectbox('Select a player', df[df['teamName'] == team]['playerName'].sort_values().unique(), index=None)

# Filter players by selected team | Just the name
# player_options = df[df['teamName'] == team]['playerName'].sort_values().unique() if team else []
# player = st.selectbox('Select a player', player_options, index=None, placeholder='Select a player')

# Filter players by selected team | Colidio (10)
if team:
    players_df = df[df['teamName'] == team]
    player_shot_counts = players_df['playerName'].value_counts()
    player_display = [f"{player} ({count})" for player, count in player_shot_counts.items()]
    display_to_player = {f"{player} ({count})": player for player, count in player_shot_counts.items()}
else:
    player_display = []
    display_to_player = {}

# Streamlit player selectbox
player_display_selected = st.selectbox('Select a player', player_display, index=None, placeholder='Select a player')

# Convert display name back to actual player name
player = display_to_player.get(player_display_selected, None)

def filter_data(df, team, player):
    if team:
        df = df[df['teamName'] == team]
    if player:
        df = df[df['playerName'] == player]

    return df

filtered_df = filter_data(df, team, player)

pitch = VerticalPitch(
    pitch_type='custom',
    pitch_length=105,
    pitch_width=68,
    half=True,
    line_color=clean_white,
    linewidth=1,
    # pitch_color=back_color,
    pitch_color=back_color, # F9F9F9
    goal_type='box', # line, circle, box
    label=False
)

# fig, ax = pitch.draw(figsize=(10,10))
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor(back_color)
pitch.draw(ax=ax)

def plot_shots(df, ax, pitch):
    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x=x['x'],
            y=x['y'],
            s=800 * x['expectedGoals'],
            color = neon_green if x['eventType'] == 'Goal' else back_color,
            edgecolors=clean_white,
            linewidth=.8,
            alpha=1 if x['eventType'] == 'Goal' else .5, # Full opacity (1) for Goals, semi-transparent (0.5) for other shots
            zorder=2 if x['eventType'] == 'Goal' else 1, # Goals are drawn on top (2) of non-goals (1)
            ax=ax,
        )

plot_shots(filtered_df, ax, pitch)

st.pyplot(fig)
