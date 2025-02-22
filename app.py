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
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///database.db"  # Database configuration using SQLite
)
app.config["SECRET_KEY"] = "your_secret_key"  # Secret key for session management
db = SQLAlchemy(app)  # Initialize the SQLAlchemy database
login_manager = LoginManager()  # Initialize the LoginManager
login_manager.init_app(app)  # Associate the LoginManager with the app
login_manager.login_view = "login"  # Set the login view for the LoginManager


# User model representing the user in the database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique user ID
    username = db.Column(db.String(150), unique=True, nullable=False)  # Unique username
    password = db.Column(db.String(150), nullable=False)  # User password (hashed)
    is_admin = db.Column(db.Boolean, default=False)  # Boolean to check if user is admin


# Manga model representing the manga details in the database
class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique manga ID
    title = db.Column(db.String(200), nullable=False)  # Manga title
    description = db.Column(db.Text, nullable=False)  # Manga description
    author = db.Column(db.String(100), nullable=False)  # Manga author
    rating = db.Column(db.Float, default=0.0)  # Manga rating
    genre = db.Column(db.String(100), nullable=False)  # Manga genre
    image_url = db.Column(db.String(500), nullable=True)  # URL for manga image


# Favorite model for managing user favorites
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique favorite ID
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Foreign key to user
    manga_id = db.Column(
        db.Integer, db.ForeignKey("manga.id"), nullable=False
    )  # Foreign key to manga
    user = db.relationship("User", backref="favorites")  # Relationship to User model
    manga = db.relationship(
        "Manga", backref="favorited_by"
    )  # Relationship to Manga model


# Function to load the user from the user ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Route for the index page, redirecting to the login page
@app.route("/")
def index():
    return redirect(url_for("login"))


# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]  # Get username from form
        password = request.form["password"]  # Get password from form
        user = User.query.filter_by(username=username).first()  # Query user by username
        if user and check_password_hash(user.password, password):  # Validate password
            login_user(user)  # Log in the user
            return redirect(url_for("home"))  # Redirect to home page
        else:
            flash("Invalid credentials")  # Flash message for invalid credentials
    return render_template("login.html")  # Render login template


# Route for the home page (after login)
@app.route("/home")
@login_required  # Require login to access this page
def home():
    mangas = Manga.query.all()  # Query all mangas
    return render_template(
        "home.html", mangas=mangas
    )  # Render home template with mangas


# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]  # Get username from form
        password = request.form["password"]  # Get password from form

        # Check if the username already exists in the database
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(
                url_for("register")
            )  # Redirect to register if username exists

        # Hash the password before saving to the database
        hashed_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        )
        new_user = User(
            username=username, password=hashed_password, is_admin=False
        )  # Create new user
        db.session.add(new_user)  # Add user to the session
        db.session.commit()  # Commit changes to the database
        flash(
            "Registration successful! You can now log in.", "success"
        )  # Flash success message
        return redirect(url_for("login"))  # Redirect to login
    return render_template("register.html")  # Render registration template


# Route for user logout
@app.route("/logout")
@login_required  # Require login to access this page
def logout():
    logout_user()  # Log out the user
    return redirect(url_for("home"))  # Redirect to home page


# Route for the admin page
@app.route("/admin")
@login_required  # Require login to access this page
def admin():
    if not current_user.is_admin:  # Check if user is admin
        return redirect(url_for("home"))  # Redirect to home if not admin
    mangas = Manga.query.all()  # Query all mangas
    return render_template(
        "admin.html", mangas=mangas
    )  # Render admin template with mangas


# Route to add new manga
@app.route("/add_manga", methods=["GET", "POST"])
@login_required  # Require login to access this page
def add_manga():
    if not current_user.is_admin:  # Check if user is admin
        return redirect(url_for("home"))  # Redirect to home if not admin

    if request.method == "POST":
        title = request.form["title"]  # Get manga title from form
        description = request.form["description"]  # Get manga description from form
        author = request.form["author"]  # Get manga author from form
        rating = float(request.form["rating"])  # Get manga rating from form
        genre = request.form["genre"]  # Get manga genre from form
        image_url = request.form["image_url"]  # Get manga image URL from form

        new_manga = Manga(  # Create new manga
            title=title,
            description=description,
            author=author,
            rating=rating,
            genre=genre,
            image_url=image_url,
        )
        db.session.add(new_manga)  # Add manga to the session
        db.session.commit()  # Commit changes to the database
        flash("Manga added successfully!")  # Flash success message
        return redirect(url_for("admin"))  # Redirect to admin page

    return render_template("add_manga.html")  # Render add manga template


# Route to edit existing manga
@app.route("/edit_manga/<int:id>", methods=["GET", "POST"])
@login_required  # Require login to access this page
def edit_manga(id):
    if not current_user.is_admin:  # Check if user is admin
        return redirect(url_for("home"))  # Redirect to home if not admin

    manga = Manga.query.get_or_404(id)  # Get manga by ID or return 404 if not found
    if request.method == "POST":
        manga.title = request.form["title"]  # Update manga title
        manga.description = request.form["description"]  # Update manga description
        manga.author = request.form["author"]  # Update manga author
        manga.image_url = request.form["image_url"]  # Update manga image URL
        db.session.commit()  # Commit changes to the database
        flash("Manga updated successfully!")  # Flash success message
        return redirect(url_for("admin"))  # Redirect to admin page

    return render_template("edit_manga.html", manga=manga)  # Render edit manga template


# Route to delete manga
@app.route("/delete_manga/<int:id>", methods=["POST"])
@login_required  # Require login to access this page
def delete_manga(id):
    if not current_user.is_admin:  # Check if user is admin
        return redirect(url_for("home"))  # Redirect to home if not admin

    manga = Manga.query.get_or_404(id)  # Get manga by ID or return 404 if not found
    db.session.delete(manga)  # Delete manga from session
    db.session.commit()  # Commit changes to the database
    flash("Manga deleted successfully!")  # Flash success message
    return redirect(url_for("admin"))  # Redirect to admin page


# Route for manga details
@app.route("/manga/<int:id>")
def manga_detail(id):
    manga = Manga.query.get_or_404(id)  # Get manga by ID or return 404 if not found
    return render_template(
        "manga_detail.html", manga=manga
    )  # Render manga detail template


# Route for searching mangas
@app.route("/search")
def search():
    query = request.args.get("query", "")  # Get search query from request
    if query:
        mangas = Manga.query.filter(
            Manga.title.ilike(f"%{query}%")
        ).all()  # Search mangas by title
    else:
        mangas = []  # Empty list if no query is provided
    return render_template(
        "search.html", mangas=mangas, query=query
    )  # Render search template


# Route to add or remove manga from favorites
@app.route("/favorite/<int:id>")
@login_required  # Require login to access this page
def favorite_manga(id):
    manga = Manga.query.get_or_404(id)  # Get manga by ID or return 404 if not found
    favorite = Favorite.query.filter_by(
        user_id=current_user.id, manga_id=id
    ).first()  # Check if manga is favorited

    if favorite:
        db.session.delete(favorite)  # Remove from favorites if already favorited
        flash("Removed from favorites!")  # Flash success message
    else:
        new_favorite = Favorite(
            user_id=current_user.id, manga_id=id
        )  # Create new favorite entry
        db.session.add(new_favorite)  # Add favorite to session
        flash("Added to favorites!")  # Flash success message

    db.session.commit()  # Commit changes to the database
    return redirect(url_for("manga_detail", id=id))  # Redirect to manga detail page


# Route for top mangas based on rating
@app.route("/top_mangas")
def top_mangas():
    top_mangas = (
        Manga.query.order_by(Manga.rating.desc()).limit(10).all()
    )  # Get top 10 mangas by rating
    return render_template(
        "top_mangas.html", mangas=top_mangas
    )  # Render top mangas template


# Route for user favorites
@app.route("/favorites")
@login_required  # Require login to access this page
def favorites():
    favorite_mangas = [
        fav.manga for fav in current_user.favorites
    ]  # Get all favorite mangas for the user
    return render_template(
        "favorites.html", mangas=favorite_mangas
    )  # Render favorites template


# Route for about page
@app.route("/about")
@login_required  # Require login to access this page
def about():
    favorite_count = Favorite.query.filter_by(
        user_id=current_user.id
    ).count()  # Count user's favorites
    return render_template(
        "about.html", favorite_count=favorite_count
    )  # Render about template


# Route for contact page
@app.route("/contact", methods=["GET", "POST"])
@login_required  # Require login to access this page
def contact():
    if request.method == "POST":
        name = request.form["name"]  # Get name from form
        email = request.form["email"]  # Get email from form
        message = request.form["message"]  # Get message from form

        # Here you can add code to handle the submitted data, e.g., send an email or save to the database
        flash("Your message has been sent!", "success")  # Flash success message
        return redirect(url_for("contact"))  # Redirect to contact page

    return render_template("contact.html")  # Render contact template


# Run the application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)  # Run the app in debug mode
