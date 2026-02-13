from cs50 import SQL
from flask import Flask, render_template, redirect, request, session
from flask_session import Session

app = Flask(__name__)

db = SQL("sqlite:///store.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def shop():
    books = db.execute("SELECT * FROM books")
    return render_template("shop.html", name=session.get("name"), books=books)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if "cart" not in session:
        session["cart"] = []

    if request.method == "POST":
        book_id = request.form.get("id")
        if request.form.get("cartaction") == "remove":
            session["cart"].remove(book_id)
            return redirect("/cart")
        elif request.form.get("cartaction") == "add":
            session["cart"].append(book_id)
            return redirect("/cart")

    books = db.execute("SELECT * FROM books WHERE id IN (?)", session["cart"])
    return render_template("cart.html", books=books)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
