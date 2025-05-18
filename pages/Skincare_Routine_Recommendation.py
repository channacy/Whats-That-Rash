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
st.set_page_config(page_title="Skincare recommendation", page_icon="images/logo.png")

# Function to render markdown to PDF
def render_markdown_to_pdf(c, text, x, y, max_width=450, line_height=16):
    """Render markdown (**bold**) text into PDF with proper word wrapping and styling."""
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
                words_with_fonts.append((" ", font))  # add space between words

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

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'response' not in st.session_state:
    st.session_state.response = None

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
    st.logo("images/logo.png", size="large")
    st.title("Skincare Routine Recommendation", anchor=False)
    st.write("Find the right routine for you!")

    skintype = st.selectbox(
        "What is your skin type?",
        ["Normal", "Dry", "Oily", "Combination"]
    )

    concernList = st.multiselect(
        "What are your concerns?",
        ["Acne", "Dry Skin", "Uneven Skin Texture", "Blemish Scars", "Hyperpigmentation", "Wrinkles", "Blackheads", "Oily Skin", "Acne Scar"]
    )

    if st.button(label="Submit", type="primary",icon="✅"):
        st.session_state.submitted = True
        if concernList:
            concerns = ', '.join(concernList)
            prompt = f"Given someone with {skintype} skin who wants to primarily fix {concerns}. " \
                     f"Within 2000 characters with the title being Skincare Routine, " \
                     f"provide recommendations for a routine and products in bullet points. " \
                     f"State the step name, frequency and purpose of step. " \
                     f"Finally, provide Amazon shopping search results, where the hyperlink is the product's name, to the products mentioned."\
                     f"Make sure the average user will be able to understand the report."
        else:
            prompt = f"Given someone with {skintype} skin. " \
                     f"Within 2000 characters with the title being Skincare Routine, " \
                     f"provide recommendations for a routine and products in bullet points. " \
                     f"State the step name, frequency and purpose of step. " \
                     f"Finally, provide Amazon shopping search results, where the hyperlink is the product's name, to the products mentioned."\
                     f"Make sure the average user will be able to understand the report."

        st.session_state.response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            temperature=0.0,
        )

# Display response and download option
if st.session_state.submitted:
    st.markdown(st.session_state.response.choices[0].message.content)

    with st.container():
        st.write("Download routine as saved PDF.")

        if st.button(label="Generate Report", type="primary", icon="📄"):
            try:
                pdf_bytes = io.BytesIO()
                c = canvas.Canvas(pdf_bytes, pagesize=letter)

                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, 770, "Skincare Routine")

                c.setFont("Helvetica", 12)
                c.drawString(50, 750, "Concerns:")
                y = 720
                for sym in concernList:
                    c.drawString(60, y, f"- {sym}")
                    y -= 15

                c.drawString(50, y - 20, "Suggested Routine:")
                y -= 40

                response_text = st.session_state.response.choices[0].message.content.strip().split("\n")
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
                    file_name="report.pdf",
                    mime="application/pdf",
                )

            except Exception as e:
                st.error(f"Error generating PDF: {e}")

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