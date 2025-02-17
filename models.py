from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# สร้างตัวแปรฐานข้อมูล
db = SQLAlchemy()


# โมเดลสำหรับผู้ใช้
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


# โมเดลสำหรับมังงะ
class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
