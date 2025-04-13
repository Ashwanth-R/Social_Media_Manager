import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def visualize_sentiment_distribution(results_df):
    sentiment_counts = results_df['Sentiment'].value_counts()
    emoji_map = {'Positive': '😊', 'Negative': '😞', 'Neutral': '😐'}
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sentiment_counts,
        labels=[f"{k} {emoji_map.get(k, '')}" for k in sentiment_counts.index],
        colors=['#F44336', '#FFC107','#4CAF50'],
        autopct='%1.1f%%',
        pctdistance=0.85,
        startangle=90
    )
    
    # Draw circle to make it a donut
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.set_title('Sentiment Distribution', fontsize=16, pad=20)
    st.pyplot(fig)