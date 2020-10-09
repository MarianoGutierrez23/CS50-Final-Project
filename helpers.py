import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup_name(name):
    """Look up meal by name."""

    # Contact API (API_KEY=1)
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={urllib.parse.quote_plus(name)}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        i = 0
        return {
                "name": quote['meals'][i]['strMeal'],
                "category": quote['meals'][i]['strCategory'],
                "ingredients": [quote['meals'][i]['strIngredient1'], quote['meals'][i]['strIngredient2'],quote['meals'][i]['strIngredient3'],
                            quote['meals'][i]['strIngredient4'], quote['meals'][i]['strIngredient5'], quote['meals'][i]['strIngredient6'],
                            quote['meals'][i]['strIngredient7'],quote['meals'][i]['strIngredient8'], quote['meals'][i]['strIngredient9'],
                            quote['meals'][i]['strIngredient10'],quote['meals'][i]['strIngredient11'],quote['meals'][i]['strIngredient12'],
                            quote['meals'][i]['strIngredient13'],quote['meals'][i]['strIngredient14'],quote['meals'][i]['strIngredient15'],
                            quote['meals'][i]['strIngredient16'],quote['meals'][i]['strIngredient17'],quote['meals'][i]['strIngredient18'],
                            quote['meals'][i]['strIngredient19'],quote['meals'][i]['strIngredient20']],
                "instructions": quote['meals'][i]['strInstructions'],
                "img": quote['meals'][i]['strMealThumb'],
                "video": quote['meals'][i]['strYoutube']
            }
    except (KeyError, TypeError, ValueError):
        return None

def lookup_key(key_word):
    # Idem 'lookup_name" but the idea is that the user does not know the specific name of the meal so he or she looks for a key word

    # Contact API (API_KEY=1)
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={urllib.parse.quote_plus(key_word)}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        meals = []
        for i in range(len(quote['meals'])):
            meals.append({
                "name": quote['meals'][i]['strMeal'],
                "category": quote['meals'][i]['strCategory'],
                "img": quote['meals'][i]['strMealThumb'],
            })
        return meals
    except (KeyError, TypeError, ValueError):
        return None    

def lookup_cat(category):
    # Let user to look up recepies by category 

     # Contact API (API_KEY=1)
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"http://www.themealdb.com/api/json/v1/{api_key}/filter.php?c={urllib.parse.quote_plus(category)}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        meals = []
        for i in range(len(quote['meals'])):
            meals.append({
                "name": quote['meals'][i]['strMeal'],
                "img": quote['meals'][i]['strMealThumb']
            })
        return meals
    except (KeyError, TypeError, ValueError):
        return None    

def lookup_random():
    # Look up for a random meal to show at index
     # Contact API (API_KEY=1)
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://www.themealdb.com/api/json/v1/{api_key}/random.php")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
       
       # Return this dict
        return {
            "name": quote['meals'][0]['strMeal'],
            "category": quote['meals'][0]['strCategory'],
            "img": quote['meals'][0]['strMealThumb']
        } 

    except (KeyError, TypeError, ValueError):
        return None    
       

