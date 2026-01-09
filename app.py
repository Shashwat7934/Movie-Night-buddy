import streamlit as st
import numpy as np
import pandas as pd
import pickle
import requests
import re
from time import sleep
from sklearn.metrics.pairwise import cosine_similarity

TMDB_API_KEY = "44f24091b8603b9f23460ba9efdc8c70"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

@st.cache_data(show_spinner=False)
def fetch_poster(title):
    import urllib.parse
    cleaned_title = re.sub(r"[^\w\s]", "", title).strip()

    params = {
        "api_key": TMDB_API_KEY,
        "query": cleaned_title,
        "include_adult": "false"
    }

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(TMDB_SEARCH_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            for result in results:
                poster_path = result.get("poster_path")
                result_title = result.get("title", "").lower()
                if poster_path and cleaned_title.lower() in result_title:
                    return TMDB_IMAGE_BASE_URL + poster_path

            for result in results:
                poster_path = result.get("poster_path")
                if poster_path:
                    return TMDB_IMAGE_BASE_URL + poster_path

        except Exception as e:
            print(f"[Retry {attempt + 1}] Poster error for '{title}': {e}")
            sleep(1)

    print(f"❌ Poster not found for: {title}")
    return "https://via.placeholder.com/200x300?text=Poster+Unavailable"

def clean_title(title):
    return re.sub(r"\s*\(\d{4}\)", "", title).strip()

with open("movies.pkl", "rb") as f:
    movies = pickle.load(f)

with open("genre_to_index.pkl", "rb") as f:
    genre_to_index = pickle.load(f)

def genre_to_vector(genres):
    vector = np.zeros(len(genre_to_index))
    for genre in genres:
        if genre in genre_to_index:
            vector[genre_to_index[genre]] = 1
    return vector

mood_keywords = {
    "Happy": ["Comedy", "Adventure", "Feel-Good"],
    "Sad": ["Drama", "Emotional", "Romance"],
    "Excited": ["Thriller", "Action"],
    "Bored": ["Mystery", "Mind-Bending"],
    "Romantic": ["Romance", "Drama"]
}

weather_genre_map = {
    "Sunny": ["Adventure", "Comedy"],
    "Rainy": ["Romance", "Drama"],
    "Cloudy": ["Sci-Fi", "Mystery"]
}

day_genre_map = {
    "Monday": ["Motivational", "Documentary"],
    "Tuesday": ["Drama", "Mystery"],
    "Wednesday": ["Crime", "Thriller"],
    "Thursday": ["Biography", "Adventure"],
    "Friday": ["Thriller", "Action"],
    "Saturday": ["Sci-Fi", "Fantasy"],
    "Sunday": ["Family", "Comedy"]
}

st.set_page_config(page_title="Movie Night Buddy", layout="wide")

st.markdown(
    """
    <style>
    html, body, .stApp {
        background-color: #121212;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .title-text {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #00BFFF;
    }
    .subtitle {
        color: #CCCCCC;
        font-size: 18px;
        text-align: center;
    }
    .movie-title {
        text-align: center;
        font-size: 14px;
        margin-top: 5px;
        color: #f0f0f0;
    }
    .chip {
        display: inline-block;
        padding: 4px 10px;
        margin: 2px;
        background-color: #333333;
        border-radius: 20px;
        color: white;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("🔍 Filter Your Preferences")
mood = st.sidebar.selectbox("🧠 What's your mood?", list(mood_keywords.keys()))
weather = st.sidebar.selectbox("🌤️ What's the weather like?", list(weather_genre_map.keys()))
day = st.sidebar.selectbox("🗓️ What day is it?", list(day_genre_map.keys()))
selected_genres = st.sidebar.multiselect("🎧 Any specific genres you like?", sorted(genre_to_index.keys()))

st.markdown("<div class='title-text'>🎬 MOVIE NIGHT BUDDY</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Get personalized recommendations based on your mood, weather, and day.</div>", unsafe_allow_html=True)

with st.expander("📘 About the App"):
    st.markdown("""
        **Movie Night Buddy** is your intelligent assistant for movie nights. Based on your mood, weather, day, and genre preferences, it recommends the top trending films that align with your current vibe. Enjoy posters, genres, and streamlined suggestions instantly.
    """)

search_query = st.text_input("🔎 Search for a movie (optional):", "").strip()

context_genres = set()
context_genres.update(mood_keywords.get(mood, []))
context_genres.update(weather_genre_map.get(weather, []))
context_genres.update(day_genre_map.get(day, []))
context_genres.update(selected_genres)

st.markdown("**🎯 Genres Used:**", unsafe_allow_html=True)
st.markdown("" + ''.join([f"<span class='chip'>{g}</span>" for g in context_genres]), unsafe_allow_html=True)

if search_query:
    st.subheader("🎯 Search Result")
    matched_movies = movies[movies['title'].str.contains(search_query, case=False, na=False)]

    if not matched_movies.empty:
        cols = st.columns(5)
        for i, (_, row) in enumerate(matched_movies.head(10).iterrows()):
            title_clean = clean_title(row['title'])
            poster_url = fetch_poster(title_clean)

            with cols[i % 5]:
                with st.spinner('Loading...'):
                    st.image(poster_url, use_container_width=True)
                st.markdown(f"<div class='movie-title'>{row['title']}</div>", unsafe_allow_html=True)
    else:
        st.warning("😕 No matching movies found.")

elif context_genres:
    user_vector = genre_to_vector(context_genres)

    if 'genre_vector' not in movies.columns:
        st.error("⚠️ Genre vectors are missing in the data.")
    else:
        movie_vectors = movies['genre_vector'].apply(np.array)
        similarity_scores = cosine_similarity([user_vector], list(movie_vectors))
        top_indices = np.argsort(similarity_scores[0])[::-1][:10]
        recommendations = movies.iloc[top_indices]

        st.subheader("🍿 Top Recommendations")
        cols = st.columns(5)
        for i, (_, row) in enumerate(recommendations.iterrows()):
            title_clean = clean_title(row['title'])
            poster_url = fetch_poster(title_clean)

            with cols[i % 5]:
                with st.spinner('Loading...'):
                    st.image(poster_url, use_container_width=True)
                st.markdown(f"<div class='movie-title'>{row['title']}</div>", unsafe_allow_html=True)

else:
    st.info("☝️ Select at least one mood, weather, or genre to get movie recommendations.")
