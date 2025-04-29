import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# Add caching to data loading
@st.cache_data
def load_data():
    return pd.read_csv('concat_files/concat_shots.csv')

# Cache filtering operations
@st.cache_data
def filter_data(df, team, player):
    if team:
        df = df[df['teamName'] == team]
    if player:
        df = df[df['playerName'] == player]
    return df

# Cache pitch creation
@st.cache_resource
def create_pitch():
    return VerticalPitch(
        pitch_type='custom',
        pitch_length=105,
        pitch_width=68,
        half=True,
        line_color=clean_white,
        linewidth=1,
        pitch_color=back_color,
        goal_type='box',
        label=False
    )

# Cache team and player options preparation
@st.cache_data
def prepare_team_options(shots_df):
    team_shot_counts = shots_df['teamName'].value_counts()
    team_display = [f"{team} ({count})" for team, count in team_shot_counts.items()]
    display_to_team = {f"{team} ({count})": team for team, count in team_shot_counts.items()}
    return team_display, display_to_team

@st.cache_data
def prepare_player_options(shots_df, team):
    if team:
        players_df = shots_df[shots_df['teamName'] == team]
        player_shot_counts = players_df['playerName'].value_counts()
        player_display = [f"{player} ({count})" for player, count in player_shot_counts.items()]
        display_to_player = {f"{player} ({count})": player for player, count in player_shot_counts.items()}
    else:
        player_display = []
        display_to_player = {}
    return player_display, display_to_player

# Configuración de página
st.set_page_config(page_title="Libertadores 2025 Shot Map", layout="centered", initial_sidebar_state="expanded")

# Estilos visuales
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }
        MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        # header {visibility: visible;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title('Libertadores 2025 Shot Map')
st.header('Filter by any team/player to see all their shots taken')

# Side Bar
st.sidebar.title('🏆 LIBERViZ')
st.sidebar.info("""
Note:\n
Shots taken in the **Copa Libertadores 2025**.\n
""")
st.sidebar.caption(
    "Want to see something else related to [Libertadores](https://www.conmebollibertadores.com/)? Feel free to send me a message [axelbol](https://x.com/axel_bol)."
)

# Side Bar Menu Example
# st.sidebar.markdown("---")
# st.sidebar.markdown("# Menu")

# Colors
back_color = '#2C3E50'
clean_white = '#FFFFFF'
clean_dark = '#000000'
neon_green = '#06D6A0'
purple = '#8338EC' # #D33E43

# Load data once and cache it
df = load_data()

# Filter on target shots once
target_shots = df[df['isOnTarget'] == True]

# Create the pitch object once
pitch = create_pitch()

# Add RADIO BUTTONS for shot type selection
shot_type_radio = st.radio(
    "Select shot type:",
    ["Shots Taken", "Shots On Target"],
    horizontal=True
)

# Use current data based on selection
current_data = target_shots if shot_type_radio == "Shots On Target" else df
goal_color = purple if shot_type_radio == "Shots On Target" else neon_green

# Get team options (cached)
team_display, display_to_team = prepare_team_options(current_data)

# Streamlit team selectbox
team_display_selected = st.selectbox('Select a team', team_display, index=None, placeholder='Select a team')

# Convert display name back to actual team name
team = display_to_team.get(team_display_selected, None)

# Get player options (cached)
player_display, display_to_player = prepare_player_options(current_data, team)

# Streamlit player selectbox
player_display_selected = st.selectbox('Select a player', player_display, index=None, placeholder='Select a player')

# Convert display name back to actual player name
player = display_to_player.get(player_display_selected, None)

# Filter the data (cached)
filtered_df = filter_data(current_data, team, player)

# Create figure for plot
with st.spinner("Drawing pitch and shots..."):
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor(back_color)
    pitch.draw(ax=ax)

    # Optimize plotting by reducing redundant operations
    for x in filtered_df.to_dict(orient='records'):
        is_goal = x['eventType'] == 'Goal'
        pitch.scatter(
            x=x['x'],
            y=x['y'],
            s=800 * x['expectedGoals'],
            color=goal_color if is_goal else back_color,
            edgecolors=clean_white,
            linewidth=.8,
            alpha=1 if is_goal else .5,
            zorder=2 if is_goal else 1,
            ax=ax,
        )

    # Display the plot
    st.pyplot(fig)

# Optional: Show statistics about the filtered data
    # with st.expander("Shot Statistics"):
    #     if not filtered_df.empty:
    #         st.write(f"Total shots: {len(target_shots)}")
    #         st.write(f"Goals: {target_shots['isGoal'].sum()}")
    #         st.write(f"Expected Goals (xG): {target_shots['expectedGoals'].sum():.2f}")
    #     else:
    #         st.write("No data available for the selected filters.")
