import datetime
import json
import sqlite3

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'Thereisnotamanhere'

def load_drinks_data():
    try: 
        with open('data/drinks.json') as file:
            drinks = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading drinks data: {e}")
        drinks = {}
    
    return drinks

def load_pizza_data():
    try: 
        with open('data/pizza.json') as file:
            pizza = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pizza data: {e}")
        pizza = {}
    
    return pizza
@app.route("/base")
def base():
    return render_template("base.html")

@app.route('/')
def index():
    drinks = load_drinks_data()
    pizza = load_pizza_data()
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/order')
def order():
    drinks = load_drinks_data()
    pizza = load_pizza_data()
    return render_template("order.html", drinks=drinks, pizza=pizza)

@app.route('/invoice')
def invoice():
    return render_template("invoice.html")

@app.route('/your_cart')
def your_cart():
    return render_template("your_cart.html")


if __name__ == '__main__':
    # initialise_database()
    app.run(debug=True)
