import streamlit as st
import numpy as np
from Bio import Entrez
import matplotlib.pyplot as plt
import io
import base64
import hashlib
from collections import Counter
import time

st.set_page_config(page_title="BioKey DNA-Guided Encryption", layout="wide")
st.title("🔐 BioKey: DNA-Parametrized Chaotic Encryption")

# Update: Use valid institutional email to avoid HTTPError
Entrez.email = "your.name@university.edu"

if 'dna_input' not in st.session_state:
    st.session_state.dna_input = ""
if 'last_encrypted' not in st.session_state:
    st.session_state.last_encrypted = b''
if 'system_usage' not in st.session_state:
    st.session_state.system_usage = []
if 'last_seed_trace' not in st.session_state:
    st.session_state.last_seed_trace = []

DNA_MAP = {'A': 0.1, 'T': 0.2, 'G': 0.3, 'C': 0.4}

# Mock chaotic systems (dummy randomness for now)
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

def bio_key_encrypt(dna_seq, plain_text, segment_length=100):
    encrypted = b''
    data_bytes = plain_text.encode('utf-8')
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

def bio_key_decrypt(dna_seq, encrypted_bytes, segment_length=100):
    decrypted = b''
    data_len = len(encrypted_bytes)
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
            chaotic_seq = lorenz(data_len, seed)
        elif system == 'Chen':
            chaotic_seq = chen(data_len, seed)
        else:
            chaotic_seq = rossler(data_len, seed)

        decrypted_segment = xor_encrypt(encrypted_bytes, chaotic_seq)
        decrypted += decrypted_segment

    return decrypted

def compute_sha256(data):
    return hashlib.sha256(data).hexdigest()

def calculate_entropy(data):
    prob = [data.count(byte)/len(data) for byte in set(data)]
    entropy = -sum([p * np.log2(p) for p in prob])
    return round(entropy, 4)

def calculate_npcr(original, modified):
    if len(original) != len(modified):
        return 0.0
    changes = sum([1 for a, b in zip(original, modified) if a != b])
    return round(changes / len(original) * 100, 2)

st.sidebar.header("📥 DNA Sequence")
choice = st.sidebar.radio("Input Type", ["Manual", "Fetch from NCBI"])

if choice == "Manual":
    dna_seq = st.sidebar.text_area("Enter DNA sequence (A,T,G,C only):", height=150)
else:
    gene = st.sidebar.text_input("Gene Name (e.g. BRCA1)")
    ids = []
    if st.sidebar.button("Search NCBI"):
        try:
            time.sleep(0.34)
            handle = Entrez.esearch(db="nucleotide", term=gene + "[Gene Name] AND Homo sapiens[Organism]", retmax=5)
            record = Entrez.read(handle)
            ids = record['IdList']
        except Exception as e:
            st.error(f"NCBI query failed: {str(e)}")
    if ids:
        selected_id = st.sidebar.selectbox("Select sequence", ids)
        if selected_id:
            try:
                time.sleep(0.34)
                fetch = Entrez.efetch(db="nucleotide", id=selected_id, rettype="fasta", retmode="text")
                fasta = fetch.read()
                seq_lines = fasta.split('\n')[1:]
                dna_seq = ''.join(seq_lines)
                st.sidebar.success("Sequence loaded.")
                st.session_state.dna_input = dna_seq
            except Exception as e:
                st.error(f"NCBI fetch failed: {str(e)}")

st.session_state.dna_input = dna_seq if 'dna_seq' in locals() else st.session_state.dna_input

st.subheader("🔐 Encrypt Message")
plain_text = st.text_input("Enter your message:")

if st.button("Encrypt"):
    encrypted = bio_key_encrypt(st.session_state.dna_input.upper(), plain_text)
    st.session_state.last_encrypted = encrypted
    st.code(encrypted.hex(), language="text")
    st.success("Message encrypted.")
    st.text(f"SHA256: {compute_sha256(encrypted)}")
    st.text(f"Entropy: {calculate_entropy(list(encrypted))}")
    st.download_button("📥 Download Ciphertext (hex)", encrypted.hex(), file_name="ciphertext.txt")

    systems = st.session_state.system_usage
    system_counts = Counter(systems)
    fig1, ax1 = plt.subplots()
    ax1.pie(system_counts.values(), labels=system_counts.keys(), autopct='%1.1f%%')
    st.pyplot(fig1)

    segments = [st.session_state.dna_input[i:i + 100] for i in range(0, len(st.session_state.dna_input), 100)]
    gc_values = [gc_content(seg) for seg in segments if len(seg) == 100]
    fig2, ax2 = plt.subplots()
    ax2.plot(gc_values, marker='o')
    ax2.set_title("GC Content per Segment")
    st.pyplot(fig2)

st.subheader("🧪 NPCR Test")
col1, col2 = st.columns(2)
with col1:
    original_dna = st.text_area("🔹 Original DNA Sequence", value=st.session_state.dna_input, height=120)
with col2:
    modified_dna = st.text_area("🔸 Modified DNA Sequence", height=120)

if st.button("▶️ Run NPCR Test"):
    if not original_dna or not modified_dna:
        st.warning("Please enter both original and modified DNA sequences.")
    else:
        enc1 = bio_key_encrypt(original_dna.strip().upper(), "test")
        enc2 = bio_key_encrypt(modified_dna.strip().upper(), "test")
        npcr = calculate_npcr(enc1, enc2)
        st.success(f"📊 NPCR: {npcr}%")
        st.progress(npcr / 100)
        st.markdown(">
        **What is NPCR?** Measures how much the encrypted output changes when a small change is made to input. High NPCR = better diffusion and stronger encryption.")

st.subheader("🔓 Decrypt Message")
hex_input = st.text_area("Enter ciphertext in hex:")
if st.button("Decrypt"):
    try:
        decrypted = bio_key_decrypt(st.session_state.dna_input.upper(), bytes.fromhex(hex_input))
        st.code(decrypted.decode(), language="text")
    except:
        st.error("Invalid ciphertext or DNA mismatch.")
