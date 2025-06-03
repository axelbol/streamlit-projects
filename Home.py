import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import time

# Colors
BACK_COLOR = '#2C3E50'
CLEAN_WHITE = '#FFFFFF'
NEON_GREEN = '#06D6A0'
VERMILION = '#F64740'
BRIGHT_PINK = '#FF6F61'

# Add caching to data loading
@st.cache_data
def load_data():
    return pd.read_csv('concat_files/concat_shots.csv')

# Cache pitch creation
@st.cache_resource
def create_pitch():
    return VerticalPitch(
        pitch_type='custom',
        pitch_length=105,
        pitch_width=68,
        half=True,
        line_color=CLEAN_WHITE,
        linewidth=1,
        pitch_color=BACK_COLOR,
        goal_type='box',
        label=False
    )

@st.cache_data
def prepare_options(df, column):
    """Generic function to prepare display options with counts for any column"""
    counts = df[column].value_counts()
    displays = [f"{value} ({count})" for value, count in counts.items()]
    display_to_value = {f"{value} ({count})": value for value, count in counts.items()}
    return displays, display_to_value

@st.cache_data
def prepare_player_options(df, team=None):
    """Prepare player options, filtered by team if provided"""
    filtered_df = df[df['teamName'] == team] if team else df
    return prepare_options(filtered_df, 'playerName')

@st.cache_data
def prepare_top_players_table(df, shot_type="all", team=None, limit=10):
    """Unified function for preparing top players table"""
    filtered_df = df[df['teamName'] == team] if team else df

    if shot_type == "target":
        filtered_df = filtered_df[filtered_df['isOnTarget'] == True]

    result = filtered_df.groupby(['playerName', 'teamName']).agg(
        Shots=('playerName', 'size'),
        xG=('expectedGoals', 'mean')
    ).reset_index()

    result = result.sort_values('Shots', ascending=False).head(limit)
    result['xG'] = result['xG'].apply(lambda x: f'{x:.2f}')
    result.columns = ['Name', 'Team', 'Shots', 'xG']

    return result

def plot_shots_progressive(filtered_df, goal_color, pitch, ax, stage="full"):
    """Plot shots progressively based on stage"""
    if stage == "pitch_only":
        # Just return the empty pitch
        return

    elif stage == "goals_only":
        # Plot only goals
        goals_df = filtered_df[filtered_df['eventType'] == 'Goal']
        for _, shot in goals_df.iterrows():
            pitch.scatter(
                x=shot['x'],
                y=shot['y'],
                s=800 * shot['expectedGoals'],
                color=goal_color,
                edgecolors=CLEAN_WHITE,
                linewidth=0.8,
                alpha=1,
                zorder=2,
                ax=ax,
            )

    elif stage == "full":
        # Plot all shots
        for _, shot in filtered_df.iterrows():
            is_goal = shot['eventType'] == 'Goal'
            pitch.scatter(
                x=shot['x'],
                y=shot['y'],
                s=800 * shot['expectedGoals'],
                color=goal_color if is_goal else BACK_COLOR,
                edgecolors=CLEAN_WHITE,
                linewidth=0.8,
                alpha=1 if is_goal else 0.5,
                zorder=2 if is_goal else 1,
                ax=ax,
            )

# Page configuration
st.set_page_config(
    page_title="Libertadores 2025 Shots",
    page_icon=":soccer:",
    layout="centered"
)

# Styles
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        MainMenu, footer, header {visibility: hidden;}

        /* Mobile responsiveness */
        @media screen and (max-width: 640px) {
            .st-emotion-cache-16txtl3 h1 {font-size: 1.5rem !important;}
            .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {font-size: 1.2rem !important;}
        }

        /* Hide index column in tables */
        .stTable table tr th:first-child, .stTable table tr td:first-child {display: none !important;}

        /* Center numeric columns */
        .stTable table tr td:nth-child(4), .stTable table tr td:nth-child(5) {text-align: center !important;}
    </style>
""", unsafe_allow_html=True)

# Load data once
df = load_data()

# Main title
st.title('Libertadores 2025 Shot Map')

# General info
teams = df['teamId'].nunique()
players = df['playerId'].nunique()
keepers = df['keeperId'].nunique()
shots = len(df)
isOnTarget = len(df[df['isOnTarget'] == True])
goals = len(df[df['eventType'] == 'Goal'])
ownGoal = len(df[df['isOwnGoal'] == True])

a, b = st.columns(2)
c, d = st.columns(2)

a.metric(label="Teams", value=teams, delta=f"{-(8)} Copa Sudamericana", delta_color="normal", border=True)
b.metric(label="Players", value=players, delta=f"{int(keepers)} keepers", delta_color="normal", border=True)

c.metric(label="Shots", value=shots, delta=f"{int(isOnTarget)} shots on target", delta_color="normal", border=True)
d.metric(label="Goals", value=goals, delta=f"{-(ownGoal)} own goals", delta_color="normal", border=True)

st.header('Filter by any team/player to see all their shots taken')

# Side Bar
st.sidebar.title('🏆 LIBERViZ')
st.sidebar.info("Note:\nShots taken in the **Copa Libertadores 2025**.")
st.sidebar.caption(
    "Want to see something else related to [Libertadores](https://www.conmebollibertadores.com/)? "
    "Feel free to send me a message [axel_bol](https://x.com/axel_bol)."
)

# Add radio buttons for shot type selection
shot_type_radio = st.radio(
    "Select shot type:",
    ["Shots Taken", "Shots On Target"],
    horizontal=True
)

# Pre-filter data based on selection
current_data = df[df['isOnTarget'] == True] if shot_type_radio == "Shots On Target" else df
goal_color = BRIGHT_PINK if shot_type_radio == "Shots On Target" else NEON_GREEN

# Get team options
team_display, display_to_team = prepare_options(current_data, 'teamName')

# Team selection
team_display_selected = st.selectbox('Select a team', team_display, index=None, placeholder='Select a team')
team = display_to_team.get(team_display_selected, None)

# Get player options based on team selection
player_display, display_to_player = prepare_player_options(current_data, team)

# Player selection - disabled if no team is selected
if team:
    player_display_selected = st.selectbox('Select a player', player_display, index=None, placeholder='Select a player')
    player = display_to_player.get(player_display_selected, None)
else:
    # Display disabled dropdown when no team is selected
    st.selectbox('Select a player', [], disabled=True, placeholder='Select a team first')
    player = None

# Filter data based on selections
filtered_df = current_data
if team:
    filtered_df = filtered_df[filtered_df['teamName'] == team]
if player:
    filtered_df = filtered_df[filtered_df['playerName'] == player]

# Create plot with progressive loading
# Create pitch and prepare figure
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor(BACK_COLOR)
pitch = create_pitch()

# Create placeholder for the plot
plot_placeholder = st.empty()

# Stage 1: Show empty pitch immediately
pitch.draw(ax=ax)
plot_shots_progressive(filtered_df, goal_color, pitch, ax, stage="pitch_only")
with plot_placeholder.container():
    st.info("🏟️ Loading pitch...")
    st.pyplot(fig)

# Small delay to show the pitch loading
time.sleep(0.5)

# Stage 2: Add goals
if len(filtered_df[filtered_df['eventType'] == 'Goal']) > 0:
    # Clear and redraw
    ax.clear()
    pitch.draw(ax=ax)
    plot_shots_progressive(filtered_df, goal_color, pitch, ax, stage="goals_only")

    with plot_placeholder.container():
        st.info("⚽ Loading goals...")
        st.pyplot(fig)

    # Small delay
    time.sleep(0.5)

# Stage 3: Add all shots
ax.clear()
pitch.draw(ax=ax)
plot_shots_progressive(filtered_df, goal_color, pitch, ax, stage="full")

with plot_placeholder.container():
    if len(filtered_df) > 0:
        goals_count = len(filtered_df[filtered_df['eventType'] == 'Goal'])
        total_shots = len(filtered_df)
        st.success(f"✅ Loaded {total_shots} shots ({goals_count} goals)")
    else:
        st.info("🔍 No shots found with current filters")
    st.pyplot(fig)

# Add separator
st.markdown("---")

# Show top players across all competition when a team is selected
if team:
    # Determine shot type and limit
    shot_type_param = "target" if shot_type_radio == "Shots On Target" else "all"
    limit = 5

    # Get top players
    top_overall = prepare_top_players_table(df, shot_type=shot_type_param, limit=limit)

    st.subheader(f"Top {limit} Players Across All Competition by {shot_type_radio}")

    # Display badges horizontally
    cols = st.columns(limit)

    for idx in range(min(limit, len(top_overall))):
        with cols[idx]:
            player_name = top_overall.iloc[idx]['Name']
            team_name = top_overall.iloc[idx]['Team']
            count = top_overall.iloc[idx]['Shots']
            xg = top_overall.iloc[idx]['xG']

            st.markdown(f"""
            <div style="text-align: center;">
                <div style="background-color: {VERMILION};
                           color: white;
                           border-radius: 12px;
                           padding: 10px;
                           margin: 5px 0;
                           height: 200px;
                           width: 100%;
                           display: flex;
                           flex-direction: column;
                           justify-content: space-between;">
                    <div style="font-size: 20px; font-weight: bold;">#{idx+1}</div>
                    <div style="font-size: 16px;">{player_name}</div>
                    <div style="font-size: 12px;">({team_name})</div>
                    <div style="font-size: 18px; font-weight: bold; margin-top: 5px;">{count}</div>
                    <div style="font-size: 14px;">xG: {xg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Display stats table based on selection
st.subheader(f"Top 10 Players by {shot_type_radio}")

# Get top players table based on shot type
shot_type_param = "target" if shot_type_radio == "Shots On Target" else "all"
top_players_table = prepare_top_players_table(df, shot_type=shot_type_param, team=team)

# Display table without index
st.table(top_players_table.reset_index(drop=True))
