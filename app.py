import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup_cat, lookup_key, lookup_name, lookup_random
import datetime

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
db = SQL("sqlite:///cuisine.db")

# Make sure API key is set
# On Windows use " set API_KEY=value "
# On Linux use "export" instead of "set"

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set. Try 'set API_KEY=1'")

#
@app.route("/")
@login_required
def index():

    # First look up three random recipes
    meal1 = lookup_random()
    meal2 = lookup_random()
    meal3 = lookup_random()
    
    # Then add them into a list
    # So random_selection will be a list of dicts
    random_selection = [
        meal1,
        meal2,
        meal3
    ]

    return render_template("index.html", selection = random_selection)    


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to index
        return redirect("/")

    # Via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        category = request.form.get("category")
        name = request.form.get("name")
        key_word = request.form.get("key_word")

        # Check if no field is filled
        if not category and not name and not key_word:
            return apology("Provide something to look up for", 403)

        # Check that only one field is filled
        if category and key_word:
            return apology("Search by category, by name or by any key word", 403)
                 
        # Search by category
        if category:
            meals = lookup_cat(category)

            # meals is a list of dicts
            return render_template("quoted_category.html", meals = meals, category=category)

        # When clicking on the meal image
        if name:
            meal = lookup_name(name)
            ingredients_raw = meal['ingredients']
            ingredients_cleaned = []
            for ingredient in ingredients_raw:
                if ingredient != "":
                    ingredients_cleaned.append(ingredient)

            # meal is a dict
            return render_template("quoted_name.html", meal = meal, ingredients = ingredients_cleaned)

        # Search by key word
        if key_word:
            meals_by_key = lookup_key(key_word)

            # meals_by_key is a list of dicts
            return render_template("quoted_key_word.html", meals = meals_by_key, key_word=key_word)          
        


@app.route("/favorites", methods=["GET","POST"])
@login_required
def favorites():
    if request.method == "POST":
        name = request.form.get("fav_meal")
        category = request.form.get("fav_category")
        img = request.form.get("fav_img")

        db.execute("CREATE TABLE IF NOT EXISTS 'favorites' ('user_id' INTEGER NOT NULL, 'name' TEXT NOT NULL, 'category' TEXT NOT NULL, 'img' TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")

        # Here query all the info as in /search to redirect to the same page (quoted_name.html) after clicking the button 'Add to favorites!'           

        meal = lookup_name(name)
        ingredients_raw = meal['ingredients']
        ingredients_cleaned = []
        for ingredient in ingredients_raw:
            if ingredient != "":
                ingredients_cleaned.append(ingredient)

        # If the meal is already in 'Favorites'
        rows = db.execute("SELECT name FROM favorites")
        for row in rows:
            if row['name'] == name:
                flash("Already in Favorites!")
                return render_template("quoted_name.html", meal=meal, ingredients=ingredients_cleaned)

        # And if not, add it
        db.execute("INSERT INTO favorites (user_id, name, category, img) VALUES(:user_id, :name, :category, :img)", 
                    user_id=session["user_id"], name=name, category=category, img=img)         
        
        # Alert!
        flash('Succesfully added!')
        # Render agaig the quoted page. Refresh 
        return render_template("quoted_name.html", meal=meal, ingredients=ingredients_cleaned)

    # Via GET
    else:
        fav = db.execute("SELECT name, category, img FROM favorites WHERE user_id = :user_id", user_id=session["user_id"])

        # Creat a list of dicts 
        favorites = []
        for row in fav:
            favorites.append({
                "meal": row["name"],
                "category": row["category"],
                "img": row["img"]
            })

        return render_template("favorites.html", favorites = favorites)        


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    # Get name by clicking 'Remove' button
    name = request.form.get("name")

    # Delete info from database
    db.execute("DELETE FROM favorites WHERE name = :name", name=name)
    
    return redirect("/favorites")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Get info from the form and check if some field is empty
        name = request.form.get("username")
        if not name:
            return apology("You must provide an username")

        password = request.form.get("password")
        if not password:
            return apology("Missing password")

        confirmation = request.form.get("confirmation")
        if confirmation != password:
            return apology("Passwords don't match")

        db.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL)")
        
        # Insert new user
        key = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username = name,
                        hash = generate_password_hash(password))
        if key == None:
            return apology("Username already exists")

        # Set user's session
        session["user_id"] = key
        
        return redirect("/")    

          

# I decided to implement the ability to change the user's passwrod
# First I set the button on the layout.html file
@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "GET":
        return render_template("changepass.html")
    else:
        # Get currente password
        rows = db.execute("SELECT hash FROM users WHERE id = :id", id = session["user_id"])
        pass_hashed = rows[0]["hash"]

        # Check if current passwords match
        curr_pass = request.form.get("current_password")
        if not check_password_hash(pass_hashed,curr_pass):
            return apology("Wrong password")

        new = request.form.get("new_password")
        confirmation_new = request.form.get("confirmation")
        if new != confirmation_new:
            return apology("New passwords don't match")

        # Change password by updating 'users'    

        db.execute("UPDATE users SET hash = :hash WHERE id = :id", id = session["user_id"], hash = generate_password_hash(new))

        # Force user to log in again
        session.clear()
        return redirect("/")            

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
