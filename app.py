from flask import Flask, render_template, request
import pandas as pd
from model import get_similar_movies_by_genre, evaluate_recommendation, recommend_movies_for_user_by_genre, \
    get_user_preferred_time

app = Flask(__name__)
movies = pd.read_csv("data/movies.csv")


@app.route("/")
def index():
    return render_template("index.html", movies=movies.to_dict(orient="records"))


@app.route("/recommend_by_genre", methods=["POST"])
def recommend_by_genre():
    selected_movies = request.form.getlist("movies")

    if not selected_movies:
        return render_template("recommendations.html", movies=[], selected_movies=[], message="⚠️ Hiç film seçmediniz!",
                               score=None)

    recommended_movies, avg_similarity = get_similar_movies_by_genre(selected_movies, movies)

    return render_template("recommendations.html",
                           movies=recommended_movies,
                           selected_movies=selected_movies,
                           score=avg_similarity)


@app.route("/knn_recommend", methods=["POST"])
def knn_recommend():
    user_id = request.form.get("user_id")

    if not user_id:
        return render_template("knn_recommendations.html", movies=[], message="⚠️ Kullanıcı ID girmelisiniz!")

    recommended_movies = recommend_movies_for_user_by_genre(int(user_id))

    if not recommended_movies:
        return render_template("knn_recommendations.html", movies=[], message="⚠️ Önerilecek film bulunamadı!")

    recommended_movies_df = movies[movies["movieId"].isin([movie["movieId"] for movie in recommended_movies])]
    accuracy = evaluate_recommendation(int(user_id), recommended_movies)
    preferred_time = get_user_preferred_time(int(user_id))

    return render_template("knn_recommendations.html",
                           movies=recommended_movies_df.to_dict(orient="records"),
                           accuracy=accuracy,
                           preferred_time=preferred_time)


if __name__ == "__main__":
    app.run(debug=True)
