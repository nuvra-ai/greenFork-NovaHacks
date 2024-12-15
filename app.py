import streamlit as st
import os
import json
import base64
import pandas as pd
import plotly.express as px
from PIL import Image
from food_classify import get_food_classification, get_nutrition_data, encode_image

# Page Configuration
st.set_page_config(
    page_title="GreenFork",
    page_icon="🌱",
    layout="wide"
)

# Session State
if 'total_carbon_saved' not in st.session_state:
    st.session_state.total_carbon_saved = 0
if 'total_water_saved' not in st.session_state:
    st.session_state.total_water_saved = 0
if 'analyzed_foods' not in st.session_state:
    st.session_state.analyzed_foods = []

def sidebar():    
    #  Tracker impact
    st.sidebar.header("♻️ Impact Metrics")
    st.sidebar.metric("Carbon Footprint", 
                      f"{st.session_state.total_carbon_saved:.2f} g CO₂")
    st.sidebar.metric("Water Conserved", 
                      f"{st.session_state.total_water_saved:.2f} liters")
    
    st.sidebar.header("Learn More")
    sdg_resources = {
        "Climate Action": "https://sdgs.un.org/goals/goal13",
        "Responsible Consumption": "https://sdgs.un.org/goals/goal12",
        "Zero Hunger": "https://sdgs.un.org/goals/goal2"
    }
    
    for goal, link in sdg_resources.items():
        st.sidebar.markdown(f"[🔗 {goal}]({link})")

# Main App
def main():
    col1, col2 = st.columns([1, 10])  
    
    with col1:
        st.image("green-fork.png", width=80)  
    
    with col2:
        st.markdown("""
       <h1 style='display: inline-block; 
                   vertical-align: middle; 
                   font-size: 46px; 
                   margin-top: 0; 
                   font-family: system-ui, Helvetica, sans-serif; 
                   color:rgb(20, 141, 91);'>
        GreenFork
        </h1>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        .content-box {
            background-color:rgb(166, 216, 177);
            border: 2px solid #2C6E49;
            border-radius:8px;
            padding: 10px;
            margin-bottom: 17px;      
            box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1); 
        }
        .content-box h3 {
            font-family: 'Arial', sans-serif;
            font-size: 20px;
            color: #2C6E49;
            margin-top: 0;
        }
        .content-box p {
            font-family: 'Arial', sans-serif;
            font-size: 15px;
            color: #333;
        }
    </style>

    <div class="content-box">
        <h4>Empowering Youth Through Sustainable Food Choices 🌱</h4>
        <p><strong>Did you know?</strong> Your food choices can make a big difference for the planet! 
        GreenFork helps you understand the environmental impact of what you eat.</p>
    </div>
""", unsafe_allow_html=True)

    #input method
    input_method = st.radio(
        "Choose how you want to input the food image:",
        ("📁 Upload an Image", "📸 Take a Photo"),
        index=0
    )

    image_path = None
    image_display = None

    # Handle image 
    if input_method == "📁 Upload an Image":
        uploaded_file = st.file_uploader("Upload an image of a food item", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            temp_path = "temp_image.jpg"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            image_path = temp_path
            image_display = temp_path

    elif input_method == "📸 Take a Photo":
        camera_input = st.camera_input("Capture an image of a food item")
        if camera_input is not None:
            image_path = "captured_image.jpg"
            with open(image_path, "wb") as f:
                f.write(camera_input.getvalue())
            image_display = image_path

    # Process and results 
    if image_path:
        base64_image = encode_image(image_path)

        try:
            # Identify  food 
            food_name = get_food_classification(base64_image)
            food_data = get_nutrition_data(food_name)

            
            if isinstance(food_data, str):
                try:
                    food_data = json.loads(food_data)
                except json.JSONDecodeError:
                    st.error("⚠️ Failed to parse nutrition data. Please try again.")
                    food_data = {}
            # validation for json format
            if not food_data or not food_name:
                st.warning("⚠️ Could not identify the food item. Please try another image.")
            else:
                carbon_impact = food_data['environmental_impact']['carbon_footprint_gCO2']
                water_impact = food_data['environmental_impact']['water_usage_liters']

                # Update metrics
                st.session_state.total_carbon_saved += carbon_impact
                st.session_state.total_water_saved += water_impact
                st.session_state.analyzed_foods.append(food_name)
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.image(image_display, caption="Uploaded Food Image", use_container_width=True)
                with col2:
                    st.markdown("### ")
                    st.write(f"**{food_name}**")
                st.markdown("---")

                st.markdown("#### 🌍 Your Sustainability Impact")

                env_impact = food_data.get("environmental_impact", {})
                if env_impact:
                    st.write(f"- **✅Healthy:** {env_impact.get('healthy', 'N/A')}")
                    st.write(f"- **♻️Eco Friendly:** {env_impact.get('eco_friendly', 'N/A')}")
                col3, col4 = st.columns(2)
                with col3:
                    impact_df = pd.DataFrame([
                        {"Metric": "Carbon Footprint", "Value": carbon_impact, "Unit": "g CO₂"},
                        {"Metric": "Water Usage", "Value": water_impact, "Unit": "liters"}
                    ])
                    
                    fig_impact = px.bar(
                        impact_df, x="Metric", y="Value", 
                        text=[f"{val} {unit}" for val, unit in zip(impact_df['Value'], impact_df['Unit'])],
                        title="Environmental Impact of Your Food",
                        color="Metric",
                        color_discrete_sequence=["#4A628A", "#40A578"]
                    )
                    st.plotly_chart(fig_impact, use_container_width=True)

                with col4:
            # Nutrient 
                    if 'nutrition' in food_data and all(k in food_data['nutrition'] for k in ['protein_g', 'carbs_g', 'fats_g']):
                        nutrients = pd.DataFrame([
                            {"Nutrient": "Protein", "Amount": food_data['nutrition']['protein_g'], "Unit": "g"},
                            {"Nutrient": "Carbs", "Amount": food_data['nutrition']['carbs_g'], "Unit": "g"},
                            {"Nutrient": "Fats", "Amount": food_data['nutrition']['fats_g'], "Unit": "g"},
                        ])
                        
                        fig_nutrients = px.bar(
                            nutrients, 
                            x="Nutrient", 
                            y="Amount",
                            text=[f"{amt} {unit}" for amt, unit in zip(nutrients['Amount'], nutrients['Unit'])],  # Fixed text
                            title="Nutrient Breakdown (g)", 
                            color="Nutrient",
                            color_discrete_sequence=["#74E291", "#59B4C3", "#40A578"]
                        )
                        st.plotly_chart(fig_nutrients, use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                #  Insights
                    st.subheader("Sustainability Insights 🌱")
                    sustainability_data = food_data.get("sustainability", {})
                    if sustainability_data:
                        st.write(f"- **Seasonality:** {sustainability_data.get('seasonality', 'N/A')}")
                        st.write(f"- **Local vs Imported:** {sustainability_data.get('local_vs_imported', 'N/A')}")
                        st.write(f"- **Food Waste Risk:** {sustainability_data.get('food_waste_risk', 'N/A')}")
                with col2:
                    st.subheader("Better Food Options ")
                    food_options = food_data.get("recommendations", {})
                    if food_options:
                        healthier_alternatives = food_options.get("healthier_alternatives", [])
                        if healthier_alternatives:
                            st.write("- **Healthier Alternatives:**")
                            for alt in healthier_alternatives:  # Iterate over the list directly
                                st.write(f"- {alt}")
                        sustainable_substitutes = food_options.get("sustainable_substitutes", [])
                        if sustainable_substitutes:
                            st.write("- **Sustainable Substitutes:**")
                            for sub in sustainable_substitutes:  # Iterate over the list directly
                                st.write(f"- {sub}")
                        st.write("**Sustainable Substitutes:**")
                        for alt in food_options.get("sustainable_substitutes", []):
                            st.write(f"- {alt}")
                        st.write("**Storage Tips:**")
                        st.write(f"- {food_options.get('storage_tips', 'N/A')}")
                        
        except Exception as e:
            st.error(f"An error occurred while processing the image: {e}")

# main app
if __name__ == "__main__":
    sidebar()
    main() 
