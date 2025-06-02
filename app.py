
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import hashlib
from collections import Counter
import time
from PIL import Image

st.set_page_config(page_title="BioKey DNA-Guided Encryption", layout="wide")
st.title("🔐 BioKey: DNA-Parametrized Chaotic Encryption")

if 'dna_input' not in st.session_state:
    st.session_state.dna_input = ""
if 'last_encrypted' not in st.session_state:
    st.session_state.last_encrypted = b''
if 'system_usage' not in st.session_state:
    st.session_state.system_usage = []
if 'last_seed_trace' not in st.session_state:
    st.session_state.last_seed_trace = []

DNA_MAP = {'A': 0.1, 'T': 0.2, 'G': 0.3, 'C': 0.4}

def lorenz(n, seed):
    np.random.seed(seed)
    return np.random.rand(n)

def chen(n, seed):
    np.random.seed(seed + 1)
    return np.random.rand(n)

def rossler(n, seed):
    np.random.seed(seed + 2)
    return np.random.rand(n)

def gc_content(segment):
    gc = segment.count('G') + segment.count('C')
    return gc / len(segment)

def dna_to_numeric(segment):
    return [DNA_MAP.get(base, 0.0) for base in segment]

def select_chaotic_system(gc):
    if gc < 0.4:
        return 'Chen'
    elif gc <= 0.6:
        return 'Lorenz'
    else:
        return 'Rossler'

def xor_encrypt(data_bytes, key_sequence):
    return bytes([b ^ int(k * 255) for b, k in zip(data_bytes, key_sequence)])

def bio_key_encrypt(dna_seq, data_bytes, segment_length=100):
    encrypted = b''
    st.session_state.system_usage = []
    st.session_state.last_seed_trace = []

    for i in range(0, len(dna_seq), segment_length):
        segment = dna_seq[i:i + segment_length]
        if len(segment) < segment_length:
            break
        gc = gc_content(segment)
        system = select_chaotic_system(gc)
        st.session_state.system_usage.append(system)
        numeric = dna_to_numeric(segment)
        seed = int(sum(numeric) * 1000) % 10000
        st.session_state.last_seed_trace.append((system, seed))

        if system == 'Lorenz':
            chaotic_seq = lorenz(len(data_bytes), seed)
        elif system == 'Chen':
            chaotic_seq = chen(len(data_bytes), seed)
        else:
            chaotic_seq = rossler(len(data_bytes), seed)

        encrypted_segment = xor_encrypt(data_bytes, chaotic_seq)
        encrypted += encrypted_segment

    return encrypted

def compute_sha256(data):
    return hashlib.sha256(data).hexdigest()

def calculate_entropy(data):
    prob = [data.count(byte)/len(data) for byte in set(data)]
    entropy = -sum([p * np.log2(p) for p in prob])
    return round(entropy, 4)

st.sidebar.header("📥 DNA Sequence")
choice = st.sidebar.radio("Input Type", ["Manual", "Select Example Dataset"])

example_datasets = {
    "Example BRCA1": "ATGGATTTTGGGAAGTTGGAAGGTTTTCCTAGGTTTTCCCTGGAATTCGATCTCCTGGTGGTGGTTGTTTTTGGTGGGTG",
    "Example TP53": "AGCGTGGTGGTACCTTATGGCGGGAGGAGACCGGCGCACAGAGGAAGAGAATCTCCGCAAGAAAGGGCCAGCCTCTGGAAG",
    "Synthetic Sample": "GCGCGCGCGCATATATATATATGCGCGCGCGCGCGCTATATATATATATCGCGCGCGCGCATATATATATATATATATATA"
}

dna_seq = ""
if choice == "Manual":
    dna_seq = st.sidebar.text_area("Enter DNA sequence (A,T,G,C only):", height=150)
elif choice == "Select Example Dataset":
    selected_example = st.sidebar.selectbox("Choose an example DNA sequence:", list(example_datasets.keys()))
    dna_seq = example_datasets[selected_example]
    st.sidebar.code(dna_seq)
    st.sidebar.success("Example DNA sequence loaded.")

st.session_state.dna_input = dna_seq if dna_seq.strip() else st.session_state.get('dna_input', example_datasets["Example BRCA1"])

st.subheader("🔐 Encrypt Text Message")
plain_text = st.text_input("Enter your message:")

if st.button("Encrypt Text"):
    encrypted = bio_key_encrypt(st.session_state.dna_input.upper(), plain_text.encode())
    st.session_state.last_encrypted = encrypted
    st.code(encrypted.hex(), language="text")
    st.success("Message encrypted.")
    st.text(f"SHA256: {compute_sha256(encrypted)}")
    st.text(f"Entropy: {calculate_entropy(list(encrypted))}")
    st.download_button("📥 Download Ciphertext (hex)", encrypted.hex(), file_name="ciphertext.txt")

st.subheader("🖼️ Encrypt Image")
image_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg"])

if image_file:
    img = Image.open(image_file)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_data = img_bytes.getvalue()

    if st.button("Encrypt Image"):
        encrypted = bio_key_encrypt(st.session_state.dna_input.upper(), img_data)
        st.session_state.last_encrypted = encrypted
        st.success("Image encrypted successfully.")
        st.text(f"SHA256: {compute_sha256(encrypted)}")
        st.text(f"Entropy: {calculate_entropy(list(encrypted))}")
        st.download_button("📥 Download Encrypted Image", encrypted, file_name="encrypted_image.bin")
