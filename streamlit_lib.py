import streamlit as st
import pandas as pd
import json
from mplsoccer import VerticalPitch

st.title('Libertadores 2025 Shot Map')
st.header('Filter by any team/player to see all their shots taken')

# Colors
back_color = '#2C3E50'
clean_white = '#FFFFFF'
neon_green = '#06D6A0'

df = pd.read_csv('concat_files/concat_shots.csv')
# df = df[df['situation'] == 'RegularPlay'].reset_index(drop=True)
# df['location'] = df['location'].apply(json.loads)

team = st.selectbox('Select a team', df['teamName'].value_counts().sort_values(ascending=False), index=None)
player = st.selectbox('Select a player', df[df['teamName'] == team]['playerName'].sort_values().unique(), index=None)

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
    pitch_color=back_color
)
fig, ax = pitch.draw(figsize=(10,10))

def plot_shots(df, ax, pitch):
    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x=x['x'],
            y=x['y'],
            ax=ax,
            s=1000 * x['expectedGoals'],
            color = neon_green if x['eventType'] == 'Goal' else back_color,
            edgecolors=clean_white,
            linewidth=.8,
            alpha=1 if x['eventType'] == 'Goal' else .5,
            zorder=2 if x['eventType'] == 'Goal' else 1
        )

plot_shots(filtered_df, ax, pitch)

st.pyplot(fig)
