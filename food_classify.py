import base64
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize API key
Groq_API = os.getenv("GROQ_API_KEY")
client = Groq(api_key=Groq_API)
# encode image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

#  get food classification

with open ('prompt/food_classifiy_prompt.txt', 'r') as file:
    prompt = file.read().strip()

def get_food_classification(base64_image):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt },
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
# get food data

with open ('prompt/food_data.txt', 'r') as file:
    food_data = file.read().strip()
# Function to get nutrition and eco-impact data
def get_nutrition_data(food_name):
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "system",
                "content": food_data
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