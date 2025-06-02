import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
import cv2

def calculate_npcr(img1, img2):
    img1 = np.array(img1)
    img2 = np.array(img2)
    diff = np.not_equal(img1, img2)
    return np.sum(diff) / diff.size * 100

def calculate_uaci(img1, img2):
    img1 = np.array(img1).astype(np.float32)
    img2 = np.array(img2).astype(np.float32)
    diff = np.abs(img1 - img2)
    return np.mean(diff) / 255 * 100

def calculate_correlation(img1, img2):
    img1 = np.array(img1).flatten()
    img2 = np.array(img2).flatten()
    return np.corrcoef(img1, img2)[0, 1]

def calculate_ssim_index(img1, img2):
    img1_gray = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
    img2_gray = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)
    score, _ = ssim(img1_gray, img2_gray, full=True)
    return score

def plot_histograms(img1, img2):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    axs[0].hist(np.array(img1).flatten(), bins=256, color='blue', alpha=0.7)
    axs[0].set_title("Original Image Histogram")
    axs[1].hist(np.array(img2).flatten(), bins=256, color='red', alpha=0.7)
    axs[1].set_title("Encrypted Image Histogram")
    return fig

st.set_page_config(page_title="🔍 Encrypted Image Analysis", layout="wide")
st.title("🧪 Image Encryption Metrics")

uploaded_original = st.file_uploader("Upload original image", type=["png", "jpg", "jpeg"])
uploaded_encrypted = st.file_uploader("Upload encrypted image", type=["png", "jpg", "jpeg"])

if uploaded_original and uploaded_encrypted:
    original = Image.open(uploaded_original).convert("RGB")
    encrypted = Image.open(uploaded_encrypted).convert("RGB")

    col1, col2 = st.columns(2)
    with col1:
        st.image(original, caption="Original Image", use_column_width=True)
    with col2:
        st.image(encrypted, caption="Encrypted Image", use_column_width=True)

    st.markdown("---")
    st.subheader("📊 Metric Results")
    npcr_val = calculate_npcr(original, encrypted)
    uaci_val = calculate_uaci(original, encrypted)
    corr_val = calculate_correlation(original, encrypted)
    ssim_val = calculate_ssim_index(original, encrypted)

    st.write(f"**NPCR:** {npcr_val:.2f}%")
    st.write(f"**UACI:** {uaci_val:.2f}%")
    st.write(f"**Pearson Correlation:** {corr_val:.4f}")
    st.write(f"**SSIM:** {ssim_val:.4f}")

    st.subheader("📈 Histogram Comparison")
    hist_fig = plot_histograms(original, encrypted)
    st.pyplot(hist_fig)
