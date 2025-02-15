from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///manga.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    mangas = Manga.query.all()
    return render_template("index.html", mangas=mangas)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/add", methods=["GET", "POST"])
def add_manga():
    if "user_id" not in session:
        flash("You need to log in to add manga.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        rating = request.form["rating"]
        description = request.form["description"]

        new_manga = Manga(
            title=title,
            author=author,
            genre=genre,
            rating=float(rating),
            description=description,
        )
        db.session.add(new_manga)
        db.session.commit()

        flash("Manga added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/delete_manga/<int:id>", methods=["GET", "POST"])
def delete_manga(id):
    if "user_id" not in session:
        flash("You need to log in to delete manga.", "warning")
        return redirect(url_for("login"))

    manga = Manga.query.get_or_404(id)
    db.session.delete(manga)
    db.session.commit()

    flash(f'Manga "{manga.title}" has been deleted.', "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
