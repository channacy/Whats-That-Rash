import streamlit as st
import os
import numpy as np
from PIL import Image
import requests
from dotenv import load_dotenv
from openai import OpenAI
import io

load_dotenv()  

client = OpenAI(api_key=os.getenv("GPTKEY"))

st.title("WHAT\'S THAT RASH?")
st.write("Concerned? Let's find out what is that rash") 

desc = st.multiselect("What is your rash like?", ["bumpy","rough", "dry", "red","white","clustered", "scaly", "blister", "crusty", "painful", "itchy", "warm", "tender", "hot","flaky", "scabbed", "burning", "tingly" ],None)
st.write(desc)

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width =True)

    with st.container(border=True):
        st.write("Send email with uploaded image and suggested diagnosis as saved PDF.") 
        if st.button(label="Generate Report"):
            image = image.convert("RGB")
            pdf_bytes = io.BytesIO()
            image.save(pdf_bytes, format="PDF")
            pdf_bytes.seek(0)
            st.success("PDF generated successfully!")
            st.download_button(
                label="Send",
                data=pdf_bytes,
                file_name="converted_image.pdf",
                mime="application/pdf"
            )

        st.link_button("Send Gmail", url="https://mail.google.com/mail/?view=cm&fs=1&to=&su=Concerns%20About%20My%20Health&body=Please%20find%20the%20PDF%20document%20attached.%0A%0A%28You%20can%20manually%20attach%20the%20PDF%29%0A%0ABest%20Regards,")
