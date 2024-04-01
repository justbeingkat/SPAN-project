from flask import Flask, render_template, request, jsonify
from main import calculate_nutritional_score, scrape_article_info
import pandas as pd

app = Flask(__name__)

data = pd.read_csv("cleaned_data.csv", low_memory=False)
allergens = pd.read_csv("allergens.csv")
articles = [{'link': 'https://www.huffpost.com/entry/thanksgiving-food-dangerous-pets_l_6554e57fe4b0e476701266eb'},
            {'link': 'https://www.foxnews.com/lifestyle/pet-lovers-roundup-deals-useful-pet-supplies-accessories'},]


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


@app.route('/search')
def search():
    return render_template('search.html', food_options=data['product_name'].tolist())


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        # Handle form submission to create the profile
        # You can access form data using request.form
        username = request.form['username']
        password = request.form['password']
        # Process the form data and create the profile

        # For now, let's just return a success message
        return jsonify({'message': 'Profile created successfully'})

    # If it's a GET request, render the template for creating a profile
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
