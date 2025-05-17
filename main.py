import streamlit as st
import cv2
import os
import numpy as np
from PIL import Image
import requests
from dotenv import load_dotenv

load_dotenv()  
from openai import OpenAI
client = OpenAI(api_key=os.getenv("GPTKEY"))

# response = client.responses.create(
#     model="gpt-4.1",
#     input="Write a one-sentence bedtime story about a unicorn."
# )

st.title("WHAT\'S THAT RASH?")
st.write("Concerned? Let's find out what is that rash") 

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width =True)
