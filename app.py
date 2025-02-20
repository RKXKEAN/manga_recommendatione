from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "your_secret_key"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, default=0.0)
    genre = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey("manga.id"), nullable=False)
    user = db.relationship("User", backref="favorites")
    manga = db.relationship("Manga", backref="favorited_by")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return redirect(url_for("login"))  # Redirect ไปหน้า login


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")


@app.route("/home")
@login_required
def home():
    mangas = Manga.query.all()
    return render_template("home.html", mangas=mangas)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # ตรวจสอบว่าชื่อผู้ใช้นั้นมีอยู่แล้วในฐานข้อมูลหรือไม่
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        )
        new_user = User(username=username, password=hashed_password, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for("home"))
    mangas = Manga.query.all()
    return render_template("admin.html", mangas=mangas)


@app.route("/add_manga", methods=["GET", "POST"])
@login_required
def add_manga():
    if not current_user.is_admin:
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        author = request.form["author"]
        rating = float(request.form["rating"])
        genre = request.form["genre"]
        image_url = request.form["image_url"]  # ⭐ รับค่า URL รูปภาพ

        new_manga = Manga(
            title=title,
            description=description,
            author=author,
            rating=rating,
            genre=genre,
            image_url=image_url,
        )
        db.session.add(new_manga)
        db.session.commit()
        flash("Manga added successfully!")
        return redirect(url_for("admin"))

    return render_template("add_manga.html")


@app.route("/edit_manga/<int:id>", methods=["GET", "POST"])
@login_required
def edit_manga(id):
    if not current_user.is_admin:
        return redirect(url_for("home"))

    manga = Manga.query.get_or_404(id)
    if request.method == "POST":
        manga.title = request.form["title"]
        manga.description = request.form["description"]
        manga.author = request.form["author"]
        manga.image_url = request.form["image_url"]  # ⭐ อัปเดตรูปภาพ
        db.session.commit()
        flash("Manga updated successfully!")
        return redirect(url_for("admin"))

    return render_template("edit_manga.html", manga=manga)


@app.route("/delete_manga/<int:id>", methods=["POST"])
@login_required
def delete_manga(id):
    if not current_user.is_admin:
        return redirect(url_for("home"))

    manga = Manga.query.get_or_404(id)
    db.session.delete(manga)
    db.session.commit()
    flash("Manga deleted successfully!")
    return redirect(url_for("admin"))


@app.route("/manga/<int:id>")
def manga_detail(id):
    manga = Manga.query.get_or_404(id)
    return render_template("manga_detail.html", manga=manga)


@app.route("/search")
def search():
    query = request.args.get("query", "")
    if query:
        mangas = Manga.query.filter(Manga.title.ilike(f"%{query}%")).all()
    else:
        mangas = []
    return render_template("search.html", mangas=mangas, query=query)


@app.route("/favorite/<int:id>")
@login_required
def favorite_manga(id):
    manga = Manga.query.get_or_404(id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, manga_id=id).first()

    if favorite:
        db.session.delete(favorite)
        flash("Removed from favorites!")
    else:
        new_favorite = Favorite(user_id=current_user.id, manga_id=id)
        db.session.add(new_favorite)
        flash("Added to favorites!")

    db.session.commit()
    return redirect(url_for("manga_detail", id=id))


@app.route("/top_mangas")
def top_mangas():
    top_mangas = Manga.query.order_by(Manga.rating.desc()).limit(10).all()
    return render_template("top_mangas.html", mangas=top_mangas)


@app.route("/favorites")
@login_required
def favorites():
    favorite_mangas = [fav.manga for fav in current_user.favorites]
    return render_template("favorites.html", mangas=favorite_mangas)


@app.route("/about")
@login_required
def about():
    favorite_count = Favorite.query.filter_by(user_id=current_user.id).count()
    return render_template("about.html", favorite_count=favorite_count)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
