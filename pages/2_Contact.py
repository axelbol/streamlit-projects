import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Libertadores 2025 Shot Map", page_icon=":soccer:", layout="centered", initial_sidebar_state="auto") #:trophy:

# Estilos visuales
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        # header {visibility: visible;}
        header {visibility: hidden;}

        /* Custom styles for mobile responsiveness */
        @media screen and (max-width: 640px) {
            .st-emotion-cache-16txtl3 h1 {
                font-size: 1.5rem !important;
            }
            .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {
                font-size: 1.2rem !important;
            }
        }

        /* FIXED: Hide index column in tables - stronger selector */
        .stTable table tr th:first-child,
        .stTable table tr td:first-child {
            display: none !important;
        }

        /* FIXED: Center numeric columns - stronger selector with !important */
        .stTable table tr td:nth-child(4),  /* Shots column */
        .stTable table tr td:nth-child(5) { /* xG column */
            text-align: center !important;
        }
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

# Colors
back_color = '#2C3E50'
clean_white = '#FFFFFF'
clean_dark = '#000000'
neon_green = '#06D6A0'
purple = '#684756'
beaver = '#AB8476'
