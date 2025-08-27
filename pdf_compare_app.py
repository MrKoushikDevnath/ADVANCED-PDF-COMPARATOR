import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageChops
import io
import hashlib

# ------------------ Helper Functions ------------------

def hash_pdf(file):
    file.seek(0)
    data = file.read()
    file.seek(0)
    return hashlib.md5(data).hexdigest()

def pdf_to_images(pdf_file, zoom=2):
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))  # higher resolution
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def add_styles():
    st.markdown("""
    <style>
      /* Import a clean, modern font */
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;900&display=swap');

      html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      }

      /* Animated gradient background */
      [data-testid="stAppViewContainer"] {
        background: linear-gradient(120deg, #f8fbff, #eef8ff, #f9f9ff);
        background-size: 300% 300%;
        animation: gradientShift 18s ease infinite;
      }
      @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }

      /* Title styling */
      .title-hero {
        font-weight: 900;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: .25rem;
        text-shadow: 0 2px 10px rgba(0,0,0,.06);
      }
      .subtitle {
        color: #5e6b7a;
        font-weight: 500;
        margin-bottom: 1.25rem;
      }

      /* Card pulse for each page section */
      @keyframes softPulse {
        0%   { box-shadow: 0 12px 30px rgba(0,0,0,.06); }
        50%  { box-shadow: 0 18px 40px rgba(0,0,0,.10); }
        100% { box-shadow: 0 12px 30px rgba(0,0,0,.06); }
      }
      .card {
        border-radius: 18px;
        padding: 14px;
        background: #ffffffcc;
        backdrop-filter: blur(6px);
        border: 1px solid rgba(0,0,0,.05);
        animation: softPulse 3.6s ease-in-out infinite;
      }

      /* Pretty section headers */
      .section-title {
        font-weight: 800;
        font-size: 1.05rem;
        margin: 6px 0 12px 0;
      }
      .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .02em;
        background: #eef6ff;
        color: #2a6df0;
        border: 1px solid #dbe9ff;
        vertical-align: middle;
        margin-left: 8px;
      }

      /* Image wrappers */
      .img-card {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(0,0,0,.06);
      }
      .caption {
        text-align: center;
        font-size: .86rem;
        color: #4c5561;
        margin-top: 6px;
        font-weight: 600;
      }
    </style>
    """, unsafe_allow_html=True)

# ------------------ Streamlit UI ------------------

st.set_page_config(page_title="Advanced PDF Comparator", layout="wide")
add_styles()

st.markdown('<h1 class="title-hero">Advanced PDF Comparator</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visual-only comparison</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    pdf_file1 = st.file_uploader("Upload first PDF", type='pdf', key="pdf1")
with col2:
    pdf_file2 = st.file_uploader("Upload second PDF", type='pdf', key="pdf2")

if pdf_file1 and pdf_file2:
    hash1 = hash_pdf(pdf_file1)
    hash2 = hash_pdf(pdf_file2)

    if hash1 == hash2:
        st.success("The PDFs are identical.")
    else:
        st.warning("Differences detected. Visual comparison below.")

        # Convert both PDFs to images
        images1 = pdf_to_images(pdf_file1, zoom=2)
        images2 = pdf_to_images(pdf_file2, zoom=2)

        max_pages = max(len(images1), len(images2))

        for i in range(max_pages):
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">Page {i+1} '
                f'<span class="badge">Visual Compare</span></div>',
                unsafe_allow_html=True
            )

            img1 = images1[i] if i < len(images1) else Image.new('RGB', images2[0].size, color='white')
            img2 = images2[i] if i < len(images2) else Image.new('RGB', images1[0].size, color='white')

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="img-card">', unsafe_allow_html=True)
                st.image(img1, caption=None, use_container_width=True)
                st.markdown('</div><div class="caption">PDF 1 — Page {}</div>'.format(i+1), unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="img-card">', unsafe_allow_html=True)
                st.image(img2, caption=None, use_container_width=True)
                st.markdown('</div><div class="caption">PDF 2 — Page {}</div>'.format(i+1), unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        st.success("Visual comparison complete.")
else:
    st.info("Upload two PDFs to begin.")