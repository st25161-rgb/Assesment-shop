import datetime
import json
import sqlite3


from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'Thereisnotamanhere'
#defining the functions for data files

def load_drink_data():
    try: 
        with open('Data/drink.json') as file:
            drinks = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading drink data: {e}")
        drinks = {}
    
    return drinks

def load_pizza_data():
    try: 
        with open('Data/pizza.json') as file:
            pizzas = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pizza data: {e}")
        pizzas = []
    
    return pizzas

# the routes for the template files or fucntions to
@app.route("/base")
def base():
    return render_template("base.html")

@app.route('/')
def index():
    drinks = load_drink_data()
    pizzas = load_pizza_data()
    return render_template("index.html", drinks=drinks, pizzas=pizzas)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/order')
def order():
    drinks = load_drink_data()
    pizzas = load_pizza_data()
    return render_template("order.html", drinks=drinks, pizzas=pizzas)

@app.route('/invoice')
def invoice():
    return render_template("invoice.html")

@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    drink = request.form['drink_id']
    quantity = int(request.form['quantity']) # makes the quantity a number
    drinks =load_drink_data()
    pizza = request.form['pizza_id']
    quantity = int(request.form['quantity']) # makes the quantity a number
    pizzas =load_pizza_data()
    cart = session.get('cart', {})

    if drink not in drinks:
            flash("invalid drink selected")
            return redirect(url_for('index'))
    
    if drink in cart:
        cart[drink]['quantity'] += quantity    
    
    
    if pizza not in pizzas:
            flash("invalid Pizza selected")
            return redirect(url_for('index'))
    
    if pizza in cart:
        cart[pizza]['quantity'] += quantity
    else:
        cart[pizza] = {
        'price': pizzas[pizza]['price'],
        'quantity': quantity
        }
    
    session['cart'] = cart #updates session
    session.modified = True #flask will save it
    flash(f"{quantity} {Pizza}(s) added to cart") #message sent to end user upon action
    return redirect(url_for('index')) #refreshes homepage











if __name__ == '__main__':
    # initialise_database()
    app.run(debug=True)
