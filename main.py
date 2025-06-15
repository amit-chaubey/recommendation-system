import streamlit as st  # To create main app.
import pickle  # To save the model.
import pandas as pd  # To create dataframe.
import requests  # To get the request.
import os
import gdown

# Load environment variables
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '8265bd1679663a7ea12ac168da84d2e8')  # Fallback to default key if not set

def download_from_gdrive(file_id, dest_path):
    if not os.path.exists(dest_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, dest_path, quiet=False)

# Google Drive file IDs
MOVIES_DIC_ID = "1GE19JsLWNSTWUwVS_EuiZsNy_2D8EQJO"  # movies_dic.pkl
TAG_SIMILARITY_ID = "12dYavQGQTB6e6KSFEFhwMSUzo_08DU8A"  # tag_similarity.pkl
MOVIES_ID = "1J3qwqguOYPpBYGyj5KZhI1tyGxKZzimx"  # movies.pkl

download_from_gdrive(MOVIES_DIC_ID, "movies_dic.pkl")
download_from_gdrive(TAG_SIMILARITY_ID, "tag_similarity.pkl")
download_from_gdrive(MOVIES_ID, "movies.pkl")

# Now load as usual
movies_dic = pickle.load(open('movies_dic.pkl', 'rb'))
movies = pd.DataFrame(movies_dic)
similarity = pickle.load(open('tag_similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    """This function use api to get the response and return the poster"""
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US")
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

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