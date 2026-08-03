import datetime
import json
import sqlite3

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'Thereisnotamanhere'

def load_deltarune_data():
    try: 
        with open('data/Deltarune.json') as file:
            deltarune = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading deltarune records data: {e}")
        deltarune = {}
    
    return deltarune

def load_jpop_data():
    try: 
        with open('data/Jpop.json') as file:
            jpop = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading jpop records data: {e}")
        jpop = {}
    
    return jpop


def load_rock_data():
    try: 
        with open('data/Rock.json') as file:
            rock = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading rock records data: {e}")
        rock = {}
    
    return rock


def load_metal_data():
    try: 
        with open('data/Metal.json') as file:
            metal = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading metal records data: {e}")
        metal = {}
    
    return metal

@app.route('/')
def index():
    deltarune = load_deltarune_data
    jpop = load_jpop_data
    metal = load_metal_data
    rock = load_rock_data
    
    return render_template("index.html",
                            deltarune=deltarune,
                            jpop=jpop,
                            metal=metal,
                            rock=rock
                            )    




if __name__ == '__main__':
    # initialise_database()
    app.run(debug=True)