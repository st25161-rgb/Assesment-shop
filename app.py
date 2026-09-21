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

def calculate_total(cart_pizza, cart_drink):
    total = sum(item['price'] * item['quantity'] for item in cart_pizza.values())
    total += sum(item['price'] * item[quantity] for item in cart_drink.values())
    
    return total

def initialise_database():
    with sqlite3.connect('order.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXIST orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            customer_name TEXT,
            pizza TEXT,
            drinks TEXT,
            total REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')


# the routes for the template files or fucntions to
@app.route("/base")
def base():
    return render_template("base.html")

@app.route('/')
def index():
    drinks = load_drink_data()
    pizzas = load_pizza_data()
    cart_pizza = session.get('cart_pizza', {})
    cart_drink = session.get('cart_drink', {})

    return render_template("index.html", 
                            drinks=drinks, 
                            pizzas=pizzas, 
                            cart_pizza=cart_pizza, 
                            cart_drink=cart_drink,
                            total = total,
                            cancel_order=cancel_order,
                            checkout = checkout
                            )
@app.route('/order')
def order():
    drinks = load_drink_data()
    pizzas = load_pizza_data()
    cart_pizza = session.get('cart_pizza', {})
    cart_drink = session.get('cart_drink', {})
    total = calculate_total(cart_pizza, cart_drink)

    cancel_order = session.get('cancel_order', False)
    checkout = session.get('checkout', False)

    return render_template("order.html",
                            drinks=drinks, 
                            pizzas=pizzas, 
                            cart_pizza=cart_pizza, 
                            total = total,
                            cart_drink=cart_drink,
                            cancel_order=cancel_order
                            )

@app.route('/about')
def about():
    return render_template("about.html")



@app.route('/invoice')
def invoice():
    return render_template("invoice.html")

@app.route('/order')
def order_display():
    with sqlite3.connect('order.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY date DESC')
        rows = cursor.fetchall()
        orders = []
        for row in rows:
            orders.append({
                'order_id': row[0],
                'invoice_number': row[1],
                'customer_name': row[2],
                'pizza': json.loads(row[3]),
                'drinks': json.loads(row[4]),
                'total': row[5],
                'date': row[7]
            })

        return render_template("order_display.html", orders=orders) 

@app.route('/checkout', methods=['POST'])
def checkout():
    customer_name = request.form['customer_name'].strip().title() #Makes sure the name is 'valid'

    if not customer_name:   #if the name isnt valid, tells user to enter a name and redierects back to order page
        flash("Customer name is required")
        return redirect(url_for("order"))
    
    cart_pizza = session.get('cart_pizza', {}) #takes items from the cart for pizza and tells route what they are
    cart_drink = session.get("cart_drinks", {}) #takes items from cart for dirnka and tells route what they are

    if not cart_pizza or cart_drink: #prevents empty cart errors
        flash("your cart is empty")
        return redirect(url_for('order'))

    total = calculate_total(cart_pizza, cart_drink)

    invoice_date = datetime.datetime.now().strftime('%Y-%M-%d %H-%M-%S') #invoice date
    invoice_number = f"INV_{customer_name.replace('  ', '_')}_{invoice_date}"

    with sqlite3.connect('order.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (invoice_number, customer_name, pizza, drinks, total)
            VALUES (?, ?, ?, ?, ?)
        ''', (invoice_number, customer_name, json.dumps(cart_pizza), json.dumps(cart_drink), total))
        conn.commit()
    
    invoice_filename = f"{invoice_number}.txt" #makes the invoice number into a string

    try:    #opens invoice as a file
        with open(invoice_filename, 'w') as f:
            f.write(f"Invoice Number : {invoice_number}\n")
            f.write(f"Customer Name: {customer_name}\n")
            f.write(f"Invoice date: {invoice_date}\n")
            f.write(f"\nPizzas:\n")
            for pizza, details in cart_pizza.item():
                f.write(f" {item}: {details['quantity']} x ${details['price']:.2f} = ${details['quantity'] * details['price']:.2f}\n  ") 
            f.write(f"\nDrinks:\n")           
            for drinks, details in cart_drink.item():
                f.write(f" {item}: {details['quantity']} x ${details['price']:.2f} = ${details['quantity'] * details['price']:.2f}\n ") 
            
            f.write(f"\nTotal: ${total:.2f}\n")
    except Exception as e:
        flash(f"Error whilst saving invoice: {e}") #prevents crash if the invoice fails
    
    session.pop('cart_pizza', None)
    session.pop('cart_drink', None)
    session.modified = True
    flash(f"Your cart has been emptied, The order is now being made")
    
    return redirect (url_for('invoice'),
                            cart_drink = cart_drink,
                            cart_pizza = cart_pizza,
                            total = total,
                            customer_name = customer_name,
                            invoice_date = invoice_date
                            )



@app.route('/remove_from_cart/<item>')
def remove_from_cart(item):
    cart_drink = session.get('cart_drink', {})
    cart_pizza = session.get('cart_pizza', {})
    
    if item in cart_drink:
        cart_drink.pop(item, None) #pop removes the 'item' in dictionary cart_drink
        session['cart_drink'] = cart_drink
        session.modified = True #updates session
        flash(f"all {{items}}('s) have been taken out of your cart.")
        
    
    elif item in cart_pizza:
        cart_pizza.pop(item, None) #pop removes the 'item' in dictionary cart_drink
        session['cart_pizza'] = cart_pizza
        session.modified = True #updates session
        flash(f"all {{items}}('s) have been taken out of your cart.")
    
    else:
        flash(f"The {{item}}('s) could not be found in your cart.")

         
    return redirect(url_for('order.html'))

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session.pop('cart_pizza', None)
    session.pop('cart_drink', None)
    session.modified = True
    flash(f"Cart has been emptied")

    return redirect(url_for('order.html'))

@app.route('/add_to_cart_drinks', methods=["POST"])
def add_to_cart_drink():
    drink_info  = request.form.get('drink_id') #gets the information on drink name, size and price
    quantity = int(request.form.get('quantity', 1)) #gets quantity of drinks from form (min is 1)

    cart_drink = session.get('cart_drink', {}) #gets the information from the form for drinks

    if drink_info:
        name, size, price = drink_info.split('_', 2)
        item_key = f"{name} ({size})"

        if item_key in cart_drink: #if the drink is already in cart, it adds on the quantity in cart
            cart_drink[item_key]['quantity'] += quantity
        else: #if drink is not in cart, then it will add it into the cart dictionary and make the price a number not string
            cart_drink[item_key] = {
                'price': float(price),
                'quantity': quantity   
            }


        session['cart_drink'] = cart_drink #updates session
        session.modified = True #flask will save it
        flash(f"{quantity} {item_key}(s) added to cart") #message sent to end user upon action
    return redirect(url_for('order'))
    
    
@app.route('/add_to_cart_pizza', methods=["POST"])
def add_to_cart_pizza():
    pizza_info = request.form.get('pizza_id') #gets the pizza name size and price (in that order)
    quantity = int(request.form.get('quantity', 1)) # makes the quantity a number

    cart_pizza = session.get('cart_pizza', {}) #creates a cart/dictionary for pizza or adds info to it

    if pizza_info:
        parts = pizza_info.split('_',2)
        if len(parts) == 3:
            name, size, price = parts   
            item_key =  f"{name} ({price})"

            if item_key in cart_pizza:
                cart_pizza[item_key]['quantity'] += quantity #adds to the quantity of item in cart if there is already the item key there
            else: #if the item is not there, it will make one there which holds all these variables
                cart_pizza[item_key] = {'name': name, 
                                        'size': size, 
                                        'price': float(price),  #float makes price a decimal instead of string, does math properly
                                        'quantity': quantity}

            session['cart_pizza'] = cart_pizza #updates session
            session.modified = True #flask will save it
            flash(f"{quantity} {item_key}(s) added to cart") #message sent to end user upon action
            return redirect(url_for('order')) #refreshes homepage

@app.route('/cancel_saved_order/<int:order_id>', methods=['POST'])
def cancel_saved_order(order_id):
    with sqlite3.connect('flower_shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
        conn.commit()
    
    flash(f"Order {order_id} has been cancelled.")
    return redirect(url_for('order_history'))


if __name__ == '__main__':
    # initialise_database()
    app.run(debug=True)
