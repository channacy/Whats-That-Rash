import streamlit as st
import os
from dotenv import load_dotenv
import base64
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key = os.getenv("GPTKEY"))

st.title("What's That Rash?")

def encode_image(image):
    return base64.b64encode(image.read()).decode("utf-8")

skinCondition = st.file_uploader("Upload a Picture of Your Skin Condition", type=["jpg", "jpeg", "png"])

if skinCondition:
    st.image(skinCondition, caption = "Uploaded image", use_container_width =True)

    base64_image = encode_image(skinCondition)

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user", 
                "content": [
                    { "type": "text", "text": "You are a dermatologist that assesses skin conditions" },
                    { "type": "text", "text": "Within 500 characters, could you identify the image and create a report to highlight important details of the skin condition, what condition it most likely is, and in bullet points, provide medical recommendations. Make it simple for the average consumer to understand." },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        },     
                    },
                ]
            }
        ],
        temperature = 0.0
    )
    
    st.markdown(response.choices[0].message.content)