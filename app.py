import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
#similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Constants
API_KEY = '02dcab7bfa9d780d5a30cb03d8353250'
NUM_RECOMMENDATIONS = 10


# Check if similarity.pkl exists; if not, download it
if not os.path.exists("similarity.pkl"):
    file_id = "1EcYrKcwllvPIbqO9QIrtGPw3iufZA28A"  # replace with your actual file ID
    gdown.download(f"https://drive.google.com/uc?id={file_id}", "similarity.pkl", quiet=False)

# Now load it
with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

# Fetch poster from TMDB
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US',
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except requests.exceptions.RequestException:
        return None

# Recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    similar_movies = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:]  # exclude the selected movie itself

    recommended_names = []
    recommended_posters = []

    for i in similar_movies:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_names.append(movies.iloc[i[0]].title)
            recommended_posters.append(poster_url)
        if len(recommended_names) == NUM_RECOMMENDATIONS:
            break

    return recommended_names, recommended_posters

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Which movie are you looking for?", movies['title'].values)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie)

    if names:
        st.subheader("You might also like:")
        for i in range(0, len(names), 5):
            cols = st.columns(5)
            for col, name, poster in zip(cols, names[i:i+5], posters[i:i+5]):
                with col:
                    st.image(poster, use_container_width=True)
                    st.markdown(
                        f"<p style='text-align: center; font-weight: 600; font-size: 16px'>{name}</p>",
                        unsafe_allow_html=True
                    )
    else:
        st.warning("Sorry, no recommendations with posters available at the moment.")
