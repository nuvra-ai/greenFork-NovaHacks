import base64
import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize the Groq client with the API key
Groq_API = os.getenv("GROQ_API_KEY")
client = Groq(api_key=Groq_API)
# Function to encode the image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to get food classification
def get_food_classification(base64_image):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": '''Identify the food item in the image. If it's a burger, tell me what kind of burger it is, like a cheeseburger or veggie burger. Just return the name of the food. Provide no extra descriptions or information. 
                     If provided image is not food, then always return 'Nothing' dont try to classify things other than food.'''},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    return chat_completion.choices[0].message.content

# Function to get nutrition and eco-impact data
def get_nutrition_data(food_name):
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "system",
                "content": '''I want you to return something to me in the exact JSON body format that I request. 
Your response should comprise only the JSON body I request and nothing other than it. 
DO NOT include the triple tricks to make it a code block. I want it to simply be a string in JSON format 
which I can do json.loads() on. 

Make sure there are no extra spaces. MAKE SURE THERE ARE NO SPECIAL CHARACTERS, 
ESPECIALLY ($, [, ], /, .). 

Pretend you are a nutrition scientist and environmental scientist working together. 
When labeling items as either healthy or unhealthy, make sure to be reasonable in your classifications. 
Things that fall into the categories of fruits, vegetables, lean meats, and other food that is traditionally 
seen as good for a human should be labeled as healthy.

For environmental impact classifications, take into account water usage, carbon emissions, and whether the 
food is locally sourced or seasonal. Suggest unique and practical ways to reduce food waste and carbon emissions.

Include actionable **sustainability tips** that relate to this food item, such as how to minimize waste, 
make eco-friendly choices, or its role in a sustainable diet. Make these tips practical, localized, and creative. 

Here is the format below, and You will provide descriptions of each individual attribute in the JSON body:
{
    {
  "food_name": "Avocado",
  "nutrition": {
    "calories": 160,
    "protein_g": 2,
    "carbs_g": 9,
    "fats_g": 15,
  },
  "environmental_impact": {
    "carbon_footprint_gCO2": 2.5,
    "water_usage_liters": 320,
    "eco_friendly": false,
    "healthy": Yes, // Yes if healthy, No otherwise
  },
  "sustainability": {
    "seasonality": "Not in season",
    "local_vs_imported": "Imported",
    "food_waste_risk": "Medium"
  },
  "recommendations": {
    "healthier_alternatives": ["Spinach", "Broccoli"],
    "sustainable_substitutes": ["Chickpeas", "Lentils"],
    "storage_tips": "Store in a cool, dry place to avoid early ripening."
  }
  }

}
'''
            },
            {
                "role": "user",
                "content": f"Please classify the food item: {food_name}"
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    return json.loads(completion.choices[0].message.content)





        # print(f"✅ Food details saved successfully for: {food_details['food_name']}")
# image = encode_image("temp_image.jpg")
# food_name = get_food_classification(image)
# print(get_nutrition_data(food_name))