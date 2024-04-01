from flask import Flask, render_template, request, jsonify
from main import calculate_nutritional_score
import pandas as pd

app = Flask(__name__)

data = pd.read_csv("cleaned_data.csv", low_memory=False)
allergens = pd.read_csv("allergens.csv")

@app.route('/')
def index():
    return render_template('home.html', food_options=data['product_name'].tolist())


@app.route('/calculate-score', methods=['POST'])
def calculate_score():
    selected_food = request.form.get('food-dropdown')
    # Define relevant columns
    relevant_columns = ['allergens'] + list(data.loc[data['product_name'] == selected_food, 'energy-kcal_100g':].columns)
    filtered_data = data[data['product_name'] != 'Nope']
    # Filter the DataFrame to include only the selected food and relevant columns
    filtered_data = filtered_data.loc[filtered_data['product_name'] == selected_food, relevant_columns]
    # Convert the filtered data to a dictionary
    nutrient_values = filtered_data.to_dict('records')[0]
    scores = calculate_nutritional_score(nutrient_values, 950, allergens)
    return jsonify({'score': scores[0], 'nutri score': scores[1]})


if __name__ == '__main__':
    app.run(debug=True)
