import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_js_eval import streamlit_js_eval

# Constants
COLORS = {
    'BACK_COLOR': '#2C3E50',
    'CLEAN_WHITE': '#FFFFFF',
    'NEON_GREEN': '#06D6A0',
    'VERMILION': '#F64740',
    'BRIGHT_PINK': '#FF6F61'
}

# Add caching to data loading
@st.cache_data
def load_data():
    """Load and cache the shots data."""
    return pd.read_csv('concat_files/concat_shots.csv')

def setup_page_config():
    """Configure the page settings."""
    st.set_page_config(
        page_title="Libertadores 2025 Shots",
        page_icon=":soccer:",
        layout="centered"
    )

    # Display helpful toasts
    st.toast('Just click on the column name', icon='👀')
    st.toast('You can order the table by Team Name, Home Shots or Away Shots', icon='🚩')

def apply_custom_styles():
    """Apply custom CSS styles."""
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

def get_screen_width():
    """Get the screen width using JS evaluation."""
    if "screen_width" not in st.session_state:
        st.session_state["screen_width"] = 1000  # default for desktop

    width = streamlit_js_eval(js_expressions="window.innerWidth", key="WIDTH", want_output=True)
    if width is not None:
        st.session_state["screen_width"] = width

    return st.session_state["screen_width"]

def setup_sidebar():
    """Configure the sidebar."""
    st.sidebar.title('🏆 LIBERViZ')
    st.sidebar.info("Note:\nShots taken in the **Copa Libertadores 2025**.")
    st.sidebar.caption(
        "Want to see something else related to [Libertadores](https://www.conmebollibertadores.com/)? "
        "Feel free to send me a message [axel_bol](https://x.com/axel_bol)."
    )

def get_team_stats(shots):
    """Calculate team statistics for home and away shots."""
    # Home teams stats
    home_teams = shots[shots['h_a'] == 'h']
    team_counts_h = home_teams['teamName'].value_counts()
    most_frequent_home_team = team_counts_h.idxmax()
    count_home_most_shots = team_counts_h.max()
    least_frequent_home_team = team_counts_h.idxmin()
    count_home_least_shots = team_counts_h.min()

    # Away teams stats
    away_teams = shots[shots['h_a'] == 'a']
    team_counts_a = away_teams['teamName'].value_counts()
    most_frequent_away_team = team_counts_a.idxmax()
    count_away_most_shots = team_counts_a.max()
    least_frequent_away_team = team_counts_a.idxmin()
    count_away_least_shots = team_counts_a.min()

    return {
        'home': {
            'most': {'team': most_frequent_home_team, 'count': count_home_most_shots},
            'least': {'team': least_frequent_home_team, 'count': count_home_least_shots}
        },
        'away': {
            'most': {'team': most_frequent_away_team, 'count': count_away_most_shots},
            'least': {'team': least_frequent_away_team, 'count': count_away_least_shots}
        }
    }

def display_team_metrics(team_stats):
    """Display team metrics in a 2x2 grid."""
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Team with Most Home Shots",
            value=team_stats['home']['most']['team'],
            delta=f"{int(team_stats['home']['most']['count'])} shots",
            border=True
        )

    with col2:
        st.metric(
            label="Team with Least Home Shots",
            value=team_stats['home']['least']['team'],
            delta=f"{int(team_stats['home']['least']['count'])} shots",
            delta_color="inverse",
            border=True
        )


    col3, col4 = st.columns(2)
    with col3:
        st.metric(
            label="Team with Most Away Shots",
            value=team_stats['away']['most']['team'],
            delta=f"{int(team_stats['away']['most']['count'])} shots",
            border=True
        )

    with col4:
        st.metric(
            label="Team with Least Away Shots",
            value=team_stats['away']['least']['team'],
            delta=f"{int(team_stats['away']['least']['count'])} shots",
            delta_color="inverse",
            border=True
        )

def prepare_pivot_data(shots, is_mobile=False):
    """Prepare the pivot table data for visualization."""
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

    # Limit to top 10 teams on mobile
    if is_mobile:
        pivot_df = pivot_df.head(10)

    return pivot_df

def create_stacked_bar_chart(pivot_df):
    """Create a stacked bar chart for home and away shots."""
    teams = pivot_df.index.tolist()
    home_counts = pivot_df['h']
    away_counts = pivot_df['a']

    # Plot with Plotly
    fig = go.Figure()

    # Home bar
    fig.add_trace(go.Bar(
        x=teams,
        y=home_counts,
        name='Home',
        marker_color=COLORS['NEON_GREEN'],
        hovertemplate='<span style="color: CLEAN_WHITE; background-color: rgba(211, 211, 211, 0.8); padding: 2px 5px; border-radius: 3px;">%{x}</span><br>' +
                     '<span style="color: ' + COLORS['CLEAN_WHITE'] + '; background-color: black; padding: 2px 5px; border-radius: 3px;">Home: %{y}</span><extra></extra>'
    ))

    # Away bar stacked on top
    fig.add_trace(go.Bar(
        x=teams,
        y=away_counts,
        name='Away',
        marker_color=COLORS['BRIGHT_PINK'],
        hovertemplate='<span style="color: CLEAN_WHITE; background-color: rgba(211, 211, 211, 0.8); padding: 2px 5px; border-radius: 3px;">%{x}</span><br>' +
                     '<span style="color: ' + COLORS['CLEAN_WHITE'] + '; background-color: black; padding: 2px 5px; border-radius: 3px;">Away: %{y}</span><extra></extra>'
    ))

    fig.update_layout(
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.1,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=14, color=COLORS['CLEAN_WHITE'])
        ),
        xaxis_tickangle=-45,
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['CLEAN_WHITE']),
        yaxis=dict(
            title_font=dict(size=18, color=COLORS['CLEAN_WHITE']),
            tickfont=dict(size=14, color=COLORS['CLEAN_WHITE']),
            showgrid=False,
            dtick=20,  # Set tick marks every 20 units
            range=[0, 100],  # Fixed range from 0 to 100
            fixedrange=True  # Prevent zooming/panning that would change this range
        ),
        margin=dict(t=70, b=100)  # Adjust margins to accommodate the legend
    )

    return fig

def prepare_display_dataframe(pivot_df):
    """Prepare the dataframe for display."""
    # Create a copy to avoid modifying the original
    display_df = pivot_df.copy()

    # Drop the total column used for sorting
    if 'total' in display_df.columns:
        display_df = display_df.drop(columns='total')

    # Reset index to make teamName a column and rename columns
    display_df = display_df.reset_index().rename(columns={
        'teamName': 'Team Name',
        'h': 'Home Shots',
        'a': 'Away Shots'
    })

    # Reorder columns
    display_df = display_df[['Team Name', 'Home Shots', 'Away Shots']]

    return display_df

def create_shots_tab(shots, screen_width):
    """Create content for the Shots Taken tab."""
    # Check if mobile
    is_mobile = screen_width <= 640

    # Get team statistics
    team_stats = get_team_stats(shots)

    # Display team metrics
    display_team_metrics(team_stats)

    # Sub header title
    st.subheader("Shot Count per Team (Home vs Away)")

    # Prepare data
    pivot_df = prepare_pivot_data(shots, is_mobile)

    # Create and display chart
    fig = create_stacked_bar_chart(pivot_df)

    if is_mobile:
        st.info("📱 Top 10 teams with most shots taken Home & Away shown on mobile")

    # Display plotly chart
    st.plotly_chart(fig, use_container_width=True)

    # Prepare and display dataframe
    display_df = prepare_display_dataframe(pivot_df)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def create_shots_on_target_tab(shots, screen_width):
    """Create content for the Shots On Target tab."""
    # Filter for shots on target only
    shots_on_target = shots[shots['isOnTarget'] == True]

    # Check if mobile
    is_mobile = screen_width <= 640

    # Get team statistics for shots on target
    team_stats = get_team_stats(shots_on_target)

    # Display team metrics
    display_team_metrics(team_stats)

    # Sub header title
    st.subheader("Shots On Target per Team (Home vs Away)")

    # Prepare data
    pivot_df = prepare_pivot_data(shots_on_target, is_mobile)

    # Create and display chart
    fig = create_stacked_bar_chart(pivot_df)

    if is_mobile:
        st.info("📱 Top 10 teams with most shots on target Home & Away shown on mobile")

    # Display plotly chart
    st.plotly_chart(fig, use_container_width=True)

    # Prepare and display dataframe
    display_df = prepare_display_dataframe(pivot_df)
    # Update column names to reflect shots on target
    display_df = display_df.rename(columns={
        'Home Shots': 'Home Shots On Target',
        'Away Shots': 'Away Shots On Target'
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def create_home_vs_away_tab():
    """Create content for the Home vs Away tab."""
    st.subheader("Shot Map Visualization")
    st.info("Shot map visualization will be displayed here. Add your mplsoccer code.")

def main():
    """Main function to run the app."""
    # Setup
    setup_page_config()
    apply_custom_styles()
    screen_width = get_screen_width()

    # Main title
    st.title('Copa Libertadores 2025')
    st.header('Home vs Away performance')

    # Setup sidebar
    setup_sidebar()

    # Load data
    shots = load_data()

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Shots Taken", "Shots On Target", "Home vs Away"])

    # Fill tabs with content
    with tab1:
        create_shots_tab(shots, screen_width)

    with tab2:
        create_shots_on_target_tab(shots, screen_width)

    with tab3:
        create_home_vs_away_tab()

if __name__ == "__main__":
    main()
