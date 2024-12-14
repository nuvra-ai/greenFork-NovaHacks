import streamlit as st
import os
import json
import base64
import pandas as pd
import plotly.express as px
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
                    {"type": "text", "text": '''Identify the food item in the image. If it's a burger, tell me what kind of burger it is, like a cheeseburger or veggie burger. Just return the name of the food. Provide no extra descriptions or information.'''},
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

Here is the format below, and I will provide descriptions of each individual attribute in the JSON body:
{
    "food_name": string, // the name of the food
    "calories_lower": int, // lower bound for calorie estimation range
    "calories_upper": int, // upper bound for calorie estimation range
    "carbon_emissions": int, // grams of CO₂ emissions for the food's production
    "gallons_per_item_produced": int, // gallons of water needed to produce the food
    "grams_of_protein": int,
    "grams_of_carbs": int,
    "grams_of_fats": int,
    "calories_from_protein": int,
    "calories_from_carbs": int,
    "calories_from_fats": int,
    "healthy": boolean, // True if healthy, False otherwise
    "environmentally_friendly": boolean, // True if eco-friendly, False otherwise
    "sustainability_tips": [string], // A list of actionable sustainability tips related to this food
    "healthier_alternatives": { 
        "alternative_1": string, // Suggest a healthier alternative
        "alternative_2": string  // Suggest another alternative
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

# Streamlit app
st.title("Food Classification and Sustainability Insights")

# uploaded_file = st.file_uploader("Upload an image of a food item", type=["jpg", "jpeg", "png"])

# Toggle for input method
input_method = st.radio(
    "Select an input method:",
    ("Upload an image", "Take a photo"),
    index=0
)

image_path = None

if input_method == "Upload an image":
    uploaded_file = st.file_uploader("Upload an image of a food item", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        temp_path = "temp_image.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        image_path = temp_path

elif input_method == "Take a photo":
    camera_input = st.camera_input("Capture an image of a food item")
    if camera_input is not None:
        image_path = "captured_image.jpg"
        with open(image_path, "wb") as f:
            f.write(camera_input.getvalue())

if image_path:
    base64_image = encode_image(image_path)

    try:
        # Identify the food item
        food_name = get_food_classification(base64_image)

        # Get nutrition and eco-impact data
        food_data = get_nutrition_data(food_name)

        # Display food name
        st.header(f"Food Item: {food_name}")

        # Display nutrient breakdown
        nutrients = pd.DataFrame([
            {"Nutrient": "Protein", "Amount": food_data['grams_of_protein']},
            {"Nutrient": "Carbs", "Amount": food_data['grams_of_carbs']},
            {"Nutrient": "Fats", "Amount": food_data['grams_of_fats']},
        ])
        fig_nutrients = px.bar(nutrients, x="Nutrient", y="Amount", title="Nutrient Breakdown (g)",
                               color="Nutrient", text="Amount")
        st.plotly_chart(fig_nutrients)

        # Display calorie distribution
        calorie_sources = pd.DataFrame([
            {"Source": "Protein", "Calories": food_data['calories_from_protein']},
            {"Source": "Carbs", "Calories": food_data['calories_from_carbs']},
            {"Source": "Fats", "Calories": food_data['calories_from_fats']},
        ])
        fig_calories = px.pie(calorie_sources, values="Calories", names="Source",
                              title="Calorie Distribution")
        st.plotly_chart(fig_calories)

        # Display environmental impact
        st.subheader("Environmental Impact")
        st.write(f"Carbon Emissions: {food_data['carbon_emissions']} g CO2")
        st.write(f"Water Usage: {food_data['gallons_per_item_produced']} gallons")
        st.write(f"Eco-Friendly: {'Yes' if food_data['environmentally_friendly'] else 'No'}")
        st.write(f"Healthy: {'Yes' if food_data['healthy'] else 'No'}")

        # Display sustainability tips
        st.subheader("Sustainability Tips")
        for tip in food_data.get('sustainability_tips', []):
            st.write(f"- {tip}")

        # Display healthier alternatives
        st.subheader("Healthier Alternatives")
        for key, alt in food_data.get("healthier_alternatives", {}).items():
            st.write(f"- {alt}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
