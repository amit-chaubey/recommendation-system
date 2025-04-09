import streamlit as st
import pickle
import pandas as pd
import requests
import os
from pathlib import Path
import urllib.parse

# Configure Streamlit - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Debug information at the very start
st.write("Environment Variables Debug:")
st.write("MOVIES_PICKLE_URL exists:", os.getenv('MOVIES_PICKLE_URL') is not None)
st.write("SIMILARITY_PICKLE_URL exists:", os.getenv('SIMILARITY_PICKLE_URL') is not None)
st.write("Raw MOVIES_PICKLE_URL:", os.getenv('MOVIES_PICKLE_URL', 'Not found'))

def convert_drive_link(url):
    """Convert Google Drive link to direct download link"""
    try:
        if not url:
            st.error("URL is empty")
            return ''
        if 'drive.google.com' in url:
            # Extract file ID from the URL
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
                st.write(f"Extracted file ID: {file_id}")
            elif 'id=' in url:
                file_id = url.split('id=')[1].split('&')[0]
                st.write(f"Extracted file ID: {file_id}")
            else:
                st.error(f"Invalid Google Drive URL format: {url}")
                return ''
            
            # Create the direct download link
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            st.write(f"Created download URL: {download_url}")
            return download_url
        return url
    except Exception as e:
        st.error(f"Error processing URL: {str(e)}")
        return ''

# Initialize session state first
if 'movies' not in st.session_state or 'similarity' not in st.session_state:
    st.session_state.movies = None
    st.session_state.similarity = None

# Load environment variables
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    st.error("TMDB API key not found. Please set the TMDB_API_KEY environment variable.")
    st.stop()

# URLs for pickle files
MOVIES_URL = convert_drive_link(os.getenv('MOVIES_PICKLE_URL', ''))
SIMILARITY_URL = convert_drive_link(os.getenv('SIMILARITY_PICKLE_URL', ''))

# Debug information
st.write("Debug Info:")
st.write(f"Movies URL: {MOVIES_URL}")
st.write(f"Similarity URL: {SIMILARITY_URL}")

def download_pickle_file(url, filename):
    """Download pickle file from URL"""
    try:
        if not url:
            # If URL not provided, try to load local file
            if not os.path.exists(filename):
                st.error(f"Error: {filename} not found and no URL provided")
                return None
            with open(filename, 'rb') as f:
                return pickle.load(f)
        
        # Download from URL
        st.write(f"Downloading {filename}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Save the file
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Load the downloaded file
        with open(filename, 'rb') as f:
            return pickle.load(f)
            
    except Exception as e:
        st.error(f"Error downloading/loading {filename}: {str(e)}")
        return None

# Load data if not already in session state
if st.session_state.movies is None or st.session_state.similarity is None:
    try:
        # Load movie data
        movies_dic = download_pickle_file(MOVIES_URL, 'movies_dic.pkl')
        if movies_dic is None:
            st.error("Failed to load movies data. Please check MOVIES_PICKLE_URL environment variable.")
            st.stop()
        
        movies_df = pd.DataFrame(movies_dic)
        
        # Load similarity matrix
        similarity = download_pickle_file(SIMILARITY_URL, 'tag_similarity.pkl')
        if similarity is None:
            st.error("Failed to load similarity data. Please check SIMILARITY_PICKLE_URL environment variable.")
            st.stop()
            
        # Update session state
        st.session_state.movies = movies_df
        st.session_state.similarity = similarity
            
    except Exception as e:
        st.error(f"Error initializing data: {str(e)}")
        st.stop()

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
        if st.session_state.movies is None or st.session_state.similarity is None:
            st.error("Movie data not properly loaded")
            return []
            
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
try:
    if st.session_state.movies is not None:
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
    else:
        st.error("Movie data not loaded. Please check your environment variables and try again.")
except Exception as e:
    st.error(f"Error in UI: {str(e)}")
    st.stop()