import pickle
import streamlit as st
import numpy as np
from transformers import pipeline

sentiment_analysis = pipeline("sentiment-analysis")

@st.cache_data
def load_data():
    df = pickle.load(open('model/games_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
    return df, similarity

df, similarity = load_data()

def recommend(game, df, similarity):
    index = df[df['name'] == game].index[0]
    distances = similarity[index]
    recommended_indices = np.argsort(-distances)[1:11]  
    recommended_game_names = df.iloc[recommended_indices]['name'].tolist()
    recommended_game_urls = ["https://rawg.io/games/{}".format(df.iloc[i]['id']) for i in recommended_indices]
    recommended_game_posters = df.iloc[recommended_indices]['poster'].tolist()
    return recommended_game_names, recommended_game_urls, recommended_game_posters

st.title('Welcome to the Game Recommender System')
st.subheader('Discover new games based on your favorite ones!')

selected_game = st.selectbox(
    "Select a game:",
    df['name'].values,
    help="Choose a game to get personalized game recommendations."
)

if st.button('Get Recommendations', help="Click to see recommended games based on your selected game"):
    recommended_game_names, recommended_game_urls, recommended_game_posters = recommend(selected_game, df, similarity)
    game_details = df[df['name'] == selected_game].iloc[0]
    
    st.header("Selected Game:")
    st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>{game_details['name']}</p>", unsafe_allow_html=True)
    selected_game_url = f"https://rawg.io/games/{game_details['id']}"
    st.markdown(f"<a href='{selected_game_url}'><img src='{game_details['poster']}' width='600'></a>", unsafe_allow_html=True)
    
    about_text = game_details['about']
    if isinstance(about_text, list):
        about_text = ' '.join(about_text)
    st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>About:</p>", unsafe_allow_html=True)
    st.markdown(about_text)

    st.markdown("---")
    st.header("Recommended Games:")
    for name, poster, url in zip(recommended_game_names, recommended_game_posters, recommended_game_urls):
        st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>{name}</p>", unsafe_allow_html=True)
        st.markdown(f"<a href='{url}'><img src='{poster}' width='450'></a>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    reviews = game_details['reviews']
    st.markdown("<p style='font-size: 20px; font-weight: bold;'>Reviews:</p>", unsafe_allow_html=True)

    if reviews:
        st.markdown("<div style='max-height: 300px; overflow-y: auto;'>", unsafe_allow_html=True)
        for review in reviews:
            truncated_review = review[:512]
            sentiment_result = sentiment_analysis(truncated_review)
            sentiment_label = sentiment_result[0]['label']
            sentiment_color = "green" if sentiment_label == "POSITIVE" else "red"
            st.markdown(
                f"<div style='margin-bottom: 10px; border: 1px solid #ccc; padding: 10px; border-radius: 5px; overflow-y: auto;'>"
                f"<span style='color: {sentiment_color}; font-weight: bold;'>{sentiment_label}</span><br>{review}</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<p>No more reviews available.</p>", unsafe_allow_html=True)
