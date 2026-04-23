import streamlit as st
import pickle as pkl
import pandas as pd
import requests

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

st.title("🎬 Movie Recommender System")

# ---------------- API FUNCTION ----------------

@st.cache_data
def fetch_movie_details(movie_title):

    try:

        # Extract year if exists
        year = None
        if "(" in movie_title and ")" in movie_title:
            year = movie_title.split("(")[-1].replace(")", "").strip()
            movie_title = movie_title.split("(")[0].strip()

        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": "bd21829c7cb007beb86b54f3696c1dc4",
            "query": movie_title,
            "year": year,
            "include_adult": False
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data["results"]:

            # choose best match with poster available
            for result in data["results"]:
                if result.get("poster_path"):

                    poster_path = result["poster_path"]
                    rating = result.get("vote_average", "N/A")
                    release_date = result.get("release_date", "")
                    overview = result.get("overview", "")

                    year = release_date[:4] if release_date else "N/A"

                    poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"

                    return poster_url, rating, year, overview

        return "https://via.placeholder.com/500x750?text=Poster+Unavailable", "N/A", "N/A", None

    except:
        return "https://via.placeholder.com/500x750?text=Connection+Error", "N/A", "N/A", None
# ---------------- RECOMMEND FUNCTION ----------------

def recommend(movie):

    movie_index = movies[movies['title'] == movie].index[0]
    distance = sim[movie_index]

    movies_list = sorted(
        list(enumerate(distance)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended = []

    for i in movies_list:

        title = movies.iloc[i[0]]['title']
        movie_id = movies.iloc[i[0]]['id']

        similarity_score = round(i[1] * 100, 2)

        poster, rating, year, overview = fetch_movie_details(title)

        recommended.append(
            (title, similarity_score, poster, rating, year, overview)
        )

    return recommended


# ---------------- LOAD DATA ----------------

sim = pkl.load(open('sim.pkl', 'rb'))
movies_dict = pkl.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)


# ---------------- UI SELECT BOX ----------------

selected_movie = st.selectbox(
    "🔍 Search or select a movie",
    movies['title'].values
)


# ---------------- BUTTON ----------------

if st.button("Recommend"):

    recommendations = recommend(selected_movie)

    cols = st.columns(5)

    for idx, movie_data in enumerate(recommendations):

        title = movie_data[0]
        similarity = movie_data[1]

        poster, rating, year, overview = fetch_movie_details(title)

        with cols[idx]:

            if poster:
                st.image(poster)

            st.markdown(f"### {title}")

            st.caption(f"⭐ {rating} | 📅 {year}")
            st.caption(f"🎯 Similarity Score: {similarity}%")

            if overview:
                with st.expander("📖 Overview"):
                    st.write(overview)