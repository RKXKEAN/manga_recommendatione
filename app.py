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
        password = generate_password_hash(
            request.form["password"], method="pbkdf2:sha256"
        )
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!")
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
        genre = request.form["genre"]  # ⭐ รับ genre จากฟอร์ม
        new_manga = Manga(
            title=title,
            description=description,
            author=author,
            rating=rating,
            genre=genre,
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
