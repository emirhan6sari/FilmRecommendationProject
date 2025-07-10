#Pocahontas filmi seçilirse farklı renkte filmler çıkıyor.
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from datetime import datetime

# Veri Yükleme
movies_df = pd.read_csv("data/movies.csv")
ratings = pd.read_csv("data/ratings.csv")
movies_df["genres"] = movies_df["genres"].fillna("")

# Tür İşleme
unique_genres = set(genre for genres in movies_df["genres"] for genre in genres.split("|"))
for genre in unique_genres:
    movies_df[genre] = movies_df["genres"].apply(lambda x: 1 if genre in x else 0)

genre_features = movies_df[list(unique_genres)].values
genre_similarity = cosine_similarity(genre_features)
genre_similarity_df = pd.DataFrame(genre_similarity, index=movies_df["movieId"], columns=movies_df["movieId"])

# Film Bazlı Öneri
def get_similar_movies_by_genre(selected_movies, movies_df, num_recommendations=5):
    if not selected_movies:
        return [], 0

    movie_ids = movies_df[movies_df["title"].isin(selected_movies)]["movieId"].tolist()
    movie_ids = [mid for mid in movie_ids if mid in genre_similarity_df.index]

    if not movie_ids:
        return [], 0

    similarity_scores = genre_similarity_df.loc[movie_ids].mean(axis=0)
    sorted_similar_movies = similarity_scores.sort_values(ascending=False)
    sorted_similar_movies = sorted_similar_movies.drop(index=movie_ids, errors='ignore')

    recommended_movie_ids = sorted_similar_movies.head(num_recommendations).index.tolist()
    recommended_scores = sorted_similar_movies.head(num_recommendations).values.tolist()

    recommended_movies = []
    for mid, score in zip(recommended_movie_ids, recommended_scores):
        movie_info = movies_df[movies_df["movieId"] == mid].iloc[0]
        percent_score = score * 100
        if percent_score < 60:
            color = "red-bg"
        elif percent_score < 90:
            color = "orange-bg"
        else:
            color = "green-bg"
        recommended_movies.append({
            "title": movie_info["title"],
            "similarity": round(percent_score, 2),
            "color": color
        })

    avg_cosine_similarity = np.mean([m["similarity"] for m in recommended_movies])
    return recommended_movies, avg_cosine_similarity

# Kullanıcı Bazlı Öneri
def recommend_movies_for_user_by_genre(user_id, num_recommendations=5):
    user_ratings = ratings[ratings["userId"] == user_id]
    user_watched_movies = set(user_ratings["movieId"])
    watched_movie_genres = movies_df[movies_df["movieId"].isin(user_watched_movies)]
    genres_list = watched_movie_genres["genres"].str.split("|").explode().tolist()
    genre_counts = Counter(genres_list)
    most_common_genres = genre_counts.most_common(3)
    genres_to_consider = [genre for genre, _ in most_common_genres]

    recommended_movies = []

    if len(genres_to_consider) >= 2:
        genre_movies = movies_df[movies_df[genres_to_consider[0]] == 1]
        for genre in genres_to_consider[1:]:
            genre_movies = genre_movies[genre_movies[genre] == 1]
        for movie_id in genre_movies["movieId"]:
            if movie_id not in user_watched_movies:
                recommended_movies.append(movie_id)
                if len(recommended_movies) >= num_recommendations:
                    break

    if len(recommended_movies) < num_recommendations:
        genre_movies = movies_df[movies_df[genres_to_consider[0]] == 1]
        for movie_id in genre_movies["movieId"]:
            if movie_id not in user_watched_movies:
                recommended_movies.append(movie_id)
                if len(recommended_movies) >= num_recommendations:
                    break

    recommended_movies_df = movies_df[movies_df["movieId"].isin(recommended_movies)]
    return recommended_movies_df.to_dict(orient="records")

# Ortalama Rating Farkı
def get_true_liked_movies(user_id, threshold=2.0):
    user_ratings = ratings[ratings["userId"] == user_id]
    return user_ratings[user_ratings["rating"] >= threshold]["movieId"].tolist()

def evaluate_recommendation(user_id, recommended_movies):
    if not recommended_movies:
        return {"rating_diff": 0}

    recommended_movie_ids = [movie["movieId"] if isinstance(movie, dict) else movie for movie in recommended_movies]
    true_liked_movies = get_true_liked_movies(user_id)
    if not true_liked_movies:
        return {"rating_diff": 0}

    recommended_ratings = ratings[ratings["movieId"].isin(recommended_movie_ids)]["rating"].mean()
    true_ratings = ratings[ratings["movieId"].isin(true_liked_movies)]["rating"].mean()

    rating_diff = abs(recommended_ratings - true_ratings) if not pd.isna(recommended_ratings) and not pd.isna(true_ratings) else 0
    return {"rating_diff": rating_diff}

# Favori İzleme Zamanı
def get_user_preferred_time(user_id):
    user_ratings = ratings[ratings["userId"] == user_id]
    times = pd.to_datetime(user_ratings["timestamp"], unit='s')
    day = sum(6 <= t.hour < 18 for t in times)
    night = len(times) - day
    return "Gündüz saatleri ☀️" if day >= night else "Gece saatleri 🌙"
