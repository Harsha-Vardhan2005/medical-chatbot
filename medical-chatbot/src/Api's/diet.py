# food2.py
import requests

def get_food_suggestions(condition):

    api_key = 'X5XAiBR3DhTt4ALLcdJvUL6LAT3ukTylkCONNPRc'
    limit = 8  # Number of results to retrieve
    url = (
        f'https://api.nal.usda.gov/fdc/v1/foods/search?'
        f'api_key={api_key}&'
        f'query={condition}&'
        f'pageSize={limit}'
    )

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        food_suggestions = []
        for item in data.get('foods', []):
            food_name = item.get('description', 'N/A')
            nutrients = item.get('foodNutrients', [])
            
            # Format nutrient information as a bulleted list
            nutrient_info = "\n".join([
                f"  - {nutrient.get('nutrientName', 'N/A')}: {nutrient.get('value', 'N/A')} {nutrient.get('unitName', 'N/A')}"
                for nutrient in nutrients
            ])
            food_suggestions.append(f"**Food Name:** {food_name}\n**Nutrients:**\n{nutrient_info}")

        return "### Food suggestions for '{}'\n\n".format(condition) + "\n\n".join(food_suggestions)
    else:
        return "Failed to retrieve data from the USDA API."
