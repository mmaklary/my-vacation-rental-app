from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import database

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = '17717'

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

# Route to display the main page
@app.route('/')
def index():
    listed_properties = database.get_listed_properties()
    print(listed_properties)  # Add this debug print
    return render_template('index.html', listed_properties=listed_properties)


# Route to display property details
@app.route('/property/<int:property_id>')
def property_details(property_id):
    # Find the property by ID in the database or data source
    property = database.get_property_by_id(property_id)

    if property:
        return render_template('property_details.html', property=property)
    else:
        return "Property not found."  # You can handle the case where the property is not found

# Route for viewing all listed properties
@app.route('/listings')
def listings():
    listed_properties = database.get_all_properties()
    print(listed_properties)  # Add this debug print to check the retrieved properties
    return render_template('listings.html', listed_properties=listed_properties)


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Register user using the database module
        if database.register_user(username, password):
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

        print(f"Username: {username}, Password: {password}")  # Add this debug print

        # Verify user login using the database module
        if database.verify_login(username, password):
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

# Route for user logout
@app.route('/logout')
@login_required  # Use the login_required decorator to protect this route
def logout():
    # Use Flask-Login's logout_user function to clear the user session
    logout_user()
    # Redirect to the login page after logout
    return redirect(url_for('login'))

# Route for user dashboard
@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in (you can use the session['username'] variable)
    logged_in = 'username' in session

    # Display personalized user dashboard
    return render_template('dashboard.html', username=session.get('username'), logged_in=logged_in)

    
# Route for search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get form data
        location = request.form['location']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        # Perform the search query based on the form data
        # For example, you can search for properties in the specified location and within the check-in and check-out dates
        # You can use the 'location', 'checkin', and 'checkout' variables to filter the properties

        # For demonstration purposes, let's assume we have a dummy list of properties as search results
        # Replace this with your actual search query logic using your database
        search_results = [
            {
                'title': 'Property 1',
                'location': 'Location A',
                'price': 100,
                'accommodates': 4
            },
            {
                'title': 'Property 2',
                'location': 'Location B',
                'price': 150,
                'accommodates': 2
            },
            # Add more properties here based on your search query results
        ]

        # Pass the search results to the search.html template for display
        return render_template('search.html', search_results=search_results)

    # If it's a GET request, simply render the search.html template with the search form
    return render_template('search.html')

# Route for adding a new property
@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    # Check if the user is logged in (you can use the session['username'] variable)
    if 'username' not in session:
        # If the user is not logged in, redirect to the login page
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        price = float(request.form['price'])
        property_type = request.form['property_type']
        accommodates = int(request.form['accommodates'])
        bedrooms = int(request.form['bedrooms'])
        bathrooms = int(request.form['bathrooms'])
        amenities = request.form['amenities']
        

        # Insert the new property into the database using the database module
        database.insert_property(title, description, location, price, property_type, accommodates, bedrooms, bathrooms, amenities)

        # Redirect to the listings page after successful addition
        return redirect(url_for('listings'))

    # Display the form to add a new property
    return render_template('add_property.html')

# Route for viewing all listed properties
@app.route('/listings')
def listings():
    listed_properties = database.get_all_properties()
    return render_template('listings.html', listed_properties=listed_properties)

if __name__ == '__main__':
    # Create the 'properties' table if it doesn't exist
    database.create_properties_table()

    app.run(debug=True)
