# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
import requests
import json
from firebase_admin import initialize_app

initialize_app()

@https_fn.on_request()
def get_food_details(request: https_fn.Request) -> https_fn.Response:
    fdcId = request.args.get('fdcId', '')  # Retrieve the fdcId from the query parameters
    api_key = 'KnbgdtX65ISaS5jKyDefHDsbrfiVOUKULfHgZMS0'
    details_url = f'https://api.nal.usda.gov/fdc/v1/food/{fdcId}?api_key={api_key}'
    
    details_response = requests.get(details_url)
    if details_response.status_code == 200:
        details_data = details_response.json()
        
        # Extract specific fields from the response
        extracted_data = {
            'publicationDate': details_data.get('publicationDate'),
            'foodNutrients': details_data.get('foodNutrients', []),
            'brandOwner': details_data.get('brandOwner'),
            'brandName': details_data.get('brandName'),
            'brandedFoodCategory': details_data.get('brandedFoodCategory'),
            'householdServingFullText': details_data.get('householdServingFullText'),
            'ingredients': details_data.get('ingredients'),
            'packageWeight': details_data.get('packageWeight'),
            'notaSignificantSourceOf': details_data.get('notaSignificantSourceOf'),
            'labelNutrients': details_data.get('labelNutrients', []),
        }
        return https_fn.Response(json.dumps(extracted_data), status=200, headers={'Content-Type': 'application/json'})
    else:
        return https_fn.Response('Failed to retrieve food details', status=details_response.status_code)



@https_fn.on_request()
def search_food(request: https_fn.Request) -> https_fn.Response:
    query = request.args.get('query', '')
    api_key = 'KnbgdtX65ISaS5jKyDefHDsbrfiVOUKULfHgZMS0'
    search_url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}&pageSize=30'
    
    search_response = requests.get(search_url)
    if search_response.status_code == 200:
        search_data = search_response.json()
        formatted_results = [
            {
                'brandName': item.get('brandOwner'),
                'description': item.get('description', 'No description available'),
                'brandOwner': item.get('brandOwner'),
                'fdcId': item.get('fdcId'),  # Include the fdcId in the response
                'gtinUpc': item.get('gtinUpc', 'No UPC available')  # Include the gtinUpc in the response
            }
            for item in search_data.get('foods', [])
            if item.get('brandOwner') and item.get('brandOwner') != 'Unknown Brand'  # Filter out unknown brands and owners
        ][:30]  # Ensure only up to 30 items are included even if more are fetched
        return https_fn.Response(json.dumps(formatted_results), status=200, headers={'Content-Type': 'application/json'})
    else:
        return https_fn.Response('Failed to retrieve data', status=500)
    






@https_fn.on_request()
def generate_analysis(request: https_fn.Request) -> https_fn.Response:
    fdcId = request.args.get('fdcId')  # Retrieve the fdcId from the query parameters
    if not fdcId:
        return https_fn.Response('No fdcId provided', status=400)

    # Fetch food details from your custom endpoint
    food_details = fetch_food_details(fdcId)
    if not food_details:
        return https_fn.Response('Failed to fetch food details', status=500)

    # Generate content based on the food details fetched
    return process_food_analysis(food_details)

def fetch_food_details(fdcId):
    details_url = f'https://get-food-details-mfckn4ttpa-uc.a.run.app/?fdcId={fdcId}'
    
    response = requests.get(details_url)
    if response.status_code == 200:
        return response.json()  # Return the parsed JSON response
    else:
        return None

def process_food_analysis(food_details):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=AIzaSyDEcqPIsunXJGt7AqT_-7uumdVDoovGZbs"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                    "text": "You are acting as a health advisor analyzing a food product. Analyze the provided information and generate a response formatted as a single, long string. Use '\'':'\'' to separate keys from their corresponding values, and use a semi-colon to separate multiple values under the same key. Ensure all keys are separated by a comma in the response. Avoid using special characters like asterisks or the phrase \"JSON literal.\" Format the output with the following structure:Brand: [Brand Name]Ingredients: [List of Ingredients separated by semi-colons]Potential Allergens: [List potential allergens, or '\''None'\'' if not apparent from the ingredients]Positive: [Highlight potential benefits]Negatives: [Highlight potential drawbacks or concerns]Considerations: [Additional factors to keep in mind]Disclaimers: [Include any necessary disclaimers regarding individual health or dietary restrictions]Vegan: [Yes/No]Vegetarian: [Yes/No]Gluten-Free: [Yes/No - Or indicate if it cannot be determined from the provided ingredients]Keto: [Yes/No]Diabetic: [Suitable, Suitable with moderation, Not suitable - Explain briefly]Paragraph1: [Provide a concise summary of the product'\''s suitability for weight management and sugar control, alongside any notable benefits]Paragraph2: [Address potential health concerns, long-term effects of ingredients, and suggest healthier alternatives where relevant]. Example Output: Brand:Coca-cola,Ingredients:Fish;Salmon;Tuna,Potential Allergens:None,Positive:Has Health Benefits,Negatives:Too Much Sugar,Considerations:Regulates health,Disclaimers:Need to consult doctor,Vegan:Yes,Vegetarian:Yes,Gluten-Free:No,Keto:Yes,Diabetic:Suitable,Paragraph1:Detailed explanation of benefits,Paragraph2:Discussion of potential risks and alternatives"
                    },
                    {
                    "text": "input:{\"publicationDate\": \"6/29/2023\",\"foodNutrients\": [{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1093,\"number\": \"307\",\"name\": \"Sodium, Na\",\"rank\": 5800,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150999,\"amount\": 11},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1004,\"number\": \"204\",\"name\": \"Total lipid (fat)\",\"rank\": 800,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150995,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 2000,\"number\": \"269\",\"name\": \"Total Sugars\",\"rank\": 1510,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150998,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1003,\"number\": \"203\",\"name\": \"Protein\",\"rank\": 600,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150994,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1008,\"number\": \"208\",\"name\": \"Energy\",\"rank\": 300,\"unitName\": \"kcal\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150997,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1005,\"number\": \"205\",\"name\": \"Carbohydrate, by difference\",\"rank\": 1110,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150996,\"amount\": 0}],\"brandOwner\": \"Coca-Cola USA Operations\",\"brandName\": \"DIET COKE\",\"brandedFoodCategory\": \"Soda\",\"householdServingFullText\": \"1 Can\",\"ingredients\": \"CARBONATED WATER, CARAMEL COLOR, ASPARTAME, PHOSPHORIC ACID, POTASSIUM C BENZOATE (TO PROTECT TASTE), NATURAL FLAVORS, CITRIC ACID, CAFFEINE\",\"packageWeight\": \"30 fl oz/888 mL\",\"notaSignificantSourceOf\": \"Not a significant source of saturated fat,trans fat, cholesterol, dietary fiber,vitamin D, calcium, iron and potassium.\",\"labelNutrients\": {6 items}} {\"publicationDate\": \"6/29/2023\",\"foodNutrients\": [{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 2000,\"number\": \"269\",\"name\": \"Total Sugars\",\"rank\": 1510,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151004,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1003,\"number\": \"203\",\"name\": \"Protein\",\"rank\": 600,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151000,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1005,\"number\": \"205\",\"name\": \"Carbohydrate, by difference\",\"rank\": 1110,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151002,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1093,\"number\": \"307\",\"name\": \"Sodium, Na\",\"rank\": 5800,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151005,\"amount\": 11},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1004,\"number\": \"204\",\"name\": \"Total lipid (fat)\",\"rank\": 800,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151001,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1008,\"number\": \"208\",\"name\": \"Energy\",\"rank\": 300,\"unitName\": \"kcal\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151003,\"amount\": 0}],\"brandOwner\": \"Coca-Cola USA Operations\",\"brandName\": \"SPRITE\",\"brandedFoodCategory\": \"Soda\",\"householdServingFullText\": \"1 Can\",\"ingredients\": \"CARBONATED WATER, LESS THAN 2% OF: CITRIC ACID, POTASSIUM CITRATE, NATURAL FLAVORS, POTASSIUM BENZOATE (TO PROTECT TASTE), ASPARTAME, ACESULFAME POTASSIUM.\",\"packageWeight\": \"30 fl oz/888 mL\",\"notaSignificantSourceOf\": \"Not a significant source of saturated fat.trans fat, cholesterol, dietary fiber,vitamin D, calcium, iron and potassium.\",\"labelNutrients\": {\"fat\": {\"value\": 0},\"sodium\": {\"value\": 24.4},\"carbohydrates\": {\"value\": 0},\"sugars\": {\"value\": 0},\"protein\": {\"value\": 0},\"calories\": {\"value\": 0}}"
                    },
                    {
                    "text": "output:Brand:Diet Coke,Ingredients:Carbonated water;Caramel color;Aspartame;Phosphoric acid;Potassium benzoate (to protect taste);Natural flavors;Citric acid;Caffeine,Potential Allergens:None,Positive:No calories;No total fat;No sugars;No carbohydrates,Negatives:Contains aspartame and caffeine,Considerations:Contains additives like caramel color and potassium benzoate,Disclaimers:Not a significant source of saturated fat, trans fat, cholesterol, dietary fiber, vitamin D, calcium, iron, and potassium,Vegan:Yes,Vegetarian:Yes,Gluten-Free:Yes,Keto:Yes,Diabetic:Suitable,Paragraph1:Diet Coke provides a calorie-free beverage option, which can be suitable for those managing weight or sugar intake. It contains no sugars, fats, or carbohydrates, which aligns with dietary needs for diabetic management.,Paragraph2:The product contains caffeine and aspartame, which may be of concern for those sensitive to stimulants or artificial sweeteners. Its ingredients also include several additives like caramel color and potassium benzoate, which could raise health considerations for long-term consumption. Healthier alternatives might include naturally flavored water or herbal teas without artificial sweeteners. Brand:Sprite,Ingredients:Carbonated water;Less than 2% of: Citric acid;Potassium citrate;Natural flavors;Potassium benzoate (to protect taste);Aspartame;Acesulfame potassium,Potential Allergens:None,Positive:No calories;No total fat;No sugars;No carbohydrates,Negatives:Contains aspartame and acesulfame potassium,Considerations:Contains additives like potassium benzoate,Disclaimers:Not a significant source of saturated fat, trans fat, cholesterol, dietary fiber, vitamin D, calcium, iron, and potassium,Vegan:Yes,Vegetarian:Yes,Gluten-Free:Yes,Keto:Yes,Diabetic:Suitable,Paragraph1:Sprite offers a calorie-free option in the soda category, making it a potential choice for those managing weight or requiring a sugar-free diet. It has zero fat, carbohydrates, and protein, which may align well with various dietary restrictions.,Paragraph2:However, the presence of artificial sweeteners like aspartame and acesulfame potassium can be a concern for those avoiding synthetic additives. The drink also includes preservatives such as potassium benzoate, which might raise health considerations for sensitive individuals. Alternatives could include sparkling water with natural fruit flavoring without added sweeteners."
                    },
                    {
                    "text": "input:{\"publicationDate\": \"6/29/2023\",\"foodNutrients\": [{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1093,\"number\": \"307\",\"name\": \"Sodium, Na\",\"rank\": 5800,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150999,\"amount\": 11},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1004,\"number\": \"204\",\"name\": \"Total lipid (fat)\",\"rank\": 800,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150995,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 2000,\"number\": \"269\",\"name\": \"Total Sugars\",\"rank\": 1510,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150998,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1003,\"number\": \"203\",\"name\": \"Protein\",\"rank\": 600,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150994,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1008,\"number\": \"208\",\"name\": \"Energy\",\"rank\": 300,\"unitName\": \"kcal\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150997,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1005,\"number\": \"205\",\"name\": \"Carbohydrate, by difference\",\"rank\": 1110,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150996,\"amount\": 0}],\"brandOwner\": \"Coca-Cola USA Operations\",\"brandName\": \"DIET COKE\",\"brandedFoodCategory\": \"Soda\",\"householdServingFullText\": \"1 Can\",\"ingredients\": \"CARBONATED WATER, CARAMEL COLOR, ASPARTAME, PHOSPHORIC ACID, POTASSIUM C BENZOATE (TO PROTECT TASTE), NATURAL FLAVORS, CITRIC ACID, CAFFEINE\",\"packageWeight\": \"30 fl oz/888 mL\",\"notaSignificantSourceOf\": \"Not a significant source of saturated fat,trans fat, cholesterol, dietary fiber,vitamin D, calcium, iron and potassium.\",\"labelNutrients\": {6 items}} {\"publicationDate\": \"6/29/2023\",\"foodNutrients\": [{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1003,\"number\": \"203\",\"name\": \"Protein\",\"rank\": 600,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151291,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1235,\"number\": \"539\",\"name\": \"Sugars, added\",\"rank\": 1540,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151302,\"amount\": 16.7},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1253,\"number\": \"601\",\"name\": \"Cholesterol\",\"rank\": 15700,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151303,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1092,\"number\": \"306\",\"name\": \"Potassium, K\",\"rank\": 5700,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151299,\"amount\": 100},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1114,\"number\": \"328\",\"name\": \"Vitamin D (D2 + D3)\",\"rank\": 8700,\"unitName\": \"µg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151301,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1005,\"number\": \"205\",\"name\": \"Carbohydrate, by difference\",\"rank\": 1110,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151293,\"amount\": 20},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1079,\"number\": \"291\",\"name\": \"Fiber, total dietary\",\"rank\": 1200,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151296,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1087,\"number\": \"301\",\"name\": \"Calcium, Ca\",\"rank\": 5300,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151297,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1089,\"number\": \"303\",\"name\": \"Iron, Fe\",\"rank\": 5400,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151298,\"amount\": 3.33},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1004,\"number\": \"204\",\"name\": \"Total lipid (fat)\",\"rank\": 800,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151292,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1257,\"number\": \"605\",\"name\": \"Fatty acids, total trans\",\"rank\": 15400,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151304,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1093,\"number\": \"307\",\"name\": \"Sodium, Na\",\"rank\": 5800,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151300,\"amount\": 267},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1258,\"number\": \"606\",\"name\": \"Fatty acids, total saturated\",\"rank\": 9700,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151305,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1008,\"number\": \"208\",\"name\": \"Energy\",\"rank\": 300,\"unitName\": \"kcal\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151294,\"amount\": 83},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 2000,\"number\": \"269\",\"name\": \"Total Sugars\",\"rank\": 1510,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32151295,\"amount\": 16.67}],\"brandOwner\": \"Troyer Dist. Co.\",\"brandName\": \"WALT CHURCHILLS MARKET\",\"brandedFoodCategory\": \"Pickles, Olives, Peppers & Relishes\",\"householdServingFullText\": \"30 mL\",\"ingredients\": \"CUCUMBERS, ONIONS, WATER, SUGAR, VINEGAR, SALT, SPICES, TURMERIC (COLORING).\",\"packageWeight\": \"32 fl oz/946 mL\",\"notaSignificantSourceOf\": null,\"labelNutrients\": {\"fat\": {\"value\": 0},\"saturatedFat\": {\"value\": 0},\"transFat\": {\"value\": 0},\"cholesterol\": {\"value\": 0},\"sodium\": {\"value\": 80.1},\"carbohydrates\": {\"value\": 6},\"fiber\": {\"value\": 0},\"sugars\": {\"value\": 5},\"protein\": {\"value\": 0},\"vitaminD\": {\"value\": 0},\"calcium\": {\"value\": 0},\"iron\": {\"value\": 0.999},\"potassium\": {\"value\": 30},\"addedSugar\": {\"value\": 5.01},\"calories\": {\"value\": 24.9}}}"
                    },
                    {
                    "text": "output:Brand:Diet Coke,Ingredients:Carbonated water;Caramel color;Aspartame;Phosphoric acid;Potassium benzoate (to protect taste);Natural flavors;Citric acid;Caffeine,Potential Allergens:None,Positive:No calories;No total fat;No sugars;No carbohydrates,Negatives:Contains aspartame and caffeine,Considerations:Contains additives like caramel color and potassium benzoate,Disclaimers:Not a significant source of saturated fat, trans fat, cholesterol, dietary fiber, vitamin D, calcium, iron, and potassium,Vegan:Yes,Vegetarian:Yes,Gluten-Free:Yes,Keto:Yes,Diabetic:Suitable,Paragraph1:Diet Coke provides a calorie-free beverage option, which can be suitable for those managing weight or sugar intake. It contains no sugars, fats, or carbohydrates, which aligns with dietary needs for diabetic management.,Paragraph2:The product contains caffeine and aspartame, which may be of concern for those sensitive to stimulants or artificial sweeteners. Its ingredients also include several additives like caramel color and potassium benzoate, which could raise health considerations for long-term consumption. Healthier alternatives might include naturally flavored water or herbal teas without artificial sweeteners. Brand:Walt Churchills Market,Ingredients:Cucumbers;Onions;Water;Sugar;Vinegar;Salt;Spices;Turmeric (coloring),Potential Allergens:None,Positive:Low in fat;Source of Potassium;Low in calories,Negatives:Contains added sugar;Relatively high in sodium,Considerations:Serving size is 30ml;Consider overall dietary sodium intake,Disclaimers:Nutritional information may vary slightly depending on specific product variations,Vegan:Yes,Vegetarian:Yes,Gluten-Free:Yes,Keto:No,Diabetic:Suitable with moderation,Paragraph1:Walt Churchills Market pickles offer a low-fat and relatively low-calorie option.  However, they do contain added sugar, contributing to the overall carbohydrate content. While a source of potassium, they are also relatively high in sodium, which individuals with dietary restrictions should consider.  For diabetics, moderate consumption could be manageable depending on individual health and dietary plans.,Paragraph2:The main concern with this product is the sodium content. High sodium intake can contribute to health issues like high blood pressure for some individuals.  Moderation and considering overall dietary sodium are crucial.  For healthier alternatives, explore low-sodium or no-sugar-added pickle options or consider making homemade pickles with controlled ingredients."
                    },
                    {
                    "text": "input:{\"publicationDate\": \"6/29/2023\",\"foodNutrients\": [{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1093,\"number\": \"307\",\"name\": \"Sodium, Na\",\"rank\": 5800,\"unitName\": \"mg\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150999,\"amount\": 11},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1004,\"number\": \"204\",\"name\": \"Total lipid (fat)\",\"rank\": 800,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150995,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 2000,\"number\": \"269\",\"name\": \"Total Sugars\",\"rank\": 1510,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150998,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1003,\"number\": \"203\",\"name\": \"Protein\",\"rank\": 600,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150994,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1008,\"number\": \"208\",\"name\": \"Energy\",\"rank\": 300,\"unitName\": \"kcal\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150997,\"amount\": 0},{\"type\": \"FoodNutrient\",\"nutrient\": {\"id\": 1005,\"number\": \"205\",\"name\": \"Carbohydrate, by difference\",\"rank\": 1110,\"unitName\": \"g\"},\"foodNutrientDerivation\": {\"id\": 70,\"code\": \"LCCS\",\"description\": \"Calculated from value per serving size measure\"},\"id\": 32150996,\"amount\": 0}],\"brandOwner\": \"Coca-Cola USA Operations\",\"brandName\": \"DIET COKE\",\"brandedFoodCategory\": \"Soda\",\"householdServingFullText\": \"1 Can\",\"ingredients\": \"CARBONATED WATER, CARAMEL COLOR, ASPARTAME, PHOSPHORIC ACID, POTASSIUM C BENZOATE (TO PROTECT TASTE), NATURAL FLAVORS, CITRIC ACID, CAFFEINE\",\"packageWeight\": \"30 fl oz/888 mL\",\"notaSignificantSourceOf\": \"Not a significant source of saturated fat,trans fat, cholesterol, dietary fiber,vitamin D, calcium, iron and potassium.\",\"labelNutrients\": {6 items}} "
                    },
                    {
                    "text": "output:Brand:Diet Coke,Ingredients:Carbonated water;Caramel color;Aspartame;Phosphoric acid;Potassium benzoate (to protect taste);Natural flavors;Citric acid;Caffeine,Potential Allergens:None,Positive:No calories;No total fat;No sugars;No carbohydrates,Negatives:Contains aspartame and caffeine,Considerations:Contains additives like caramel color and potassium benzoate,Disclaimers:Not a significant source of saturated fat, trans fat, cholesterol, dietary fiber, vitamin D, calcium, iron, and potassium,Vegan:Yes,Vegetarian:Yes,Gluten-Free:Yes,Keto:Yes,Diabetic:Suitable,Paragraph1:Diet Coke provides a calorie-free beverage option, which can be suitable for those managing weight or sugar intake. It contains no sugars, fats, or carbohydrates, which aligns with dietary needs for diabetic management.,Paragraph2:The product contains caffeine and aspartame, which may be of concern for those sensitive to stimulants or artificial sweeteners. Its ingredients also include several additives like caramel color and potassium benzoate, which could raise health considerations for long-term consumption. Healthier alternatives might include naturally flavored water or herbal teas without artificial sweeteners. "
                    },
                    {
                    "text": json.dumps(food_details)
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 1,
            "topK": 0,
            "topP": 0.95,
            "maxOutputTokens": 8192,
            "stopSequences": []
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            # Parse the JSON response to extract the 'text' field from the generated content
            content_data = response.json()
            analysis_text = content_data['candidates'][0]['content']['parts'][0]['text']
            return https_fn.Response(json.dumps({"analysis": analysis_text}), status=200, headers={'Content-Type': 'application/json'})
        except (KeyError, IndexError, TypeError) as e:
            # Log and handle exceptions if the response structure is not as expected
            print(f"Error parsing response: {str(e)}")
            return https_fn.Response('Error parsing the generated content.', status=500)
    else:
        # Return error details if the API call was not successful
        return https_fn.Response(json.dumps({'error': response.status_code, 'message': response.text}), status=response.status_code)