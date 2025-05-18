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

# Functions
def render_markdown_to_pdf(c, text, x, y, max_width=450, line_height=16):
    """Render markdown (**bold**) text into PDF with proper word wrapping and styling."""
    text_obj = c.beginText()
    text_obj.setTextOrigin(x, y)
    text_obj.setFont("Helvetica", 12)

    # Split text into parts (plain and **bold** chunks)
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

    # Draw each line
    for line in lines:
        for word, font in line:
            text_obj.setFont(font, 12)
            text_obj.textOut(word)
        text_obj.textLine("")

    c.drawText(text_obj)
    return y - line_height * len(lines)  # return new y position


# Main UI container
with stylable_container(
    key="wrapper_container",
    css_styles="""
        { 
            background-color: #BFE7F9;
            border: rounded;
            border-radius: 25px;
            padding: 35px;
        }
    """,
):
    # Header for website
    st.title("Skincare recommendation")
    st.write("Find the right routine for you")

    # Tag selection for rash description
    skintype = st.selectbox(
        "What is your skin type?",
        [
            "normal", "dry", "oily", "combination"
        ],
    )
    concernList = st.multiselect("What are your concerns?", ["acne", "dry skin", "blemish scars", "wrinkles", "black heads", "oily skin", "acne scar"])

    # GPT Integration
    submitted = False
    if st.button("Submit"):
        submitted = True
        # Only include description list in prompt if user provided any
        if concernList and len(concernList) > 0:
            concerns = ','.join(concernList)
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Given someone with " + skintype + "skin who wants to primarily fix " + concerns +
                            ". Within 1000 characters with the title being Skincare Routine, "
                                "provide recommendations for a routine and products in bullet points. "
                                "Make sure the average user will be able to understand the report."},
                        ],
                    }
                ],
                temperature=0.0,
            )
        else:  # no user description given
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Given someone with " + skintype + "skin." +
                            "Within 1000 characters with the title being Skincare Routine, "
                                "provide recommendations for a routine and products in bullet points. "
                                "Make sure the average user will be able to understand the report."},
                        ],
                    }
                ],
                temperature=0.0,
            )

        # Prints as markdown
        st.markdown(response.choices[0].message.content)

# Container with options to download and send report
if submitted:
    with st.container():
        st.write("Download routine as saved PDF.")

        if st.button(label="Generate Report"):
            try:
                pdf_bytes = io.BytesIO()
                c = canvas.Canvas(pdf_bytes, pagesize=letter)

                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, 770, "Skincare Routine")

                # Self-described symptoms
                c.drawString(50, 470, "Concerns:")
                y = 450
                for sym in concernList:
                    c.drawString(60, y, f"- {sym}")
                    y -= 15  # space between lines

                # Suggested Diagnosis Section
                c.drawString(50, y - 20, "Suggested Routine:")
                y -= 40

                response_text = response.choices[0].message.content.strip().split("\n")
                for paragraph in response_text:
                    if paragraph.strip():
                        y = render_markdown_to_pdf(c, paragraph.strip(), 60, y, max_width=480)
                        y -= 10  # spacing between paragraphs
                        if y < 60:
                            c.showPage()
                            y = 750

                # Save PDF
                c.save()
                pdf_bytes.seek(0)
                st.success("PDF generated successfully!")

                # Download button
                st.download_button(
                    label="Download",
                    data=pdf_bytes,
                    file_name="report.pdf",
                    mime="application/pdf",
                )

            except Exception as e:
                st.error(f"Error generating PDF: {e}")

    # Disclaimer
    st.markdown("**Disclaimer**")
    st.text(
        "Any content available via this website is for general informational purposes only and is not intended to be, and should not be treated as, substitute for professional medical advice, diagnosis or treatment. The content is provided on the understanding that no surgical or medical advice or recommendation is being rendered to you via the website. Medical treatment has to be individualised and can only be rendered after adequate assessment of your condition through appropriate clinical examination. Please do not disregard the professional medical advice of your physician or local healthcare provider or delay in seeking medical advice from them because of any information provided on the website."
    )