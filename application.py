import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Ensure environment variable is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///JAWS.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pictures", methods=["GET", "POST"])
def pictures():
    if request.method == "POST":

        """Check if they entered a year"""
        if not request.form.get("year"):
            return apology("Please enter a year", 403)

        """Check if they entered which season"""
        if not request.form.get("season"):
            return apology("Please enter a season", 403)

        if ((request.form.get("year") == "2018") & (request.form.get("season") == "Spring")):
            return render_template("getpicture.html", link = "https://drive.google.com/drive/folders/1FmEuX1r0LSMAMoGqhN4Ky36p7O7cekOx")

        else:
            return render_template("comingsoon.html")

    else:
        return render_template("pictures.html")

@app.route("/signups", methods=["GET", "POST"])
def signups():
    if request.method == "POST":
        if not ("user_id" in session.keys()):
            return redirect("/login")
        name = db.execute("SELECT name FROM users WHERE username == :username", username = session["user_id"])
        """Check if already signed up"""
        rows = db.execute("Select * FROM Signup WHERE Name == :naame", naame = name[0][0])
        for i in range(len(rows)):
            if request.form.get("wednesday"):
                if rows[i]["day"] == "Wednesday":
                    return apology("Oops! You've already signed up for Wednesday.", 403)
            if request.form.get("saturday"):
                if rows[i]["day"] == "Saturday":
                    return apology("Oops! You've already signed up for Saturday.", 403)
            if request.form.get("sunday"):
                if rows[i]["day"] == "Sunday":
                    return apology("Oops! You've already signed up for Sunday.", 403)
        """Sign Up"""
        if request.form.get("ride"):
            if request.form.get("wednesday"):
                db.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "True", day = "Wednesday")
            if request.form.get("sunday"):
                db.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "True", day = "Saturday")
            if request.form.get("saturday"):
                db.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "True", day = "Sunday")
        else:
            if request.form.get("wednesday"):
                db.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "False", day = "Wednesday")
            if request.form.get("sunday"):
                db.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "False", day = "Saturday")
            if request.form.get("saturday"):
                db.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "False", day = "Sunday")

        return render_template("success.html")

    else:
        return render_template("signups.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide a name", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        #Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 403)

        # Ensure confirmation matches password
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("confirmation and password do not match")

        db.execute("INSERT INTO users (username, password, name) VALUES( :username, :hash, :name)",
            username=request.form.get("username"),
            hash=generate_password_hash(request.form.get("password")),
            name=request.form.get("name"))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/signedup", methods=["GET"])
def signedup():
    if not ("user_id" in session.keys()):
        return redirect("/login")
    name = db.execute("SELECT name FROM users WHERE username = :username", username = session["user_id"])
    sdays = db.execute("SELECT day FROM Signup WHERE Name = :naame", naame = "Eric")
    days = []
    if len(sdays) == 0:
        return render_template("signedup.html", days = 0)
    for i in range(len(sdays)):
        days.append(sdays[i]["day"])
    return render_template("signedup.html", days = ", ".join(days))

@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not ("user_id" in session.keys()):
            return redirect("/login")
        # Check if they're signed up for the submitted day
        rows = db.execute("Select * FROM Signup WHERE Name == :naame", naame = "Eric")
        issignedup = False
        if request.form.get("wednesday"):
            for i in range(len(rows)):
                if rows[i]["day"] == "Wednesday":
                    issignedup = True
                    break
        if request.form.get("saturday"):
            for i in range(len(rows)):
                if rows[i]["day"] == "Saturday":
                    issignedup = True
                    break
        if request.form.get("sunday"):
            for i in range(len(rows)):
                if rows[i]["day"] == "Sunday":
                    issignedup = True
                    break
        if issignedup == False:
            return apology("Sorry, you are not signed up for those practices")
        # Remove row from database
        if request.form.get("wednesday"):
            db.execute("DELETE FROM Signup WHERE Name == :naame AND day == :day", naame = "Eric", day = "Wednesday")
        if request.form.get("saturday"):
            db.execute("DELETE FROM Signup WHERE Name == :naame AND day == :day", naame = "Eric", day = "Saturday")
        if request.form.get("sunday"):
            db.execute("DELETE FROM Signup WHERE Name == :naame and day == :day", naame = "Eric", day = "Sunday")
        return render_template("canceled.html")
    else:
        return render_template("cancel.html")

@app.route("/finalcancel", methods=["GET", "POST"])
def finalcancel():
    if request.method == "POST":
        if not request.form.get("side"):
            return apology("Please pick a side", 403)
            # Clear all practices for this user
            db.execute("DELETE FROM Signup WHERE Name == :naame", naame = "Eric")
            # Re-signup
            if not ("user_id" in session.keys()):
                return redirect("/login")
            if request.form.get("ride"):
                if request.form.get("wednesday"):
                    db.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( :name, :ride, :day, :side)", name = "Eric", ride = "True", day = "Wednesday", side = request.form.get("side"))
                if request.form.get("sunday"):
                    db.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( :name, :ride, :day, :side)", name = "Eric", ride = "True", day = "Saturday", side = request.form.get("side"))
                if request.form.get("saturday"):
                    db.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( :name, :ride, :day, :side)", name = "Eric", ride = "True", day = "Sunday", side = request.form.get("side"))

            else:
                if request.form.get("wednesday"):
                    db.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( :name, :ride, :day, :side)", name = "Eric", ride = "False", day = "Wednesday", side = request.form.get("side"))
                if request.form.get("sunday"):
                    db.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( :name, :ride, :day, :side)", name = "Eric", ride = "False", day = "Saturday", side = request.form.get("side"))
                if request.form.get("saturday"):
                    db.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( :name, :ride, :day, :side)", name = "Eric", ride = "False", day = "Sunday", side = request.form.get("side"))

            return render_template("success.html")
    else:
        day = db.execute("SELECT day FROM Signup WHERE Name = :name", name = "Eric")
        ride = db.execute("SELECT Ride FROM Signup WHERE Name = :name", name = "Eric")
        side = db.execute("SELECT side FROM Signup WHERE Name = :name", name = "Eric")
        rows = db.execute("SELECT day FROM Signup WHERE Name = :naame", naame = "Eric")
        wed = db.execute("SELECT * FROM Signup WHERE day = :day", day = "Wednesday")
        sat = db.execute("SELECT * FROM Signup WHERE day = :day", day = "Saturday")
        sun = db.execute("SELECT * FROM Signup WHERE day = :day", day = "Sunday")
        wedavailable = len(wed)
        satavailable = len(sat)
        sunavailable = len(sun)
        if len(rows) == 0:
            return render_template("finalcancel.html", a = "", b = "", c = "")
        else:
            if len(rows) == 1:
                if rows[0]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "", day = day, ride = ride, side = side, available = wedavailable)
                if rows[0]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "", day = day, ride = ride, side = side, available = satavailable)
                if rows[0]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "", b = "", c = "checked", day = day, ride = ride, side = side, available = sunavailable)
            if len(rows) == 2:
                if rows[0]["day"] == "Wednesday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [wedavailable, satavailable])
                if rows[0]["day"] == "Wednesday" and rows [1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [wedavailable, sunavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [satavailable, sunavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [satavailable, wedavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, wedavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, satavailable])
            if len(rows) == 3:
                if rows[0]["day"] == "Wednesday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [wedavailable, satavailable, sunavailable])
                if rows[0]["day"] == "Wednesday" and rows [1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [wedavailable, sunavailable, satavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [satavailable, sunavailable, wedavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [satavailable, wedavailable, sunavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, wedavailable, satavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, satavailable, wedavailable])

            return apology("Oops! Something Went Wrong", 403)