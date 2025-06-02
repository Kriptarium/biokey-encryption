
import streamlit as st
import base64
import io
from PIL import Image

st.set_page_config(page_title="BioKey - Decryption Module", layout="wide")
st.title("🔓 BioKey: Decryption Module")

if 'dna_input' not in st.session_state or not st.session_state.dna_input:
    st.warning("DNA input not found. Please enter or select a DNA sequence in the main app.")
    st.stop()

from app import bio_key_decrypt

st.subheader("Select Decryption Mode")
decryption_mode = st.radio("Choose data type to decrypt:", ["Text", "Image"])

if decryption_mode == "Text":
    encrypted_hex = st.text_area("Paste the encrypted hex string:")
    if st.button("Decrypt Text"):
        try:
            encrypted_bytes = bytes.fromhex(encrypted_hex.strip())
            decrypted = bio_key_decrypt(st.session_state.dna_input.upper(), encrypted_bytes)
            st.success("Decryption successful!")
            st.code(decrypted.decode("utf-8", errors="replace"), language="text")
        except Exception as e:
            st.error(f"Decryption failed: {str(e)}")

elif decryption_mode == "Image":
    encrypted_file = st.file_uploader("Upload encrypted image data file (.bin)", type=["bin"])
    if encrypted_file:
        encrypted_bytes = encrypted_file.read()
        if st.button("Decrypt Image"):
            try:
                decrypted = bio_key_decrypt(st.session_state.dna_input.upper(), encrypted_bytes)
                img = Image.open(io.BytesIO(decrypted))
                st.image(img, caption="Decrypted Image", use_column_width=True)
                st.success("Image decrypted successfully.")
            except Exception as e:
                st.error(f"Image decryption failed: {str(e)}")
