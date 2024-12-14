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
    page_title="GreenFork: Youth Sustainability Platform",
    page_icon="🌱",
    layout="wide"
)

# Session State for Tracking Impact
if 'total_carbon_saved' not in st.session_state:
    st.session_state.total_carbon_saved = 0
if 'total_water_saved' not in st.session_state:
    st.session_state.total_water_saved = 0
if 'analyzed_foods' not in st.session_state:
    st.session_state.analyzed_foods = []

# Sidebar for Youth Engagement
def sidebar_youth_impact():
    st.sidebar.title("🌍 Your Sustainability Journey")
    
    # Impact Tracker
    st.sidebar.header("♻️ Impact Metrics")
    st.sidebar.metric("Carbon Saved", 
                      f"{st.session_state.total_carbon_saved:.2f} g CO₂")
    st.sidebar.metric("Water Conserved", 
                      f"{st.session_state.total_water_saved:.2f} liters")
    
    # Educational Resources
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
    st.title("🍽️ GreenFork")
    
    # Youth-Focused Introduction
    st.markdown("""
    ### Empowering Youth Through Sustainable Food Choices 🌱

    **Did you know?** Your food choices can make a big difference for the planet! 
    GreenFork helps you understand the environmental impact of what you eat.
    """)

    # Toggle for input method
    input_method = st.radio(
        "Choose how you want to input the food image:",
        ("📁 Upload an Image", "📸 Take a Photo"),
        index=0
    )

    # Initialize variables
    image_path = None
    image_display = None

    # Handle image input based on user choice
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

    # Process and display results if an image is provided
    if image_path:
        base64_image = encode_image(image_path)

        try:
            # Identify the food item
            food_name = get_food_classification(base64_image)
            food_data = get_nutrition_data(food_name)

            # Ensure food_data is a dictionary
            if isinstance(food_data, str):
                try:
                    food_data = json.loads(food_data)
                except json.JSONDecodeError:
                    st.error("⚠️ Failed to parse nutrition data. Please try again.")
                    food_data = {}

            # Check if valid data is returned
            if not food_data or not food_name:
                st.warning("⚠️ Could not identify the food item. Please try another image.")
            else:
    # Extract impact metrics
                carbon_impact = food_data['environmental_impact']['carbon_footprint_gCO2']
                water_impact = food_data['environmental_impact']['water_usage_liters']

                # Update session state for metrics
                st.session_state.total_carbon_saved += carbon_impact
                st.session_state.total_water_saved += water_impact
                st.session_state.analyzed_foods.append(food_name)
                col1, col2 = st.columns([1, 2])

                # Left Column: Display the Image and Food Title
                with col1:
                    st.image(image_display, caption="Uploaded Food Image", use_container_width=True)

                # Right Column: Display Food Name and Environmental Impact
                with col2:
                    st.markdown("### ")
                    st.write(f"**{food_name}**")
                st.markdown("---")

                # Youth Education Section
                st.markdown("### 🌍 Your Sustainability Impact")
                col3, col4 = st.columns(2)
                with col3:
                # Environmental Impact Visualization
                    impact_df = pd.DataFrame([
                        {"Metric": "Carbon Footprint", "Value": carbon_impact, "Unit": "g CO₂"},
                        {"Metric": "Water Usage", "Value": water_impact, "Unit": "liters"}
                    ])
                    
                    fig_impact = px.bar(
                        impact_df, x="Metric", y="Value", 
                        text=[f"{val} {unit}" for val, unit in zip(impact_df['Value'], impact_df['Unit'])],
                        title="Environmental Impact of Your Food",
                        color="Metric",
                        color_discrete_sequence=["#A1EEBD", "#C6E7FF"]
                    )
                    st.plotly_chart(fig_impact, use_container_width=True)

                with col4:
            # Nutrient Breakdown
                    if 'nutrition' in food_data and all(k in food_data['nutrition'] for k in ['protein_g', 'carbs_g', 'fats_g']):
    # Create DataFrame for nutrients
                        nutrients = pd.DataFrame([
                            {"Nutrient": "Protein", "Amount": food_data['nutrition']['protein_g'], "Unit": "g"},
                            {"Nutrient": "Carbs", "Amount": food_data['nutrition']['carbs_g'], "Unit": "g"},
                            {"Nutrient": "Fats", "Amount": food_data['nutrition']['fats_g'], "Unit": "g"},
                        ])
                        
                        # Display Nutrient Bar Plot
                        fig_nutrients = px.bar(
                            nutrients, 
                            x="Nutrient", 
                            y="Amount",
                            text=[f"{amt} {unit}" for amt, unit in zip(nutrients['Amount'], nutrients['Unit'])],  # Fixed text
                            title="Nutrient Breakdown (g)", 
                            color="Nutrient",
                            color_discrete_sequence=["#A1EEBD", "#C6E7FF", "#73BBA3"]
                        )
                        st.plotly_chart(fig_nutrients, use_container_width=True)


                # Sustainability Insights
                st.subheader("Sustainability Insights 🌱")
                sustainability_data = food_data.get("sustainability", {})
                if sustainability_data:
                    st.write(f"- **Seasonality:** {sustainability_data.get('seasonality', 'N/A')}")
                    st.write(f"- **Local vs Imported:** {sustainability_data.get('local_vs_imported', 'N/A')}")
                    st.write(f"- **Food Waste Risk:** {sustainability_data.get('food_waste_risk', 'N/A')}")

                # Interactive Quiz Button
                
        except Exception as e:
            st.error(f"An error occurred while processing the image: {e}")

# Run the main app
if __name__ == "__main__":
    sidebar_youth_impact()
    main()
