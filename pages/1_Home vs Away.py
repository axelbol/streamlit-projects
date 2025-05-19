import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import plotly.graph_objects as go
from streamlit_js_eval import streamlit_js_eval

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
shots = load_data()

# Main title
st.title('Copa Libertadores 2025')
st.header('Home vs Away performance')

# Side Bar
st.sidebar.title('🏆 LIBERViZ')
st.sidebar.info("Note:\nShots taken in the **Copa Libertadores 2025**.")
st.sidebar.caption(
    "Want to see something else related to [Libertadores](https://www.conmebollibertadores.com/)? "
    "Feel free to send me a message [axel_bol](https://x.com/axel_bol)."
)

# Get screen width with streamlit_js_eval - more efficient approach
if "screen_width" not in st.session_state:
    st.session_state["screen_width"] = 1000  # default for desktop

# This call doesn't create visual elements and won't create a gap
width = streamlit_js_eval(js_expressions="window.innerWidth", key="WIDTH", want_output=True)
if width is not None:
    st.session_state["screen_width"] = width

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Shots Taken", "Shots On Target", "Home vs Away"])

with tab1:
    # General info
    # Display the team with the most home & away shots
    col1, col2 = st.columns(2)
    # Filter rows where h_a is 'h'
    home_teams = shots[shots['h_a'] == 'h']
    # Group by teamName and count occurrences
    team_counts_h = home_teams['teamName'].value_counts()
    # Get the team with the highest count
    most_frequent_home_team = team_counts_h.idxmax()
    count_home_most_shots = team_counts_h.max()
    with col1:
        st.metric(label="Team with Most Home Shots", value=most_frequent_home_team, delta=f"{int(count_home_most_shots)} shots", border=True)
    # Filter rows where h_a is 'a'
    away_teams = shots[shots['h_a'] == 'a']
    # Group by teamName and count occurrences
    team_counts_a = away_teams['teamName'].value_counts()
    # Get the team with the highest count
    most_frequent_away_team = team_counts_a.idxmax()
    count_away_most_shots = team_counts_a.max()
    with col2:
        st.metric(label="Team with Most Away Shots", value=most_frequent_away_team, delta=f"{int(count_away_most_shots)} shots", border=True)

    # Display the team with the most home & away shots
    col3, col4 = st.columns(2)
    # Get the h team with the lowest count
    least_frequent_home_team = team_counts_h.idxmin()
    count_home_least_shots = team_counts_h.min()
    with col3:
        st.metric(label="Team with Least Home Shots", value=least_frequent_home_team, delta=f"{(int(count_home_least_shots))} shots", delta_color="inverse", border=True)
    # Get the h team with the lowest count
    least_frequent_away_team = team_counts_a.idxmin()
    count_away_least_shots = team_counts_a.min()# Filter rows where h_a is 'a'
    with col4:
        st.metric(label="Team with Least Away Shots", value=least_frequent_away_team, delta=f"{(int(count_away_least_shots))} shots", delta_color="inverse", border=True)

    # Sub header title
    st.subheader("Shot Count per Team (Home vs Away)")

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

    # Determine if mobile
    is_mobile = st.session_state.get("screen_width", 1000) <= 640

    # Limit to top 10 teams on mobile
    if is_mobile:
        pivot_df = pivot_df.head(10)

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
        name='Home',
        marker_color=NEON_GREEN,
        hovertemplate='<span style="color: CLEAN_WHITE; background-color: rgba(211, 211, 211, 0.8); padding: 2px 5px; border-radius: 3px;">%{x}</span><br>' + '<span style="color: ' + CLEAN_WHITE + '; background-color: black; padding: 2px 5px; border-radius: 3px;">Home: %{y}</span><extra></extra>'
    ))

    # Away bar stacked on top
    fig.add_trace(go.Bar(
        x=teams,
        y=away_counts,
        name='Away',
        marker_color=BRIGHT_PINK,
        hovertemplate='<span style="color: CLEAN_WHITE; background-color: rgba(211, 211, 211, 0.8); padding: 2px 5px; border-radius: 3px;">%{x}</span><br>' + '<span style="color: ' + CLEAN_WHITE + '; background-color: black; padding: 2px 5px; border-radius: 3px;">Away: %{y}</span><extra></extra>'
    ))

    fig.update_layout(
        barmode='stack',
        # title='Shot Count per Team (Home vs Away)',
        # xaxis_title='Team Name',
        # yaxis_title='Number of Shots',
        legend=dict(
            # title='Location',
            orientation="h",
            yanchor="top",
            y=1.1,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=14, color=CLEAN_WHITE)
        ),
        xaxis_tickangle=-45,
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CLEAN_WHITE),
        yaxis=dict(
            title_font=dict(size=18, color=CLEAN_WHITE),
            tickfont=dict(size=14, color=CLEAN_WHITE),
            showgrid=False,
            range=[0, pivot_df.sum(axis=1).max() * 1.1],  # Set y-axis range from 0 to 10% above max value
            fixedrange=True  # Prevent zooming/panning that would change this range
        ),
        margin=dict(t=70, b=100)  # Adjust margins to accommodate the legend
    )

    if is_mobile:
        st.info("📱 Top 10 teams with most shots taken Home & Away shown on mobile")

    # Display plotly chart
    st.plotly_chart(fig, use_container_width=True)

    # Display the data table
    st.dataframe(pivot_df.rename(columns={'h': 'Home Shots', 'a': 'Away Shots'}),
                 use_container_width=True)

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
