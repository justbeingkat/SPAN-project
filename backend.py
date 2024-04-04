from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from main import calculate_nutritional_score, scrape_article_info
from extensions import init_app, db
import pandas as pd
from flask_migrate import Migrate
from models import Profile
from werkzeug.security import check_password_hash
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'  # SQLite database file path
init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login view

with app.app_context():
    # Create the database tables before running the application
    db.create_all()


data = pd.read_csv("cleaned_data.csv", low_memory=False)
allergens = pd.read_csv("allergens.csv")
articles = [{'link': 'https://www.huffpost.com/entry/thanksgiving-food-dangerous-pets_l_6554e57fe4b0e476701266eb'},
            {'link': 'https://www.foxnews.com/lifestyle/pet-lovers-roundup-deals-useful-pet-supplies-accessories'},]


@login_manager.user_loader
def load_user(user_id):
    return Profile.query.get(int(user_id))


@app.route('/')
def home():
    for article in articles:
        title, image_url = scrape_article_info(article['link'])
        article['title'] = title
        article['image_url'] = image_url
    return render_template('home.html', articles=articles)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        # Retrieve the user from the database by username or email
        user = Profile.query.filter((Profile.username == username_or_email) | (Profile.email == username_or_email)).first()
        if user and check_password_hash(user.password, password):
            # Login successful
            flash("Successful Login!", "success")
            # Redirect to a different page after successful login
            return redirect(url_for('profile'))  # Redirect to the profile page
        else:
            # Invalid username or password
            flash("Invalid username or password. Please try again.", "error")
            return render_template('login.html')
    return render_template('login.html')


@app.route('/search')
def search():
    return render_template('search.html', food_options=data['product_name'].tolist())


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if the username already exists
        existing_profile = Profile.query.filter_by(username=username).first()
        if existing_profile:
            return render_template('create-profile.html', message='Username already exists')

        # Create a new profile
        new_profile = Profile(username=username, password=password, email=email)
        db.session.add(new_profile)
        db.session.commit()
        return render_template('create-profile.html', message='Profile created successfully!')

    return render_template('create-profile.html')


@app.route('/calculate-score', methods=['POST'])
def calculate_score():
    selected_food = request.form.get('food-dropdown')
    # Define relevant columns
    relevant_columns = ['allergens'] + list(data.loc[data['product_name'] == selected_food, "energy-kcal_100g":].columns)
    # Filter the DataFrame to include only the selected food and relevant columns
    filtered_data = data.loc[data['product_name'] == selected_food, relevant_columns]
    # Convert the filtered data to a dictionary
    nutrient_values = filtered_data.to_dict('records')[0]
    scores = calculate_nutritional_score(nutrient_values, 950, allergens)
    return jsonify({'score': scores[0], 'nutri score': scores[1]})


if __name__ == '__main__':
    app.run(debug=True)
