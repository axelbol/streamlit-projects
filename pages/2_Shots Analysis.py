import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import base64
import os
from PIL import Image
from streamlit_js_eval import streamlit_js_eval

# Constants
LOGOS_FOLDER = 'logos'
DATA_PATH = 'concat_files/concat_shots.csv'
DEFAULT_SCREEN_WIDTH = 1000
MOBILE_BREAKPOINT = 640

# Sizing configurations
MOBILE_CONFIG = {
    'width': 400,
    'height': 500,
    'logo_size': (20, 20),
    'sizex': 0.3,
    'sizey': 0.006,
    'title_size': 16,
    'axis_title_size': 12,
    'tick_size': 10,
    'annotation_size': 8  # Smaller for mobile but still visible
}

DESKTOP_CONFIG = {
    'width': 1000,
    'height': 700,
    'logo_size': (30, 30),
    'sizex': 0.4,
    'sizey': 0.008,
    'title_size': 20,
    'axis_title_size': 16,
    'tick_size': 12,
    'annotation_size': 14
}

@st.cache_data
def load_data():
    """Load and cache the shots data."""
    return pd.read_csv(DATA_PATH)

def setup_page_config():
    """Configure the page settings."""
    st.set_page_config(
        page_title="Libertadores 2025 Shots",
        page_icon=":soccer:",
        layout="wide"
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

            @media screen and (max-width: 640px) {
                .st-emotion-cache-16txtl3 h1 {font-size: 1.5rem !important;}
                .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {font-size: 1.2rem !important;}
            }
        </style>
    """, unsafe_allow_html=True)

def get_screen_width():
    """Get the screen width using JS evaluation."""
    if "screen_width" not in st.session_state:
        st.session_state["screen_width"] = DEFAULT_SCREEN_WIDTH

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

@st.cache_data
def encode_image(image_path):
    """Convert image to base64 string for Plotly"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        st.warning(f"Error encoding image {image_path}: {e}")
        return None

def resize_logo(image_path, size=(40, 40)):
    """Resize logo to consistent size"""
    try:
        with Image.open(image_path) as img:
            img = img.resize(size, Image.Resampling.LANCZOS)
            temp_path = image_path.replace('.png', '_resized.png')
            img.save(temp_path)
            return temp_path
    except Exception as e:
        st.warning(f"Error resizing image {image_path}: {e}")
        return image_path

@st.cache_data
def prepare_team_data(shots_df):
    """Prepare team-level statistics from shots dataframe"""
    team_stats = shots_df.groupby('teamName').agg({
        'expectedGoals': 'sum',
        'id': 'count',
        'matchRound': 'nunique',
        'isOnTarget': 'sum'
    }).reset_index()

    team_stats.columns = ['team', 'total_xg_conceded', 'total_shots_conceded', 'games_played', 'shots_on_target']

    # Calculate derived metrics
    team_stats['shots_conceded_per_game'] = team_stats['total_shots_conceded'] / team_stats['games_played']
    team_stats['xg_conceded_per_shot'] = team_stats['total_xg_conceded'] / team_stats['total_shots_conceded']
    team_stats['xg_conceded_per_game'] = team_stats['total_xg_conceded'] / team_stats['games_played']

    return team_stats

def get_config(is_mobile):
    """Get configuration based on device type"""
    return MOBILE_CONFIG if is_mobile else DESKTOP_CONFIG

def create_hover_trace(team_stats):
    """Create invisible hover trace for the plot"""
    return go.Scatter(
        x=team_stats['shots_conceded_per_game'],
        y=team_stats['xg_conceded_per_shot'],
        mode='markers',
        marker=dict(size=20, opacity=0),
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
    )

def create_logo_images(team_stats, logos_path, config):
    """Create logo images for the plot"""
    images = []
    for _, row in team_stats.iterrows():
        team_name = row['team']
        logo_path = os.path.join(logos_path, f"{team_name}.png")

        if os.path.exists(logo_path):
            resized_path = resize_logo(logo_path, size=config['logo_size'])
            encoded_image = encode_image(resized_path)

            if encoded_image:
                images.append(dict(
                    source=encoded_image,
                    xref="x", yref="y",
                    x=row['shots_conceded_per_game'],
                    y=row['xg_conceded_per_shot'],
                    sizex=config['sizex'],
                    sizey=config['sizey'],
                    xanchor="center", yanchor="middle",
                    layer="above"
                ))

            # Cleanup temporary file
            if resized_path != logo_path and os.path.exists(resized_path):
                try:
                    os.remove(resized_path)
                except:
                    pass
        else:
            st.warning(f"Logo not found for team: {team_name}")

    return images

def add_quadrant_annotations(fig, team_stats, config):
    """Add quadrant annotations to the plot - ALWAYS include them"""
    x_range = team_stats['shots_conceded_per_game'].max() - team_stats['shots_conceded_per_game'].min()
    y_range = team_stats['xg_conceded_per_shot'].max() - team_stats['xg_conceded_per_shot'].min()

    annotations = [
        dict(x=team_stats['shots_conceded_per_game'].min() + x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].max() - y_range*0.1,
             text="Low Shots Conceded,<br>High xG per Shot",
             showarrow=False,
             font=dict(color="black", size=config['annotation_size'], family='Arial Black')),

        dict(x=team_stats['shots_conceded_per_game'].max() - x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].max() - y_range*0.1,
             text="High Shots Conceded,<br>High xG per Shot",
             showarrow=False,
             font=dict(color="red", size=config['annotation_size'], family='Arial Black')),

        dict(x=team_stats['shots_conceded_per_game'].min() + x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].min() + y_range*0.1,
             text="Low Shots Conceded,<br>Low xG per Shot",
             showarrow=False,
             font=dict(color="green", size=config['annotation_size'], family='Arial Black')),

        dict(x=team_stats['shots_conceded_per_game'].max() - x_range*0.1,
             y=team_stats['xg_conceded_per_shot'].min() + y_range*0.1,
             text="High Shots Conceded,<br>Low xG per Shot",
             showarrow=False,
             font=dict(color="black", size=config['annotation_size'], family='Arial Black'))
    ]

    fig.update_layout(annotations=annotations)

def create_plotly_viz_with_logos(team_stats, logos_path, is_mobile=False, for_download=False):
    """Create interactive Plotly scatter plot with team logos"""
    config = get_config(is_mobile)

    # Use larger size for download images even on mobile
    if for_download:
        config = DESKTOP_CONFIG.copy()
        config['width'] = 1200
        config['height'] = 800

    fig = go.Figure()

    # Add hover trace
    fig.add_trace(create_hover_trace(team_stats))

    # Add team logos
    images = create_logo_images(team_stats, logos_path, config)

    # Add quadrant lines
    median_shots = team_stats['shots_conceded_per_game'].median()
    median_xg = team_stats['xg_conceded_per_shot'].median()
    fig.add_hline(y=median_xg, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=median_shots, line_dash="dash", line_color="gray", opacity=0.5)

    # Update layout with BOLD titles
    fig.update_layout(
        images=images,
        title={
            'text': '<b>Volume of Shots vs Quality of Chances Conceded</b>',
            'x': 0.5, 'xanchor': 'center',
            'font': {'size': config['title_size'], 'family': 'Arial Black', 'color': '#000000'}
        },
        xaxis_title={
            'text': '<b>Shots conceded per Game</b>',
            'font': {'size': config['axis_title_size'], 'family': 'Arial Black', 'color': '#000000'}
        },
        yaxis_title={
            'text': '<b>xG conceded per Shot</b>',
            'font': {'size': config['axis_title_size'], 'family': 'Arial Black', 'color': '#000000'}
        },
        xaxis=dict(
            tickfont=dict(color='#000000', family='Arial Black', size=config['tick_size']),
            gridcolor='lightgray', gridwidth=1, showgrid=True, fixedrange=True
        ),
        yaxis=dict(
            tickfont=dict(color='#000000', family='Arial Black', size=config['tick_size']),
            gridcolor='rgba(200, 200, 200, 0.5)', gridwidth=1, showgrid=True, fixedrange=True
        ),
        plot_bgcolor='#eaf4f4', paper_bgcolor='#eaf4f4',
        font=dict(family="Arial", size=10 if is_mobile else 12),
        width=config['width'], height=config['height'],
        margin=dict(t=60 if is_mobile else 80, b=40 if is_mobile else 60,
                   l=60 if is_mobile else 80, r=80 if is_mobile else 100)
    )

    # ALWAYS add quadrant annotations
    add_quadrant_annotations(fig, team_stats, config)

    # Add X account reference
    fig.add_annotation(
        x=1, y=0, xref="paper", yref="paper",
        text="@axel_bol", showarrow=False,
        font=dict(size=10 if is_mobile else 12, color='gray'),
        align="right", xanchor="right", yanchor="bottom"
    )

    return fig

def create_simple_scatter_plot(team_data, is_mobile=False, for_download=False):
    """Create simple scatter plot without logos"""
    config = get_config(is_mobile)

    # Use larger size for download images even on mobile
    if for_download:
        config = DESKTOP_CONFIG.copy()
        config['width'] = 1200
        config['height'] = 800

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
        title='<b>Volume of Shots vs Quality of Chances Conceded</b>',
        xaxis_title='<b>Shots Conceded per Game</b>',
        yaxis_title='<b>xG Conceded per Shot</b>',
        height=config['height'], width=config['width'],
        xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True)
    )

    # Add quadrant annotations for simple plot too
    add_quadrant_annotations(fig, team_data, config)

    return fig

def convert_plotly_to_image(fig):
    """Convert Plotly figure to image bytes for download"""
    try:
        return fig.to_image(format="png", engine="kaleido", width=1200, height=800)
    except Exception as e:
        st.error(f"Error converting plot to image: {e}")
        return None

def create_download_section(fig, team_data, is_mobile):
    """Create download section for mobile users"""
    st.info("📱 On mobile? Use the download button below to save the visualization")

    try:
        # Create a high-quality version specifically for download
        if os.path.exists(LOGOS_FOLDER):
            download_fig = create_plotly_viz_with_logos(team_data, LOGOS_FOLDER, is_mobile=False, for_download=True)
        else:
            download_fig = create_simple_scatter_plot(team_data, is_mobile=False, for_download=True)

        img_bytes = convert_plotly_to_image(download_fig)
        if not img_bytes:
            return

        # Generate filename
        base_filename = "team_shots_libertadores25_axel_bol"
        count_key = f"download_count_{base_filename}"

        if count_key not in st.session_state:
            st.session_state[count_key] = 1
        else:
            st.session_state[count_key] += 1

        count = st.session_state[count_key]
        filename = f"{base_filename}_{count}.png" if count > 1 else f"{base_filename}.png"

        # Create download button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.download_button(
                label="📥 Download Visualization",
                data=img_bytes,
                file_name=filename,
                mime="image/png",
                type="primary",
                use_container_width=True,
                key=f"download_btn_{count}"
            ):
                st.success("🎉 Download started! Check your downloads folder.")
                st.balloons()

        # st.caption(f"File: {filename} • Size: {len(img_bytes) // 1024} KB")

    except Exception as e:
        st.error(f"Error preparing download: {e}")
        st.info("Try refreshing the page if the download doesn't work")

def display_team_statistics(team_stats):
    """Display team statistics in a formatted table"""
    st.subheader("📊 Team Statistics")

    display_df = team_stats.copy().round({
        'shots_conceded_per_game': 1,
        'xg_conceded_per_shot': 3,
        'xg_conceded_per_game': 2,
        'total_xg_conceded': 2
    })

    display_df.columns = [
        'Team', 'Total xG Conceded', 'Total Shots Conceded',
        'Games Played', 'Shots on Target', 'Shots/Game',
        'xG/Shot', 'xG/Game'
    ]

    st.dataframe(display_df, use_container_width=True)

def display_visualization_tab(team_data, is_mobile):
    """Display the visualization tab content"""
    st.subheader("Shot Conceded Analysis")
    st.write("""
    This visualization shows the relationship between the volume of shots conceded per game
    and the quality of chances conceded (xG per shot). Teams in different quadrants represent
    different defensive profiles.
    """)

    plot_config = {
        'scrollZoom': False,
        'doubleClick': False,
        'displayModeBar': False
    }

    if os.path.exists(LOGOS_FOLDER):
        fig = create_plotly_viz_with_logos(team_data, LOGOS_FOLDER, is_mobile)

        if is_mobile:
            create_download_section(fig, team_data, is_mobile)
            st.subheader("Preview")
            small_fig = create_plotly_viz_with_logos(team_data, LOGOS_FOLDER, is_mobile=True)
            small_fig.update_layout(height=300, width=350)
            st.plotly_chart(small_fig, use_container_width=True)
        else:
            st.plotly_chart(fig, use_container_width=True, config=plot_config)
    else:
        st.warning(f"⚠️ Logos folder not found at '{LOGOS_FOLDER}'. Displaying chart without logos.")
        fig = create_simple_scatter_plot(team_data, is_mobile)

        if is_mobile:
            create_download_section(fig, team_data, is_mobile)
        else:
            st.plotly_chart(fig, use_container_width=True, config=plot_config)

def main():
    """Main function to run the app."""
    setup_page_config()
    apply_custom_styles()

    screen_width = get_screen_width()
    is_mobile = screen_width <= MOBILE_BREAKPOINT

    st.title('Copa Libertadores 2025')
    st.header('Shot Analysis Dashboard')
    setup_sidebar()

    try:
        shots = load_data()
        st.success(f"✅ Data loaded successfully! {len(shots)} shots analyzed.")

        team_data = prepare_team_data(shots)

        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Teams", len(team_data))
        with col2:
            st.metric("Total Shots", len(shots))
        with col3:
            st.metric("Total xG", f"{shots['expectedGoals'].sum():.2f}")

        st.markdown("---")

        # Create tabs
        tab1, tab2 = st.tabs(["📈 Interactive Visualization", "📋 Team Statistics"])

        with tab1:
            display_visualization_tab(team_data, is_mobile)

        with tab2:
            display_team_statistics(team_data)

    except FileNotFoundError:
        st.error(f"❌ Data file not found. Please make sure '{DATA_PATH}' exists.")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
