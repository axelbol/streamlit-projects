import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import plotly.graph_objects as go

# Colors
BACK_COLOR = '#2C3E50'
CLEAN_WHITE = '#FFFFFF'
NEON_GREEN = '#06D6A0'
PURPLE = '#684756'
BEAVER = '#AB8476'

# Add caching to data loading
@st.cache_data
def load_data():
    return pd.read_csv('concat_files/concat_shots.csv')

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

# Main title
st.title('Libertadores 2025')
st.header('Home vs Away performance')

# Side Bar
st.sidebar.title('🏆 LIBERViZ')
st.sidebar.info("Note:\nShots taken in the **Copa Libertadores 2025**.")
st.sidebar.caption(
    "Want to see something else related to [Libertadores](https://www.conmebollibertadores.com/)? "
    "Feel free to send me a message [axelbol](https://x.com/axel_bol)."
)

# Load data once
shots = load_data()

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Shots Taken", "Shots On Target", "Home vs Away"])

with tab1:
    st.subheader("Home vs Away Performance")

    # Group by teamName and h_a
    grouped = shots.groupby(['teamName', 'h_a']).size().reset_index(name='count')

    # Pivot the data
    pivot_df = grouped.pivot(index='teamName', columns='h_a', values='count').fillna(0)

    # Ensure 'h' and 'a' columns exist
    for col in ['h', 'a']:
        if col not in pivot_df.columns:
            pivot_df[col] = 0

    # Sort by total count
    pivot_df['total'] = pivot_df.sum(axis=1)
    pivot_df = pivot_df.sort_values('total', ascending=False)
    teams = pivot_df.index.tolist()
    home_counts = pivot_df['h']
    away_counts = pivot_df['a']
    pivot_df = pivot_df.drop(columns='total')

    # Plot with Plotly
    fig = go.Figure()

    # Home bar
    fig.add_trace(go.Bar(
        x=teams,
        y=home_counts,
        name='Home (h)',
        marker_color=NEON_GREEN
    ))

    # Away bar stacked on top
    fig.add_trace(go.Bar(
        x=teams,
        y=away_counts,
        name='Away (a)',
        marker_color=PURPLE
    ))

    fig.update_layout(
        barmode='stack',
        title='Shot Count per Team (Home vs Away)',
        xaxis_title='Team Name',
        yaxis_title='Number of Shots',
        legend_title='Location',
        xaxis_tickangle=-45,
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CLEAN_WHITE)
    )

    # Display plotly chart
    st.plotly_chart(fig, use_container_width=True)

    # Display the data table
    st.dataframe(pivot_df.rename(columns={'h': 'Home Shots', 'a': 'Away Shots'}),
                 use_container_width=True)

    # Add some insights
    st.subheader("Insights")

    # Calculate team with most home shots
    max_home_team = home_counts.idxmax()
    max_home_shots = home_counts.max()

    # Calculate team with most away shots
    max_away_team = away_counts.idxmax()
    max_away_shots = away_counts.max()

    # Display insights
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Team with Most Home Shots", value=max_home_team, delta=f"{int(max_home_shots)} shots")

    with col2:
        st.metric(label="Team with Most Away Shots", value=max_away_team, delta=f"{int(max_away_shots)} shots")

with tab2:
    st.subheader("Shot Map Visualization")
    # Here you would add your mplsoccer VerticalPitch visualization
    # You can add your shot map visualization code here

    # Example placeholder for the shot map
    st.info("Shot map visualization will be displayed here. Add your mplsoccer code.")

    # Example code for shot map (you'll need to adapt this to your data)
    # pitch = VerticalPitch(pitch_type='statsbomb', pitch_color=BACK_COLOR, line_color=CLEAN_WHITE)
    # fig, ax = pitch.draw(figsize=(10, 7))
    # # Add shots visualization code here
    # st.pyplot(fig)

with tab3:
    st.subheader("Shot Map Visualization")
    # Here you would add your mplsoccer VerticalPitch visualization
    # You can add your shot map visualization code here

    # Example placeholder for the shot map
    st.info("Shot map visualization will be displayed here. Add your mplsoccer code.")

    # Example code for shot map (you'll need to adapt this to your data)
    # pitch = VerticalPitch(pitch_type='statsbomb', pitch_color=BACK_COLOR, line_color=CLEAN_WHITE)
    # fig, ax = pitch.draw(figsize=(10, 7))
    # # Add shots visualization code here
    # st.pyplot(fig)
