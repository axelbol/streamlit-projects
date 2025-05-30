import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import base64
import os
from PIL import Image

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
        layout="wide"  # Changed to wide for better visualization display
    )

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
        </style>
    """, unsafe_allow_html=True)

def setup_sidebar():
    """Configure the sidebar."""
    st.sidebar.title('🏆 LIBERViZ')
    st.sidebar.info("Note:\nShots taken in the **Copa Libertadores 2025**.")
    st.sidebar.caption(
        "Want to see something else related to [Libertadores](https://www.conmebollibertadores.com/)? "
        "Feel free to send me a message [axel_bol](https://x.com/axel_bol)."
    )

@st.cache_data
def encode_image(image_path):
    """
    Convert image to base64 string for Plotly
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        st.warning(f"Error encoding image {image_path}: {e}")
        return None

def resize_logo(image_path, size=(40, 40)):
    """
    Resize logo to consistent size
    """
    try:
        with Image.open(image_path) as img:
            img = img.resize(size, Image.Resampling.LANCZOS)
            # Save temporarily or return as base64
            temp_path = image_path.replace('.png', '_resized.png')
            img.save(temp_path)
            return temp_path
    except Exception as e:
        st.warning(f"Error resizing image {image_path}: {e}")
        return image_path

@st.cache_data
def prepare_team_data(shots_df):
    """
    Prepare team-level statistics from shots dataframe
    """
    # Calculate team statistics including shots on target
    team_stats = shots_df.groupby('teamName').agg({
        'expectedGoals': 'sum',  # Total xG conceded
        'id': 'count',  # Total shots conceded
        'matchRound': 'nunique',  # Number of games (assuming each round is a game)
        'isOnTarget': 'sum'  # Total shots on target (assuming this column exists)
    }).reset_index()

    # Rename columns for clarity
    team_stats.columns = ['team', 'total_xg_conceded', 'total_shots_conceded', 'games_played', 'shots_on_target']

    # Calculate metrics
    team_stats['shots_conceded_per_game'] = team_stats['total_shots_conceded'] / team_stats['games_played']
    team_stats['xg_conceded_per_shot'] = team_stats['total_xg_conceded'] / team_stats['total_shots_conceded']
    team_stats['xg_conceded_per_game'] = team_stats['total_xg_conceded'] / team_stats['games_played']

    return team_stats

def create_plotly_viz_with_logos(team_stats, logos_path):
    """
    Create interactive Plotly scatter plot with team logos
    """
    # Create the scatter plot
    fig = go.Figure()

    # Add invisible scatter points first (for hover functionality)
    fig.add_trace(go.Scatter(
        x=team_stats['shots_conceded_per_game'],
        y=team_stats['xg_conceded_per_shot'],
        mode='markers',
        marker=dict(
            size=20,
            opacity=0,  # Make invisible
        ),
        text=team_stats['team'],
        hovertemplate='<b>%{text}</b><br>' +
                     'Shots per Game: %{x:.1f}<br>' +
                     'xG per Shot: %{y:.3f}<br>' +
                     'Total Shots: %{customdata[0]}<br>' +
                     'Games Played: %{customdata[1]}<br>' +
                     'Shots on Target: %{customdata[2]}<br>' +
                     'xG per Game: %{customdata[3]:.2f}<br>' +
                     'Total xG: %{customdata[4]:.2f}<br>' +
                     '<extra></extra>',
        customdata=np.column_stack((
            team_stats['total_shots_conceded'],
            team_stats['games_played'],
            team_stats['shots_on_target'],
            team_stats['xg_conceded_per_game'],
            team_stats['total_xg_conceded']
        )),
        showlegend=False
    ))

    # Add team logos as layout images
    images = []
    for i, row in team_stats.iterrows():
        team_name = row['team']
        logo_filename = f"{team_name}.png"
        logo_path = os.path.join(logos_path, logo_filename)

        if os.path.exists(logo_path):
            # Resize logo for consistency
            resized_path = resize_logo(logo_path, size=(30, 30))
            encoded_image = encode_image(resized_path)

            if encoded_image:
                images.append(dict(
                    source=encoded_image,
                    xref="x",
                    yref="y",
                    x=row['shots_conceded_per_game'],
                    y=row['xg_conceded_per_shot'],
                    sizex=0.4,  # Adjust size as needed
                    sizey=0.008,  # Adjust size as needed
                    xanchor="center",
                    yanchor="middle",
                    layer="above"
                ))

            # Clean up resized image if it was created
            if resized_path != logo_path and os.path.exists(resized_path):
                try:
                    os.remove(resized_path)
                except:
                    pass
        else:
            st.warning(f"Logo not found for team: {team_name} at path: {logo_path}")

    # Add quadrant lines
    median_shots = team_stats['shots_conceded_per_game'].median()
    median_xg = team_stats['xg_conceded_per_shot'].median()

    fig.add_hline(y=median_xg, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=median_shots, line_dash="dash", line_color="gray", opacity=0.5)

    # Update layout with images
    fig.update_layout(
        images=images,
        title={
            'text': 'Volume of Shots vs Quality of Chances Conceded',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#000000'}
        },
        xaxis_title={
            'text': 'Shots conceded per Game',
            'font': {'size': 16, 'family': 'Arial Black', 'color': '#000000'}
        },
        yaxis_title={
            'text': 'xG conceded per Shot',
            'font': {'size': 16, 'family': 'Arial Black', 'color': '#000000'}
        },
        xaxis=dict(
            tickfont=dict(
                color='#000000',  # Change to your desired color for x-axis numbers
                family='Arial Black',
                size=12
            ),
            gridcolor='lightgray',  # Add this line for grid color
            gridwidth=1,
            showgrid=True
        ),
        yaxis=dict(
            tickfont=dict(
                color='#000000',  # Change to your desired color for y-axis numbers
                family='Arial Black',
                size=12,
            ),
            gridcolor='rgba(200, 200, 200, 0.5)',  # Add this line for grid color
            gridwidth=1,
            showgrid=True
        ),
        plot_bgcolor='#eaf4f4',
        paper_bgcolor='#eaf4f4',
        font=dict(family="Arial", size=12),
        width=1000,
        height=700,
        margin=dict(t=80, b=60, l=80, r=100)
    )

    # Add quadrant annotations
    x_range = team_stats['shots_conceded_per_game'].max() - team_stats['shots_conceded_per_game'].min()
    y_range = team_stats['xg_conceded_per_shot'].max() - team_stats['xg_conceded_per_shot'].min()

    # Add annotations for quadrants
    annotations = [
        dict(x=team_stats['shots_conceded_per_game'].min() + x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].max() - y_range*0.1,
             text="Low Shots Conceded,<br>High xG per Shot",
             showarrow=False, font=dict(color="black", size=14)),

        dict(x=team_stats['shots_conceded_per_game'].max() - x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].max() - y_range*0.1,
             text="High Shots Conceded,<br>High xG per Shot",
             showarrow=False, font=dict(color="red", size=14)),

        dict(x=team_stats['shots_conceded_per_game'].min() + x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].min() + y_range*0.1,
             text="Low Shots Conceded,<br>Low xG per Shot",
             showarrow=False, font=dict(color="green", size=14)),

        dict(x=team_stats['shots_conceded_per_game'].max() - x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].min() + y_range*0.1,
             text="High Shots Conceded,<br>Low xG per Shot",
             showarrow=False, font=dict(color="black", size=14))
    ]

    fig.update_layout(annotations=annotations)

    # Add X account reference at bottom right
    fig.add_annotation(
        x=1, y=0,
        xref="paper", yref="paper",
        text="@axel_bol",
        showarrow=False,
        font=dict(size=12, color='gray'),
        align="right",
        xanchor="right",
        yanchor="bottom"
    )

    return fig

def display_team_statistics(team_stats):
    """Display team statistics in a formatted table"""
    st.subheader("📊 Team Statistics")

    # Format the dataframe for display
    display_df = team_stats.copy()
    display_df = display_df.round({
        'shots_conceded_per_game': 1,
        'xg_conceded_per_shot': 3,
        'xg_conceded_per_game': 2,
        'total_xg_conceded': 2
    })

    # Rename columns for better display
    display_df.columns = [
        'Team', 'Total xG Conceded', 'Total Shots Conceded',
        'Games Played', 'Shots on Target', 'Shots/Game',
        'xG/Shot', 'xG/Game'
    ]

    st.dataframe(display_df, use_container_width=True)

def main():
    """Main function to run the app."""
    # Setup
    setup_page_config()
    apply_custom_styles()

    # Main title
    st.title('Copa Libertadores 2025')
    st.header('Shot Analysis Dashboard')

    # Setup sidebar
    setup_sidebar()

    # Load data
    try:
        shots = load_data()
        st.success(f"✅ Data loaded successfully! {len(shots)} shots analyzed.")

        # Prepare team statistics
        team_data = prepare_team_data(shots)

        # Display basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Teams", len(team_data))
        with col2:
            st.metric("Total Shots", len(shots))
        with col3:
            st.metric("Total xG", f"{shots['expectedGoals'].sum():.2f}")

        st.markdown("---")

        # Create tabs for different views
        tab1, tab2 = st.tabs(["📈 Interactive Visualization", "📋 Team Statistics"])

        with tab1:
            st.subheader("Shot Conceded Analysis")
            st.write("""
            This visualization shows the relationship between the volume of shots conceded per game
            and the quality of chances conceded (xG per shot). Teams in different quadrants represent
            different defensive profiles.
            """)

            # Path to logos folder - you may need to adjust this path
            logos_folder = 'logos'  # Adjust this path as needed

            if os.path.exists(logos_folder):
                # Create and display the plotly visualization
                fig = create_plotly_viz_with_logos(team_data, logos_folder)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠️ Logos folder not found at '{logos_folder}'. Displaying chart without logos.")
                # Create a simple version without logos
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=team_data['shots_conceded_per_game'],
                    y=team_data['xg_conceded_per_shot'],
                    mode='markers+text',
                    text=team_data['team'],
                    textposition="middle center",
                    marker=dict(size=12, color='blue'),
                    hovertemplate='<b>%{text}</b><br>' +
                             'Shots per Game: %{x:.1f}<br>' +
                             'xG per Shot: %{y:.3f}<br>' +
                             '<extra></extra>'
                ))
                fig.update_layout(
                    title='Volume of Shots vs Quality of Chances Conceded',
                    xaxis_title='Shots Conceded per Game',
                    yaxis_title='xG Conceded per Shot',
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            display_team_statistics(team_data)

    except FileNotFoundError:
        st.error("❌ Data file not found. Please make sure 'concat_files/concat_shots.csv' exists.")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
