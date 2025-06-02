import streamlit as st
import numpy as np
from PIL import Image
import io
import base64
import hashlib
import matplotlib.pyplot as plt

st.set_page_config(page_title="BioKey DNA-Guided Encryption", layout="wide")
st.title("🔐 BioKey: DNA-Parametrized Chaotic Encryption")

# Session state initialization
if 'dna_input' not in st.session_state:
    st.session_state.dna_input = ""
if 'last_encrypted' not in st.session_state:
    st.session_state.last_encrypted = b''
if 'system_usage' not in st.session_state:
    st.session_state.system_usage = []
if 'last_seed_trace' not in st.session_state:
    st.session_state.last_seed_trace = []

# DNA and chaos helpers
DNA_MAP = {'A': 0.1, 'T': 0.2, 'G': 0.3, 'C': 0.4}
def lorenz(n, seed): np.random.seed(seed); return np.random.rand(n)
def chen(n, seed): np.random.seed(seed+1); return np.random.rand(n)
def rossler(n, seed): np.random.seed(seed+2); return np.random.rand(n)
def gc_content(seq): return (seq.count('G') + seq.count('C')) / len(seq)
def dna_to_numeric(segment): return [DNA_MAP.get(base, 0.0) for base in segment]
def select_chaotic_system(gc):
    return 'Chen' if gc < 0.4 else 'Lorenz' if gc <= 0.6 else 'Rossler'
def xor_encrypt(data_bytes, key_seq): return bytes([b ^ int(k * 255) for b, k in zip(data_bytes, key_seq)])

# Core functions
def bio_key_encrypt(dna_seq, data_bytes, segment_length=100):
    encrypted = b''; st.session_state.system_usage = []; st.session_state.last_seed_trace = []
    for i in range(0, len(dna_seq), segment_length):
        segment = dna_seq[i:i+segment_length]
        if len(segment) < segment_length: break
        gc = gc_content(segment)
        system = select_chaotic_system(gc)
        st.session_state.system_usage.append(system)
        numeric = dna_to_numeric(segment)
        seed = int(sum(numeric) * 1000) % 10000
        st.session_state.last_seed_trace.append((system, seed))
        chaos = lorenz if system == 'Lorenz' else chen if system == 'Chen' else rossler
        key_seq = chaos(len(data_bytes), seed)
        encrypted += xor_encrypt(data_bytes, key_seq)
    return encrypted

def compute_sha256(data): return hashlib.sha256(data).hexdigest()
def calculate_entropy(data):
    prob = [data.count(byte)/len(data) for byte in set(data)]
    return round(-sum([p * np.log2(p) for p in prob]), 4)

# Sidebar
st.sidebar.header("📥 DNA Sequence")
choice = st.sidebar.radio("Input Type", ["Manual", "Example Dataset"])
if choice == "Manual":
    dna_seq = st.sidebar.text_area("Enter DNA sequence (A,T,G,C only):", height=150)
else:
    example_choice = st.sidebar.selectbox("Choose example dataset", ["Example BRCA1", "Example TP53", "Synthetic Sample"])
    example_sequences = {
        "Example BRCA1": "ATGGATTTGGAAGTTGCCAGTTTGCTGGCATTTCTGTTTGTCAGCTTTGGAAGGACAGAGGATTTTG",
        "Example TP53": "AGGCGTGTTTGTGCCTGTCCTGGGAGAGACCGGCGCACAGAGGAAGAGAATCTCCGCAAGAAAGGG",
        "Synthetic Sample": "ATCGATCGGATCGATGCTAGCTAGCATCGATCGTACGTAGCTAGCTGACTGACTGACTGATCGA"
    }
    dna_seq = example_sequences[example_choice]
    st.sidebar.code(dna_seq, language="text")

st.session_state.dna_input = dna_seq if 'dna_seq' in locals() and dna_seq.strip() else st.session_state.get('dna_input', "")

# Encryption Mode
st.subheader("🔐 Select Encryption Mode")
mode = st.radio("Choose data type to encrypt:", ["Text", "Image"])

if mode == "Text":
    msg = st.text_input("Enter your message:")
    if st.button("Encrypt Text"):
        encrypted = bio_key_encrypt(st.session_state.dna_input.upper(), msg.encode('utf-8'))
        st.session_state.last_encrypted = encrypted
        st.code(encrypted.hex())
        st.success("Text encrypted.")
        st.text(f"SHA256: {compute_sha256(encrypted)}")
        st.text(f"Entropy: {calculate_entropy(list(encrypted))}")
        st.download_button("Download Encrypted Text", encrypted.hex(), file_name="ciphertext.txt")

elif mode == "Image":
    image_file = st.file_uploader("Upload image file (.jpg/.png)", type=["jpg", "png"])
    if image_file:
        img = Image.open(image_file)
        img_bytes = io.BytesIO(); img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()
        if st.button("Encrypt Image"):
            encrypted = bio_key_encrypt(st.session_state.dna_input.upper(), img_data)
            st.session_state.last_encrypted = encrypted
            st.code(base64.b64encode(encrypted).decode('utf-8')[:300] + "...")
            st.success("Image encrypted.")
            st.text(f"SHA256: {compute_sha256(encrypted)}")
            st.text(f"Entropy: {calculate_entropy(list(encrypted))}")
            st.download_button("Download Encrypted Image Data", encrypted, file_name="encrypted_image.bin")

# Charts and Analysis
st.markdown("---")
st.subheader("📊 System Usage Analysis")

if st.session_state.system_usage:
    # Pie Chart
    system_counts = Counter(st.session_state.system_usage)
    fig1, ax1 = plt.subplots()
    ax1.pie(system_counts.values(), labels=system_counts.keys(), autopct='%1.1f%%')
    st.pyplot(fig1)

    # GC Distribution
    st.subheader("🧬 GC Content per Segment")
    gc_list = [gc_content(st.session_state.dna_input[i:i+100]) for i in range(0, len(st.session_state.dna_input)-99, 100)]
    fig2, ax2 = plt.subplots()
    ax2.plot(gc_list)
    ax2.set_xlabel("Segment Index")
    ax2.set_ylabel("GC Content")
    st.pyplot(fig2)

    # Seed trace
    st.subheader("🔑 System and Seed Trace")
    st.table(st.session_state.last_seed_trace)

# Navigation
st.markdown("### 🧭 Navigation")
st.markdown("[📊 Go to Analysis Module](pages/analysis_module.py)", unsafe_allow_html=True)
st.markdown("[🔓 Go to Decryption Module](pages/decryption_module.py)", unsafe_allow_html=True)