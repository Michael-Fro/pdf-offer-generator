import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image
import fitz  # PyMuPDF
import tempfile
import os
import img2pdf

def extract_keywords(text):
    text = text.lower()
    keywords = {
        "door_1": "1pildins.jpg" if "1-pane" in text or "1 pildi" in text else None,
        "door_2": "2pildini.jpeg" if "2-pane" in text or "2 pildi" in text else None,
        "cross_section": "scandi_uzbuve.jpeg" if "durvis" in text else None,
    }
    return {k: v for k, v in keywords.items() if v is not None}

def convert_pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    image_paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        tmp_img_path = tempfile.mktemp(suffix=".jpg")
        pix.save(tmp_img_path)
        image_paths.append(tmp_img_path)
    doc.close()
    return image_paths

def resize_image(image_path, max_width=1000):
    img = Image.open(image_path)
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.ANTIALIAS)
        resized_path = tempfile.mktemp(suffix=".jpg")
        img.save(resized_path, format="JPEG")
        return resized_path
    return image_path

def main():
    st.title("Automātiska PDF piedāvājuma ģenerēšana")

    offer_pdf = st.file_uploader("Augšupielādē piedāvājuma PDF", type="pdf")

    if st.button("Ģenerēt piedāvājumu") and offer_pdf:
        with tempfile.TemporaryDirectory() as tmpdir:
            offer_path = os.path.join(tmpdir, "offer.pdf")
            with open(offer_path, "wb") as f:
                f.write(offer_pdf.read())

            reader = PdfReader(offer_path)
            full_text = "
".join(page.extract_text() or "" for page in reader.pages)
            detected = extract_keywords(full_text)

            all_images = []
            all_images.extend(convert_pdf_to_images("static/title.pdf"))
            all_images.extend(convert_pdf_to_images(offer_path))

            for key, img_name in detected.items():
                img_path = os.path.join("images", img_name)
                if os.path.exists(img_path):
                    all_images.append(img_path)

            all_images.extend(convert_pdf_to_images("static/end.pdf"))

            resized_images = [resize_image(img) for img in all_images]

            output_path = os.path.join(tmpdir, "output.pdf")
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(resized_images))

            with open(output_path, "rb") as f:
                st.download_button("Lejupielādēt ģenerēto PDF", f, file_name="piedavajums.pdf")
