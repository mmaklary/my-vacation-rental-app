import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

# File path to store registered clients
CLIENTS_FILE = 'clients.json'

def load_clients():
    try:
        with open(CLIENTS_FILE, 'r') as f:
            clients = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        clients = []
    return clients

def save_clients(clients):
    with open(CLIENTS_FILE, 'w') as f:
        json.dump(clients, f)

def register_user(username, password):
    # Load existing clients from file
    clients = load_clients()

    # Check if the username is already taken
    for client in clients:
        if client["username"] == username:
            return False  # Username already exists, registration failed

    # Add the new user to the list of clients
    clients.append({"username": username, "password": password})

    # Save the updated clients list to the file
    save_clients(clients)

    print(f"Registered user: {username}")  # Add this debug print

    return True  # Registration successful


def connect_database():
    # Connect to the SQLite database or create it if it doesn't exist
    conn = sqlite3.connect('vacation_rental.db')

    # Create 'properties' table if it doesn't exist
    c = conn.cursor()
    c.execute('''PRAGMA foreign_keys = ON''')
    c.execute('''CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                price REAL NOT NULL,
                property_type TEXT NOT NULL,
                accommodates INTEGER NOT NULL,
                bedrooms INTEGER NOT NULL,
                bathrooms REAL NOT NULL,
                amenities TEXT NOT NULL
                )''')

    # Create 'clients' table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
                )''')

    conn.commit()
    return conn

def verify_login(username, password):
    # Connect to the SQLite database
    conn = connect_database()
    c = conn.cursor()

    # Check if the username and password match a registered user
    c.execute('SELECT * FROM clients WHERE username = ? AND password = ?', (username, password))
    user_data = c.fetchone()

    print(f"User data: {user_data}")  # Add this debug print

    conn.close()

    return user_data is not None  # Return True if the user is registered, False otherwise

def create_properties_table():
    # Create the 'properties' table in the database if it doesn't exist
    conn = connect_database()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def insert_property(title, description, location, price, property_type, accommodates, bedrooms, bathrooms, amenities):
    # Insert a new property into the 'properties' table
    conn = connect_database()
    c = conn.cursor()
    c.execute('INSERT INTO properties (title, description, location, price, property_type, accommodates, bedrooms, bathrooms, amenities) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (title, description, location, price, property_type, accommodates, bedrooms, bathrooms, amenities))
    conn.commit()
    conn.close()

def get_all_properties():
    # Get all properties from the 'properties' table
    conn = connect_database()
    c = conn.cursor()
    c.execute('SELECT * FROM properties')
    properties = c.fetchall()
    conn.close()
    return properties

def get_property_by_id(property_id):
    # Get a property by its ID from the 'properties' table
    conn = connect_database()
    c = conn.cursor()
    c.execute('SELECT * FROM properties WHERE id = ?', (property_id,))
    property_data = c.fetchone()
    conn.close()
    if property_data:
        return {"id": property_data[0], "title": property_data[1], "description": property_data[2]}
    else:
        return None

def get_listed_properties():
    conn = connect_database()
    c = conn.cursor()
    c.execute('SELECT * FROM properties')
    properties = c.fetchall()
    conn.close()

    # Convert the list of tuples to a list of dictionaries
    property_list = []
    for property_data in properties:
        property_dict = {
            'id': property_data[0],
            'title': property_data[1],
            'description': property_data[2],
            'location': property_data[3],
            'price': property_data[4],
            'property_type': property_data[5],
            'accommodates': property_data[6],
            'bedrooms': property_data[7],
            'bathrooms': property_data[8],
            'amenities': property_data[9]
        }
        property_list.append(property_dict)

    return property_list

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize the LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Your user model class (implement UserMixin for some useful methods)
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Your user loader function (replace this with actual user loading from the database)
@login_manager.user_loader
def load_user(user_id):
    # For example, fetch the user from the database using the user_id
    # Return a User object if the user exists, or None if not found
    return User(user_id)

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Register user using the database module
        if register_user(username, password):
            # Redirect to login page after successful registration
            return redirect(url_for('login'))

    # Display the registration page
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Verify user login using the database module
        if verify_login(username, password):
            # Assuming you have verified the username and password, create a User object
            user = User(username)

            # Use Flask-Login's login_user function to set up the user session
            login_user(user)

            # Redirect to the user dashboard after successful login
            return redirect(url_for('dashboard'))
        else:
            # If login fails, display an error message on the login page
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)

    # Display the login page
    return render_template('login.html')

# Route for user dashboard
@app.route('/dashboard')
@login_required  # Use the login_required decorator to protect this route
def dashboard():
    # Check if the user is logged in (you can use the session['username'] variable)
    logged_in = 'username' in session

    # Display personalized user dashboard
    return render_template('dashboard.html', username=session.get('username'), logged_in=logged_in)

# Route for user logout
@app.route('/logout')
@login_required  # Use the login_required decorator to protect this route
def logout():
    # Use Flask-Login's logout_user function to clear the user session
    logout_user()
    # Redirect to the login page after logout
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create the 'properties' table if it doesn't exist
    create_properties_table()

    app.run(debug=True)
