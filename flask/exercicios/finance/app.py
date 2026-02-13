import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Pega todas as holdings do usuário bem como o seu dinheiro
    stocks = db.execute("SELECT * FROM holdings WHERE user_id = ?", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash[0]["cash"]
    total_cash = cash

    # Atualiza seus preços
    for stock in stocks:
        current_price = lookup(stock["symbol"])
        current_price = current_price["price"]
        stock_symbol = stock["symbol"]
        shares = db.execute("SELECT shares FROM holdings WHERE symbol = ? AND user_id = ?", stock_symbol, session["user_id"])[0]["shares"]
        db.execute("UPDATE holdings SET price = ?, holding = ?*? WHERE symbol = ? AND user_id = ?", current_price, current_price, shares, stock_symbol, session["user_id"])
        # Adiciona o valor da holding atualizada em total_cash
        total_cash+=stock["holding"]

    return render_template("index.html", cash=cash, total_cash=total_cash, stocks=stocks)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Checa a validade do símbolo inserido
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Blank symbol.")

        stock = lookup(symbol)
        if not stock:
            return apology("Invalid symbol.")

        # Checa a validade do número de shares inserido
        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("You can't add fractionary numbers.")
        if shares < 1:
            return apology("You must buy at least one share.")

        # Pega o preço do stock e o dinheiro do usuário
        stock_price = stock["price"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = cash[0]["cash"]

        # Calcula o valor da holding a ser adquirida
        holding_value = stock_price*shares

        # Se o valor for maior que o dinheiro do usuário, ele não pode comprar
        if holding_value > cash:
            return apology("You don't have enough cash to buy this.")

        # Checa se o usuário já tem uma holding desse stock
        holding = db.execute("SELECT * FROM holdings WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)

        # Se tiver, atualize seus números de shares e holding value
        if holding:
            db.execute("UPDATE holdings SET shares = ?+?, holding = ?+? WHERE user_id = ? AND symbol = ?", holding[0]["shares"], shares, holding[0]["holding"], holding_value, session["user_id"], symbol)
        # Se não, insere a holding nova na db
        else:
            db.execute("INSERT INTO holdings (user_id, symbol, price, shares, holding) VALUES (?, ?, ?, ?, ?)", session["user_id"], symbol, stock_price, shares, holding_value)

        # Pega a data
        date = datetime.now(timezone.utc)
        date = str(date)[:19]

        # Insere dados da transação em transactions
        action = "Purchase"
        db.execute("INSERT INTO transactions (user_id, action, symbol, price, shares, date) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], action, symbol, stock_price, shares, date)

        # Atualiza o dinheiro do usuário
        new_cash = cash-holding_value
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    # Pega todas as holdings do usuário bem como o seu dinheiro
    stocks = db.execute("SELECT * FROM holdings WHERE user_id = ?", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash[0]["cash"]
    total_cash = cash

    # Atualiza seus preços
    for stock in stocks:
        current_price = lookup(stock["symbol"])
        current_price = current_price["price"]
        stock_symbol = stock["symbol"]
        shares = db.execute("SELECT shares FROM transactions WHERE symbol = ? AND user_id = ?", stock_symbol, session["user_id"])[0]["shares"]
        db.execute("UPDATE holdings SET price = ?, holding = ?*? WHERE symbol = ? AND user_id = ?", current_price, current_price, shares, stock_symbol, session["user_id"])
        total_cash+=stock["holding"]

    # Pega todas as transações do usuário e as ordena em decrescente (mais recente ao menos recente)
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC", session["user_id"])
    return render_template("history.html", transactions=transactions, cash=cash, total_cash=total_cash)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Blank symbol.")

        stock = lookup(symbol)
        if not stock:
            return apology("Invalid symbol.")

        return render_template("quoted.html", stock=stock)

    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Pega todos os valores da form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Checa a validade de username
        if not username:
            return apology("Username is blank.")

        # Checa a validade da senha
        if not password:
            return apology("Password is blank.")

        # Checa a validade da confirmação
        if not confirmation:
            return apology("Confirmation is blank.")

        # Checa se a senha e a confirmação são iguais
        if password != confirmation:
            return apology("Confirmation does not match password.")

        # Checa se o username tem espaços
        for i in username:
            if i == " ":
                return apology("Can't have spaces in username.")

        # Checa se password tem espaços
        for i in password:
            if i == " ":
                return apology("Can't have spaces in password.")

        # Hash senha
        passwordHash = generate_password_hash(password)

        # Tenta inserir o usuário e o hash da senha na database
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, passwordHash)
        # Se o username já existir:
        except ValueError:
            return apology("Username already exists.")

        # Esquece o log in anterior
        session.clear()

        # Pega o username na database
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )

        # Armazena seu ID na sessão
        session["user_id"] = rows[0]["id"]

        # Redireciona usuário para a homepage
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":

        # Checa a validade do símbolo selecionado
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("You have to select a stock to sell.")

        # Checa se o usuário possui alguma holding nesse stock
        holding = db.execute("SELECT * FROM holdings WHERE symbol = ? AND user_id = ?", symbol, session["user_id"])
        if not holding:
            return apology("You have no shares of that stock.")

        # Checa a validade do número de shares
        shares = int(request.form.get("shares"))
        if shares < 0:
            return apology("You have to buy at least one share.")

        # Checa se o usuário possui o número de shares que está tentando vender
        if holding[0]["shares"] < shares:
            return apology("You don't own that many shares of that stock.")

        # Pega o dinheiro do usuário
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = cash[0]["cash"]

        # Pega o preço do stock e o preço da venda
        stock_price = lookup(symbol)["price"]
        sold_value = stock_price*shares

        # Atualiza o dinheiro do usuário
        new_cash = cash+sold_value
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])

        # Atualiza a holding do stock que foi vendido
        db.execute("UPDATE holdings SET shares = ?-?, holding = ?-? WHERE symbol = ? AND user_id = ?", holding[0]["shares"], shares, holding[0]["holding"], sold_value, symbol, session["user_id"])

        # Pega a holding do stock que foi vendido
        holding = db.execute("SELECT * FROM holdings WHERE symbol = ? AND user_id = ?", symbol, session["user_id"])

        # Se o usuário não possui mais shares, apague a holding
        if holding[0]["shares"] == 0:
            db.execute("DELETE FROM holdings WHERE symbol = ? AND user_id = ?", symbol, session["user_id"])

        # Pega a data
        date = datetime.now(timezone.utc)
        date = str(date)[:19]

        # Insere dados da transação em transactions
        action = "Sale"
        db.execute("INSERT INTO transactions (user_id, action, symbol, price, shares, date) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], action, symbol, stock_price, shares, date)

        return redirect("/")

    else:
        stocks = db.execute("SELECT * FROM holdings WHERE user_id = ?", session["user_id"])
        return render_template("sell.html", stocks=stocks)

@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():

    # Pega o dinheiro do usuário
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash[0]["cash"]

    if request.method == "GET":
        return render_template("cash.html", cash=cash)
    else:

        # Checa validade da quantia de dinheiro inserida
        addcash = request.form.get("addcash")
        if addcash <= 0:
            return apology("Can't add 0 cash")

        # Atualiza dinheiro do usuário
        db.execute("UPDATE users SET cash = ?+? WHERE id = ?", cash, addcash, session["user_id"])
        redirect("/")


