import streamlit as st
import pickle
import pandas as pd
import requests
import os
from pathlib import Path
import urllib.request

# Configure Streamlit
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Load environment variables
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    st.error("TMDB API key not found. Please set the TMDB_API_KEY environment variable.")
    st.stop()

# URLs for pickle files (you'll need to replace these with your actual URLs)
MOVIES_URL = os.getenv('MOVIES_PICKLE_URL', '')
SIMILARITY_URL = os.getenv('SIMILARITY_PICKLE_URL', '')

def download_pickle_file(url, filename):
    """Download pickle file from URL"""
    try:
        if not url:
            # If URL not provided, try to load local file
            with open(filename, 'rb') as f:
                return pickle.load(f)
        
        # Download from URL
        urllib.request.urlretrieve(url, filename)
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Error downloading/loading {filename}: {str(e)}")
        return None

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_API_KEY}"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('poster_path'):
            return "https://via.placeholder.com/500x750.png?text=No+Poster+Available"
            
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    except Exception as e:
        st.warning(f"Could not fetch poster: {str(e)}")
        return "https://via.placeholder.com/500x750.png?text=Poster+Not+Found"

def get_recommendations(movie):
    """Get movie recommendations based on similarity"""
    try:
        idx = st.session_state.movies[st.session_state.movies['title'] == movie].index[0]
        distances = sorted(
            list(enumerate(st.session_state.similarity[idx])),
            reverse=True,
            key=lambda x: x[1]
        )
        
        recommendations = []
        for i in distances[1:6]:  # Get top 5 recommendations (excluding the movie itself)
            movie_data = st.session_state.movies.iloc[i[0]]
            recommendations.append({
                'title': movie_data.title,
                'poster': fetch_poster(movie_data.id)
            })
        return recommendations
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return []

# Main UI
st.title('🎬 AI-Powered Movie Recommender')
st.write('Select a movie and get personalized recommendations!')

# Movie selection
selected_movie = st.selectbox(
    "Choose a movie you like",
    options=st.session_state.movies['title'].values
)

if st.button('Get Recommendations 🎯'):
    with st.spinner('Finding similar movies...'):
        recommendations = get_recommendations(selected_movie)
        
        if recommendations:
            cols = st.columns(5)
            for col, movie in zip(cols, recommendations):
                with col:
                    st.image(movie['poster'], use_column_width=True)
                    st.markdown(f"**{movie['title']}**")
        else:
            st.warning("Couldn't find recommendations at this time. Please try again.")