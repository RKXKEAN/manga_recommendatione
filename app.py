from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///manga.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)


@app.route("/")
def home():
    mangas = Manga.query.all()
    return render_template("index.html", mangas=mangas)


@app.route("/manga/<int:manga_id>")
def manga_detail(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    return render_template("detail.html", manga=manga)


@app.route("/add", methods=["GET", "POST"])
def add_manga():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        rating = float(request.form["rating"])
        description = request.form["description"]
        new_manga = Manga(
            title=title,
            author=author,
            genre=genre,
            rating=rating,
            description=description,
        )
        db.session.add(new_manga)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")


@app.route("/delete/<int:manga_id>")
def delete_manga(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    db.session.delete(manga)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
