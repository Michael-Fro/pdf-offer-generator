import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
from PIL import Image
import tempfile
import os

def extract_keywords(text):
    text = text.lower()
    keywords = {
        "door_1": "1pildins.jpg" if "1-pane" in text or "1 pildi" in text else None,
        "door_2": "2pildini.jpeg" if "2-pane" in text or "2 pildi" in text else None,
        "cross_section": "scandi_uzbuve.jpeg" if "durvis" in text else None,
    }
    return {k: v for k, v in keywords.items() if v is not None}

def add_image_page(pdf, image_path):
    img = Image.open(image_path)
    img_w, img_h = img.size
    page_w, page_h = 210, 297
    dpi = 96
    img_w_mm = img_w * 25.4 / dpi
    img_h_mm = img_h * 25.4 / dpi
    scale = min(page_w / img_w_mm, page_h / img_h_mm)
    display_w = img_w_mm * scale
    display_h = img_h_mm * scale
    x = (page_w - display_w) / 2
    y = (page_h - display_h) / 2
    pdf.add_page()
    pdf.image(image_path, x=x, y=y, w=display_w, h=display_h)

def add_pdf_content(pdf, pdf_path):
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        pdf.add_page()
        text = page.extract_text()
        if text:
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text)

def main():
    st.title("Automātiska PDF piedāvājuma ģenerēšana")

    offer_pdf = st.file_uploader("Augšupielādē piedāvājuma PDF", type="pdf")
    title_page = st.file_uploader("Titullapa (PDF)", type="pdf")
    end_page = st.file_uploader("Beigu lapa (PDF)", type="pdf")

    images = {}
    for label in ["1pildins.jpg", "2pildini.jpeg", "scandi_uzbuve.jpeg"]:
        images[label] = st.file_uploader(f"Attēls: {label}", type=["jpg", "jpeg", "png"], key=label)

    if st.button("Ģenerēt piedāvājumu") and offer_pdf and title_page and end_page:
        with tempfile.TemporaryDirectory() as tmpdir:
            offer_path = os.path.join(tmpdir, "offer.pdf")
            title_path = os.path.join(tmpdir, "title.pdf")
            end_path = os.path.join(tmpdir, "end.pdf")
            with open(offer_path, "wb") as f: f.write(offer_pdf.read())
            with open(title_path, "wb") as f: f.write(title_page.read())
            with open(end_path, "wb") as f: f.write(end_page.read())

            reader = PdfReader(offer_path)
            full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            detected = extract_keywords(full_text)

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            add_pdf_content(pdf, title_path)
            add_pdf_content(pdf, offer_path)

            for key, img_name in detected.items():
                if images.get(img_name):
                    img_path = os.path.join(tmpdir, img_name)
                    with open(img_path, "wb") as f: f.write(images[img_name].read())
                    add_image_page(pdf, img_path)

            add_pdf_content(pdf, end_path)

            output_path = os.path.join(tmpdir, "output.pdf")
            pdf.output(output_path)

            with open(output_path, "rb") as f:
                st.download_button("Lejupielādēt ģenerēto PDF", f, file_name="piedavajums.pdf")

if __name__ == "__main__":
    main()
