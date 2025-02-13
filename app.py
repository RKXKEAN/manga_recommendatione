from flask import Flask, render_template

app = Flask(__name__)

manga_list = [
    {
        "id": 1,
        "title": "One Piece",
        "author": "Eiichiro Oda",
        "genre": "Action, Adventure",
        "rating": 9.5,
        "description": "Monkey D. Luffy and his crew of pirates embark on a quest to find the One Piece treasure and become the Pirate King.",
    },
    {
        "id": 2,
        "title": "Attack on Titan",
        "author": "Hajime Isayama",
        "genre": "Action, Drama",
        "rating": 9.0,
        "description": "Eren Yeager and his friends join the Scout Regiment to fight the Titans and uncover the truth behind their existence.",
    },
    {
        "id": 3,
        "title": "Naruto",
        "author": "Masashi Kishimoto",
        "genre": "Action, Fantasy",
        "rating": 8.9,
        "description": "Naruto Uzumaki, a young ninja with a sealed demon fox spirit inside him, dreams of becoming the strongest ninja and the Hokage of his village.",
    },
    {
        "id": 4,
        "title": "My Hero Academia",
        "author": "Kohei Horikoshi",
        "genre": "Action, Superhero",
        "rating": 8.7,
        "description": "In a world of superpowers, Izuku Midoriya inherits One For All and trains at U.A. High to become a hero, facing rivals, villains, and his destiny.",
    },
    {
        "id": 5,
        "title": "Demon Slayer",
        "author": "Koyoharu Gotouge",
        "genre": "Action, Dark Fantasy",
        "rating": 8.6,
        "description": "Tanjiro Kamado becomes a demon slayer to avenge his family and cure his sister Nezuko, who is turning into a demon.",
    },
    {
        "id": 6,
        "title": "Black Clover",
        "author": "Yūki Tabata",
        "genre": "Action, Fantasy",
        "rating": 8.5,
        "description": "Asta and Yuno are orphans raised in a church. Yuno has exceptional magical powers while Asta has none. However, Asta receives the rare five-leaf clover grimoire that gives him the power of anti-magic.",
    },
    {
        "id": 7,
        "title": "One Punch",
        "author": "Yusuke Murata",
        "genre": "Action, Comedy",
        "rating": 8.4,
        "description": "Saitama is a hero who can defeat any opponent with a single punch but seeks a worthy opponent after growing bored by a lack of challenge in his fight against evil.",
    },
    {
        "id": 8,
        "title": "Tokyo Ghoul",
        "author": "Sui Ishida",
        "genre": "Action, Horror",
        "rating": 8.3,
        "description": "Ken Kaneki becomes a half-ghoul after a date with a beautiful.",
    },
    {
        "id": 9,
        "title": "The Promised Neverland",
        "author": "Kaiu Shirai",
        "genre": "Mystery, Thriller",
        "rating": 8.2,
        "description": "Emma, Norman, and Ray plan to escape from Grace Field House, an orphanage where children are raised as food for demons.",
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
