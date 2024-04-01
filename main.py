import requests
from bs4 import BeautifulSoup


def get_nutrients(row_index, dataframe):
    # Extract nutrient values for the specified row
    nutrient_values = dataframe.loc[
        row_index, ['allergens'] + list(dataframe.loc[row_index, 'energy-kcal_100g':].index)]
    return nutrient_values


negative_ingredients = ["saturated-fat_100g", "trans-fat_100g", "cholesterol_100g", "sugars_100g",
                        "-insoluble-fiber_100g", "salt_100g", "sodium_100g", "alcohol_100g", "caffeine_100g"]


def calculate_nutritional_score(values, max_calories, allergens):
    total_score = 0
    points = 0
    total_possible_score = 0
    total_calories = values.get("energy-kcal_100g", 0)
    allergen_ingredients = values.get("allergens")
    # Define recommended values for each nutrient (converted to grams for consistency)
    recommended_values = {
        "vitamin-a_100g": 0.0004,
        "vitamin-d_100g": 0.0000038,
        "vitamin-e_100g": 0.009,
        "vitamin-k_100g": 0.00000041,
        "vitamin-b1_100g": 0.00000056,
        "vitamin-b2_100g": 0.0000013,
        "vitamin-b6_100g": 0.0000004,
        "vitamin-b3_100g": 0.000004,
        "pantothenic-acid_100g": 0.000004,
        "vitamin-b12_100g": 0.000000009,
        "folates_100g": 0.000000068,
        "choline_100g": 0.425,
        "calcium_100g": 0.001,
        "phosphorus_100g": 0.00075,
        "magnesium_100g": 0.00015,
        "proteins_100g": 26,
        "fat_100g": 15,
        "sodium_100g": 0.0002,
        "potassium_100g": 0.001,
        "chloride_100g": 0.0003,
        "iron_100g": 0.0075,
        "copper_100g": 0.0015,
        "zinc_100g": 0.015,
        "manganese_100g": 0.0012,
        "selenium_100g": 0.00000009,
        "iodine_100g": 0.00000022,
        "fiber_100g": 11,
        "carbohydrates_100g": 125,
    }
    if allergen_ingredients in allergens:
        return "Food not suitable for pet!"
    # Calculate the caloric percentage
    if str(total_calories).replace('.', '', 1).isdigit():
        caloric_percentage = (float(total_calories) / max_calories) * 100 if max_calories > 0 else "N/A"
        print("Caloric Percentage:", caloric_percentage)

    # Nutrients present in the food
    present_nutrients = []
    total_volume = 0
    # Iterate through each nutrient
    for nutrient, value in values.items():
        if str(value).replace('.', '', 1).isdigit():
            if nutrient in recommended_values:
                # Calculate the percentage of recommended value
                percentage = (float(value) / float(recommended_values[nutrient])) * 100
                # Update the total_possible_score based on the percentage
                total_possible_score += percentage

                # Check for penalties if the value exceeds the recommended value
                if percentage > 100:
                    penalty_percentage = min(percentage - 100, 50)  # Maximum penalty of 50%
                    total_score -= penalty_percentage
                    points -= 0.5  # penalty for nutriscore

                # Update the total_score based on the percentage
                total_score += min(percentage, 100)  # Cap the score at 100%     
            total_volume += float(value)
            present_nutrients.append(nutrient)

    # Calculate the final score as a percentage of filled nutritional needs
    final_score = (total_score / total_possible_score) * 100 if total_possible_score > 0 else "Not enough information"

    if not present_nutrients:
        points = ""

    for nutrient, value in values.items():
        if str(value).replace('.', '', 1).isdigit():
            if nutrient in negative_ingredients:
                points -= round((float(value) / total_volume) * 10)
            else:
                points += round((float(value) / total_volume) * 10)

    print("Nutrients Present in the Food:", present_nutrients)
    nutriscore = ""

    if points != "":
        if points <= -6:
            nutriscore = "E"
        elif points <= -2:
            nutriscore = "D"
        elif points <= 2:
            nutriscore = "C"
        elif points <= 6:
            nutriscore = "B"
        elif points <= 10:
            nutriscore = "A"
    else:
        nutriscore = "Not enough information"

    return final_score, nutriscore


def scrape_article_info(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the article title
    title = soup.find('title').get_text()

    # Extract the article image URL (assuming it's in the <meta property="og:image"> tag)
    image_url = soup.find('meta', property='og:image')['content']

    return title, image_url
