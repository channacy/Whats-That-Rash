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
                    { "type": "text", "text": "Could you describe the image and create a report to highlight important details of the skin condition, and provide medical recommendations. Create a report with observations, important details and recommendations with bullet points." },
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

# if "WTR" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("How can we help you today?"):
#     response = client.responses.create(
#         model="gpt-4.1",
#         input="Write a one-sentence bedtime story about a unicorn."
#     )

#     st.title("WHAT\'S THAT RASH?")
#     st.write("Concerned? Let's find out what is that rash") 
#     response = client.responses.create(
#         model="gpt-4.1-mini",
#         input=[{
#             "role": "user",
#             "content": [
#                 {"type": "input_text", "text": "what's in this image?"},
#                 {
#                     "type": "input_image",
#                     "image_url": "https://www.minecraftskins.com/uploads/preview-skins/2025/03/25/my-first-minecraft-youtube-skin-extended-version--23141318.png?v825",
#                 },
#             ],
#         }],
#     )

