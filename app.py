import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import hashlib
from collections import Counter
from PIL import Image
import time

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

def lorenz(n, seed): np.random.seed(seed); return np.random.rand(n)
def chen(n, seed): np.random.seed(seed + 1); return np.random.rand(n)
def rossler(n, seed): np.random.seed(seed + 2); return np.random.rand(n)

def gc_content(segment): gc = segment.count('G') + segment.count('C'); return gc / len(segment)
def dna_to_numeric(segment): return [DNA_MAP.get(base, 0.0) for base in segment]
def select_chaotic_system(gc): return 'Chen' if gc < 0.4 else 'Lorenz' if gc <= 0.6 else 'Rossler'
def xor_encrypt(data_bytes, key_sequence): return bytes([b ^ int(k * 255) for b, k in zip(data_bytes, key_sequence)])

def compute_sha256(data): return hashlib.sha256(data).hexdigest()
def calculate_entropy(data): prob = [data.count(byte)/len(data) for byte in set(data)]; return round(-sum([p * np.log2(p) for p in prob]), 4)
def calculate_npcr(original, modified): return round(sum([1 for a, b in zip(original, modified) if a != b]) / len(original) * 100, 2) if len(original) == len(modified) else 0.0

example_datasets = {
    "Example BRCA1": "ATGGATTTTGGGAAGTTGGAAGGTTTTCCTAGGTTTTCCCTGGAATTCGATCTCCTGGTGGTGGTTGTTTTTGGTGGGTG",
    "Example TP53": "AGCGTGGTGGTACCTTATGGCGGGAGGAGACCGGCGCACAGAGGAAGAGAATCTCCGCAAGAAAGGGCCAGCCTCTGGAAG",
    "Synthetic Sample": "GCGCGCGCGCATATATATATATGCGCGCGCGCGCGCTATATATATATATCGCGCGCGCGCATATATATATATATATATATA"
}

st.sidebar.header("📥 DNA Sequence")
choice = st.sidebar.radio("Input Type", ["Manual", "Select Example Dataset"])
dna_seq = st.sidebar.text_area("Enter DNA sequence:", height=150) if choice == "Manual" else example_datasets[st.sidebar.selectbox("Choose example", list(example_datasets.keys()))]
st.session_state.dna_input = dna_seq.upper()

st.subheader("🔐 Encrypt Text")
text = st.text_input("Enter text to encrypt:")
if st.button("Encrypt Text"):
    data_bytes = text.encode()
    encrypted = b''
    for i in range(0, len(dna_seq), 100):
        seg = dna_seq[i:i+100]
        if len(seg) < 100: break
        gc = gc_content(seg)
        system = select_chaotic_system(gc)
        st.session_state.system_usage.append(system)
        seed = int(sum(dna_to_numeric(seg)) * 1000) % 10000
        chaotic = {'Lorenz': lorenz, 'Chen': chen, 'Rossler': rossler}[system](len(data_bytes), seed)
        encrypted += xor_encrypt(data_bytes, chaotic)
    st.session_state.last_encrypted = encrypted
    st.code(encrypted.hex())
    st.text(f"SHA256: {compute_sha256(encrypted)}")
    st.text(f"Entropy: {calculate_entropy(list(encrypted))}")
    st.download_button("📥 Download", encrypted.hex(), file_name="cipher.txt")

    fig1, ax1 = plt.subplots()
    counts = Counter(st.session_state.system_usage)
    ax1.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%')
    ax1.set_title("Chaotic System Usage")
    st.pyplot(fig1)

    gc_vals = [gc_content(dna_seq[i:i+100]) for i in range(0, len(dna_seq), 100) if len(dna_seq[i:i+100]) == 100]
    fig2, ax2 = plt.subplots()
    ax2.plot(gc_vals, marker='o')
    ax2.set_title("GC Content")
    st.pyplot(fig2)

st.subheader("🖼 Encrypt Image")
img_file = st.file_uploader("Upload image", type=["jpg", "png"])
if img_file:
    img = Image.open(img_file)
    buf = io.BytesIO(); img.save(buf, format='PNG'); img_bytes = buf.getvalue()
    if st.button("Encrypt Image"):
        encrypted_img = b''
        for i in range(0, len(dna_seq), 100):
            seg = dna_seq[i:i+100]
            if len(seg) < 100: break
            gc = gc_content(seg)
            system = select_chaotic_system(gc)
            seed = int(sum(dna_to_numeric(seg)) * 1000) % 10000
            chaotic = {'Lorenz': lorenz, 'Chen': chen, 'Rossler': rossler}[system](len(img_bytes), seed)
            encrypted_img += xor_encrypt(img_bytes, chaotic)
        st.image(img, caption="Original")
        st.download_button("Download Encrypted Image", encrypted_img, file_name="enc_image.bin")
        st.code(base64.b64encode(encrypted_img).decode()[:200] + "...")