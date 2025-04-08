import streamlit as st  # To create main app.
import pickle  # To save the model.
import pandas as pd  # To create dataframe.
import requests  # To get the request.
import os  # To access environment variables

# Load environment variables
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '8265bd1679663a7ea12ac168da84d2e8')  # Default to current key if not set
PORT = int(os.getenv('PORT', 10000))  # Default port for Render

# Configure Streamlit to use the correct port
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Error handling for pickle loading
try:
    movies_dic = pickle.load(open('movies_dic.pkl', 'rb'))
    movies = pd.DataFrame(movies_dic)
    similarity = pickle.load(open('tag_similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading movie data: {str(e)}")
    st.stop()

def fetch_poster(movie_id):
    """This function use api to get the response and return the poster"""
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US",
            timeout=10
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        if 'poster_path' not in data or data['poster_path'] is None:
            return "https://via.placeholder.com/500x750.png?text=No+Poster+Available"
            
        return "https://image.tmdb.org/t/p/w500" + data['poster_path']
    except Exception as e:
        st.warning(f"Could not fetch poster for movie ID {movie_id}: {str(e)}")
        return "https://via.placeholder.com/500x750.png?text=Poster+Not+Found"

def recommendation(movie):
    """This function fetches the title and poster using the index."""
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])

    movies_recommended = []
    movies_recommended_poster = []
    for dist in distance[0:5]:
        movie_id = movies.iloc[dist[0]].id
        movies_recommended.append(movies.iloc[dist[0]].title)
        movies_recommended_poster.append((fetch_poster(movie_id)))
    return movies_recommended, movies_recommended_poster

st.title('AI-Powered Movie Recommender System')

select_movie = st.selectbox("What's in your mind", (movies['title'].values))

# creating a button for name and poster
if st.button('Recommend'):
    names, posters = recommendation(select_movie)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])


    col4, col5, col6 = st.columns(3)

    if len(names) > 3:
        with col4:
            st.text(names[3])
            st.image(posters[3])

    if len(names) > 4:
        with col5:
            st.text(names[4])
            st.image(posters[4])