import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Libertadores 2025 Shot Map", layout="centered", initial_sidebar_state="expanded")

# Estilos visuales
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: visible;}
    </style>
""", unsafe_allow_html=True)

st.title('Libertadores 2024 Shot Map')
st.header('Page in progress...')

# Side Bar
st.sidebar.title('LIBERViZ 🏆')
st.sidebar.info("""
Note on metrics:\n
Words with more frequent letters have a higher '**letter score**' (suggested for 1st or 2nd guesses).\n
""")
st.sidebar.caption("A [WORDLE](https://www.nytimes.com/games/wordle/index.html) ch🟨🟩t sh🟨🟨t made by [Siavash Yasini](https://www.linkedin.com/in/siavash-yasini/).")

# Side Bar Menu Example
# st.sidebar.markdown("---")
# st.sidebar.markdown("# Menu")
