import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import streamlit as st

sns.set(style="whitegrid")

@st.cache_data
def load_data():
    return pd.read_excel(r"salah_shots.xlsx")

df = load_data()

st.title("Mohamed Salah Performance Analysis Dashboard")
st.markdown("An in-depth analysis of Mohamed Salah's performance based on goals, shots, and contributions.")

seasons = df['season'].dropna().unique()
selected_season = st.sidebar.selectbox("Select Season", sorted(seasons))

filtered_df = df[df['season'] == selected_season]

analysis = st.sidebar.radio("Choose an analysis:", [
    "Goals per Season",
    "Top Teams Conceding Goals",
    "Goal Distribution (Home vs Away)",
    "Top Assist Providers",
    "Shot Foot Distribution",
    "Clutch Goals (Last-Minute Goals)",
    "Shot Map",
    "xG Over Time"
])

if analysis == "Goals per Season":
    goals_df = filtered_df[filtered_df['result'] == 'Goal']
    goals_per_match = goals_df['date'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=goals_per_match.index, y=goals_per_match.values, ax=ax, palette="viridis")
    ax.set_title(f"Goals in {selected_season}", fontsize=16)
    ax.set_xlabel("Match Date", fontsize=12)
    ax.set_ylabel("Goals", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("""
    This bar chart shows the number of goals scored by Mohamed Salah in each season. 
    It helps us understand his goal-scoring consistency over time.
    """)


elif analysis == "Top Teams Conceding Goals":
    goals = filtered_df[filtered_df['result'] == 'Goal'].copy()
    goals['vs_team'] = goals.apply(lambda r: r['a_team'] if r['h_a'] == 'h' else r['h_team'], axis=1)
    top_teams = goals['vs_team'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_teams.values, y=top_teams.index, ax=ax, palette="magma")
    ax.set_title(f"Top Teams Conceding Goals ({selected_season})", fontsize=16)
    ax.set_xlabel("Goals Scored", fontsize=12)
    ax.set_ylabel("Team", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("""
    This horizontal bar chart shows the top 10 teams that have conceded the most goals from Mohamed Salah.
    It gives insight into which teams have been the most vulnerable to his attacking play.
    """)

elif analysis == "Goal Distribution (Home vs Away)":
    salah_goals = filtered_df[(filtered_df['player'] == 'Mohamed Salah') & (filtered_df['result'] == 'Goal')]
    venue_counts = salah_goals['h_a'].map({'h': 'Home', 'a': 'Away'}).value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        venue_counts,
        labels=venue_counts.index,
        autopct='%1.1f%%',
        colors=['#66b3ff', '#ff9999'],
        startangle=90,
        shadow=True,
        explode=[0.05]*len(venue_counts)
    )
    ax.set_title(f"Goal Distribution: Home vs Away ({selected_season})")
    st.pyplot(fig)
    st.markdown("""
    This pie chart illustrates the distribution of Mohamed Salah's goals between home and away matches.
    It shows how his performance varies depending on the match location.
    """)


elif analysis == "Top Assist Providers":
    assisted_shots = filtered_df[['player_assisted', 'xG']].dropna(subset=['player_assisted'])
    assist_stats = assisted_shots.groupby('player_assisted').agg(
        assists=('player_assisted', 'count'),
        avg_xG=('xG', 'mean')
    ).sort_values('assists', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(y=assist_stats.index, x=assist_stats['assists'], ax=ax, palette="Blues_d")
    ax.set_title(f"Top Assist Providers ({selected_season})", fontsize=16)
    ax.set_xlabel('Number of Assists', fontsize=12)
    ax.set_ylabel('Player Assisted', fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("""
    This chart shows the top 10 players who have provided the most assists to Mohamed Salah.
    It highlights the key players who have contributed to his goal-scoring opportunities.
    """)


elif analysis == "Shot Foot Distribution":
    salah_shots = filtered_df[filtered_df['player'] == 'Mohamed Salah'].copy()
    salah_shots['foot'] = salah_shots['shotType'].str.replace('Foot', '').str.strip()
    foot_counts = salah_shots['foot'].value_counts().loc[['Left', 'Right']]
    fig = px.pie(foot_counts, names=foot_counts.index, values=foot_counts.values, 
                 title=f"Shot Distribution by Foot ({selected_season})", color=foot_counts.index, 
                 color_discrete_map={'Left': '#ff7f0e', 'Right': '#1f77b4'})
    st.plotly_chart(fig)
    st.markdown("""
    This pie chart illustrates the distribution of Mohamed Salah's shots between his left and right foot.
    It shows how often he uses each foot when taking shots on goal.
    """)

elif analysis == "Clutch Goals (Last-Minute Goals)":
    clutch_goals = filtered_df[(filtered_df['result'] == 'Goal') & (filtered_df['minute'] > 75)]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(clutch_goals['minute'], bins=range(75, 91, 5), color='#e63946', edgecolor='black')
    ax.set_title(f"Clutch Goals After 75th Minute ({selected_season})", fontsize=16)
    ax.set_xlabel("Minute", fontsize=12)
    ax.set_ylabel("Number of Goals", fontsize=12)
    ax.set_xticks(range(75, 91, 5))
    ax.grid(axis='y', alpha=0.2)
    total_clutch = len(clutch_goals)
    ax.text(82, ax.get_ylim()[1]*0.9, f"Total Clutch Goals: {total_clutch}", bbox=dict(facecolor='white', alpha=0.8))
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("""
    This histogram displays Mohamed Salah's goals scored after the 75th minute, showcasing his ability to score clutch goals in crucial moments.
    It highlights how often he contributes to his team's success in the final stages of the game.
    """)

elif analysis == "Shot Map":
    shot_df = filtered_df[filtered_df['player'] == 'Mohamed Salah']
    fig = px.scatter(
        shot_df, x='X', y='Y', color='result', size='xG',
        title=f"Salah's Shot Map ({selected_season})",
        labels={'X': 'Pitch X', 'Y': 'Pitch Y'},
        color_discrete_map={
            'Goal': 'green',
            'MissedShots': 'red',
            'BlockedShot': 'orange',
            'SavedShot': 'blue'
        }, height=600
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig)
    st.markdown("""
   #### Mohamed Salah's Shot Map
    This interactive chart displays the location of all shots taken by Mohamed Salah on the pitch.
    Each dot represents a shot, positioned based on where it was taken on the field.
    The color indicates the outcome of the shot:
  - 🟢 Goal
  - 🔴 Missed
  - 🔵 Saved by the goalkeeper
  - 🟠 Blocked by defenders
                
  The size of the dot reflects the chance quality (xG – Expected Goals)

This visualization helps identify Salah’s most dangerous zones and his shooting tendencies across different match situations.
""")

elif analysis == "xG Over Time":
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    xg_df = filtered_df[(filtered_df['player'] == 'Mohamed Salah')].sort_values('date')
    fig = px.line(
        xg_df,
        x='date',
        y='xG',
        title=f'Expected Goals (xG) Over Time ({selected_season})',
        markers=True
    )
    st.plotly_chart(fig)
    st.markdown("""
    #### 📈 Expected Goals (xG) Over Time (Since 2020)

    This chart tracks the quality of Mohamed Salah's scoring chances over time.
    Analyzing how his xG fluctuates helps us evaluate his involvement in high-quality opportunities throughout recent seasons.
    """)
