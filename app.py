from flask import Flask, render_template

app = Flask(__name__)

manga_list = [
    {
        "id": 1,
        "title": "One Piece",
        "author": "Eiichiro Oda",
        "genre": "Action, Adventure",
        "rating": 9.5,
        "description": "A story about pirates and the search for the ultimate treasure, One Piece.",
    },
    {
        "id": 2,
        "title": "Attack on Titan",
        "author": "Hajime Isayama",
        "genre": "Action, Drama",
        "rating": 9.0,
        "description": "Humanity's battle against giant humanoid Titans.",
    },
    {
        "id": 3,
        "title": "Naruto",
        "author": "Masashi Kishimoto",
        "genre": "Action, Fantasy",
        "rating": 8.9,
        "description": "A young ninja's journey to become the strongest Hokage.",
    },
]


@app.route("/")
def home():
    return render_template("index.html", manga_list=manga_list)


@app.route("/manga/<int:manga_id>")
def manga_detail(manga_id):
    manga = next((m for m in manga_list if m["id"] == manga_id), None)
    if manga:
        return render_template("detail.html", manga=manga)
    return "Manga not found", 404


if __name__ == "__main__":
    app.run(debug=True)
