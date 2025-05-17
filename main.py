import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import io
import base64

load_dotenv()  

client = OpenAI(api_key=os.getenv("GPTKEY"))

st.title("WHAT\'S THAT RASH?")
st.write("Concerned? Let's find out what is that rash") 

descList = st.multiselect("What is your rash like?", ["bumpy","rough", "dry", "red","white","clustered", "scaly", "blister", "crusty", "painful", "itchy", "warm", "tender", "hot","flaky", "scabbed", "burning", "tingly" ],None)
st.write(descList)
desc = ','.join(descList)
st.write("Your patient describes the rash to be " + desc)

def encode_image(image):
    return base64.b64encode(image.read()).decode("utf-8")

skinCondition = st.file_uploader("Upload a Picture of Your Skin Condition", type=["jpg", "jpeg", "png"])

if skinCondition:
    st.image(skinCondition, caption = "Uploaded image", use_container_width =True)
    base64_image = encode_image(skinCondition)
    if len(descList) > 0:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user", 
                    "content": [
                        { "type": "text", "text": "You are a dermatologist that assesses skin conditions" },
                        { "type": "text", "text": "Could you describe the image and create a report to highlight important details of the skin condition, and provide medical recommendations. Create a report with observations, important details and recommendations with bullet points." },
                        { "type": "text", "text": "You are a dermatologist that assesses skin conditions" },
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
    else:
        st.image(skinCondition, caption = "Uploaded image", use_container_width =True)
        base64_image = encode_image(skinCondition)
        if len(descList) > 0:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            { "type": "text", "text": "You are a dermatologist that assesses skin conditions" },
                            { "type": "text", "text": "Could you describe the image and create a report to highlight important details of the skin condition, and provide medical recommendations. Create a report with observations, important details and recommendations with bullet points." },
                            { "type": "text", "text": "You are a dermatologist that assesses skin conditions" },
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
