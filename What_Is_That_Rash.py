# Libraries
import os
import io
import re
import base64
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

# Load environment key for OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("GPTKEY"))

# Set Page's Title and Icon
st.set_page_config(page_title="What's That Rash?", page_icon="images/logo.png")

# Helper Functions
def render_markdown_to_pdf(c, text, x, y, max_width=450, line_height=16):
    text_obj = c.beginText()
    text_obj.setTextOrigin(x, y)
    text_obj.setFont("Helvetica", 12)

    parts = re.split(r'(\*\*.*?\*\*)', text)

    lines = []
    current_line = []
    current_width = 0

    def get_font(part):
        return "Helvetica-Bold" if part.startswith("**") and part.endswith("**") else "Helvetica"

    def get_text(part):
        return part[2:-2] if part.startswith("**") and part.endswith("**") else part

    words_with_fonts = []
    for part in parts:
        font = get_font(part)
        txt = get_text(part)
        words = txt.split(' ')
        for i, word in enumerate(words):
            if word:
                words_with_fonts.append((word, font))
            if i < len(words) - 1:
                words_with_fonts.append((" ", font))

    for word, font in words_with_fonts:
        width = stringWidth(word, font, 12)
        if current_width + width > max_width and current_line:
            lines.append(current_line)
            current_line = [(word, font)]
            current_width = width
        else:
            current_line.append((word, font))
            current_width += width

    if current_line:
        lines.append(current_line)

    for line in lines:
        for word, font in line:
            text_obj.setFont(font, 12)
            text_obj.textOut(word)
        text_obj.textLine("")

    c.drawText(text_obj)
    return y - line_height * len(lines)


def encode_image(image):
    return base64.b64encode(image.read()).decode("utf-8")

# Main UI container
with stylable_container(
    key="wrapper_container",
    css_styles="""
        {
            background-color: #A8DADC;
            border: rounded;
            border-radius: 25px;
            padding: 20px;
        }
    """,
):
    st.sidebar.success("Select a page below")

    st.logo("images/logo.png", size="large")
    st.title("What's That Rash?", anchor=False)
    st.write("Concerned? Let's find out what that rash is")

    descList = st.multiselect(
        "What is your rash like?",
        [
            "Bumpy", "Rough", "Dry", "Scaly", "Flaky", "Crusty", "Scabbed",
            "Red", "White", "Darkened", "Discolored", "Bruised",
            "Clustered", "Spread", "Localized",
            "Blistered", "Oozing", "Swollen", "Raised", "Indented",
            "Painful", "Itchy", "Burning", "Tingling", "Tender", "Warm", "Hot", "Numb"
        ],
        None,
    )

# Upload Image
skinCondition = st.file_uploader("Upload a Picture of Your Skin Condition", type=["jpg", "jpeg", "png"])

# GPT Integration
if skinCondition:
    st.image(skinCondition, caption="Uploaded image", use_container_width=True)
    base64_image = encode_image(skinCondition)

    common_prompt = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "You are a dermatologist that assesses skin conditions, including inflammatory, autoimmune and connective tissue, neoplastic, pigmentary, infectious, genetic and congenital, drug-induced and trauma and scarring disorders."},
                {
                    "type": "text",
                    "text": (
                        "Within 2000 characters with the title being WTR Report, analyse the image and "
                        "create a report to highlight what condition it most likely is, and in bullet points, "
                        "provide medical recommendations. Make sure the average user will be able to understand the report."
                    ),
                }
            ]
        }
    ]

    if descList:
        common_prompt[0]["content"].append({"type": "text", "text": ','.join(descList)})

    common_prompt[0]["content"].append({
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}",
            "detail": "low"
        }
    })

    response = client.chat.completions.create(
        model="ft:gpt-4o-2024-08-06:channacy::BYifiu0c",
        messages=common_prompt,
        temperature=0.0,
    )

    if response.choices[0].message.content == "I'm sorry, I can't assist with that." or "I'm unable to analyze images or provide specific medical diagnoses" in response.choices[0].message.content or "I'm unable to analyze images or provide medical diagnoses" in response.choices[0].message.content:
        response = client.chat.completions.create(
        model="gpt-4.1",
        messages=common_prompt,
        temperature=0.0,
    )
        
    st.markdown(response.choices[0].message.content)

# PDF Report Generator
with st.container():
    st.write("Download report with uploaded image and suggested diagnosis as saved PDF.")

    if st.button(label="Generate Report", type="primary", icon="📄") and skinCondition:
        try:
            image = Image.open(skinCondition).convert("RGB")
            pdf_bytes = io.BytesIO()
            c = canvas.Canvas(pdf_bytes, pagesize=letter)

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 770, "Skin Condition Report")

            c.setFont("Helvetica", 12)
            c.drawString(50, 750, "Uploaded Image:")
            image_reader = ImageReader(image)
            c.drawImage(image_reader, 50, 500, width=300, height=200, preserveAspectRatio=True)

            c.drawString(50, 470, "Self-Described Symptoms:")
            y = 450
            for sym in descList:
                c.drawString(60, y, f"- {sym}")
                y -= 15

            c.drawString(50, y - 20, "Suggested Diagnosis and Treatment:")
            y -= 40

            response_text = response.choices[0].message.content.strip().split("\n")
            for paragraph in response_text:
                if paragraph.strip():
                    y = render_markdown_to_pdf(c, paragraph.strip(), 60, y, max_width=480)
                    y -= 10
                    if y < 60:
                        c.showPage()
                        y = 750

            c.save()
            pdf_bytes.seek(0)
            st.success("PDF generated successfully!")

            st.download_button(
                label="Download",
                type="primary",
                icon="💾",
                data=pdf_bytes,
                file_name="WTR Report.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error generating PDF: {e}")

    st.link_button(
        "Send Gmail",
        type="primary",
        icon="📩",
        url="https://mail.google.com/mail/?view=cm&fs=1&to=&su=Concerns%20About%20My%20Health&body=Please%20find%20the%20PDF%20document%20attached.%0A%0A%28You%20can%20manually%20attach%20the%20PDF%29%0A%0ABest%20Regards,"
    )

# Disclaimer
st.markdown("**Disclaimer**")
st.markdown(
    '<div style="text-align: justify;">'
    'The content provided on this platform is for informational and educational purposes only and is not intended as a substitute for professional medical advice, diagnosis, or treatment. '
    'Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. '
    'Never disregard professional medical advice or delay in seeking it because of something you have read here. '
    'If you think you may have a medical emergency, call your doctor or emergency services immediately. '
    'Reliance on any information provided by this platform is solely at your own risk.'
    '</div>',
    unsafe_allow_html=True
)
