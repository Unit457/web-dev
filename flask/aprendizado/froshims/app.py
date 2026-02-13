from cs50 import SQL
from flask import Flask, render_template, request

app = Flask(__name__)

db = SQL("sqlite:///froshims.db")

SPORTS = [
    "Basketball",
    "Soccer",
    "Ultimate Frisbee",
]

@app.route("/")
def index():
    return render_template("indexRadio.html", sports=SPORTS)

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")

    if not name:
        return render_template("error.html", error="Missing name.")

    sport = request.form.get("sport")

    if not sport:
        return render_template("error.html", error="Missing sport.")

    if sport not in SPORTS:
        return render_template("error.html", error="Sport does not exist.")

    db.execute("INSERT INTO registrants (name, sport) VALUES (?, ?)", name, sport)

    return render_template("success.html")

@app.route("/registrants")
def registrants():
    registrants = db.execute("SELECT name, sport FROM registrants")
    return render_template("registrants.html", registrants=registrants)
