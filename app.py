import streamlit as st
import numpy as np
from Bio import Entrez
import matplotlib.pyplot as plt
import io
import base64
import hashlib
from collections import Counter

st.set_page_config(page_title="BioKey DNA-Guided Encryption", layout="centered")
st.title("🔐 BioKey: DNA-Parametrized Chaotic Encryption")

# Email for NCBI access
Entrez.email = "example@domain.com"  # Replace with a real email

# Session state init
if 'dna_input' not in st.session_state:
    st.session_state.dna_input = ""
if 'last_encrypted' not in st.session_state:
    st.session_state.last_encrypted = b''
if 'system_usage' not in st.session_state:
    st.session_state.system_usage = []
if 'last_seed_trace' not in st.session_state:
    st.session_state.last_seed_trace = []

# DNA to value map
DNA_MAP = {'A': 0.1, 'T': 0.2, 'G': 0.3, 'C': 0.4}

# Mock chaotic systems
def lorenz(n, seed):
    np.random.seed(seed)
    return np.random.rand(n)

def chen(n, seed):
    np.random.seed(seed + 1)
    return np.random.rand(n)

def rossler(n, seed):
    np.random.seed(seed + 2)
    return np.random.rand(n)

# GC content calculator
def gc_content(segment):
    gc = segment.count('G') + segment.count('C')
    return gc / len(segment)

# DNA to numeric
def dna_to_numeric(segment):
    return [DNA_MAP.get(base, 0.0) for base in segment]

# Chaotic system selection
def select_chaotic_system(gc):
    if gc < 0.4:
        return 'Chen'
    elif gc <= 0.6:
        return 'Lorenz'
    else:
        return 'Rossler'

# XOR encryption
def xor_encrypt(data_bytes, key_sequence):
    return bytes([b ^ int(k * 255) for b, k in zip(data_bytes, key_sequence)])

# BioKey encryption with tracking
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

# Decryption
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

# Utility: SHA256 checksum
def compute_sha256(data):
    return hashlib.sha256(data).hexdigest()

# Utility: Entropy calculation
def calculate_entropy(data):
    prob = [data.count(byte)/len(data) for byte in set(data)]
    entropy = -sum([p * np.log2(p) for p in prob])
    return round(entropy, 4)

# Utility: NPCR (for binary data)
def calculate_npcr(original, modified):
    if len(original) != len(modified):
        return 0.0
    changes = sum([1 for a, b in zip(original, modified) if a != b])
    return round(changes / len(original) * 100, 2)

# Improved NPCR Test UI
st.subheader("🧪 NPCR (Number of Pixels Change Rate) Test")

st.markdown("""
Compare how much the encryption output changes when a small mutation is applied to the DNA sequence.
This simulates cryptographic diffusion performance.
""")

col1, col2 = st.columns(2)

with col1:
    original_dna = st.text_area("🔹 Original DNA Sequence", value=st.session_state.dna_input, height=120)

with col2:
    modified_dna = st.text_area("🔸 Slightly Modified DNA Sequence", height=120)

if st.button("▶️ Run NPCR Test"):
    if not original_dna or not modified_dna:
        st.warning("Please enter both original and modified DNA sequences.")
    else:
        encrypted_orig = bio_key_encrypt(original_dna.strip().upper(), "testmsg")
        encrypted_mod = bio_key_encrypt(modified_dna.strip().upper(), "testmsg")
        npcr = calculate_npcr(encrypted_orig, encrypted_mod)

        st.success(f"📊 NPCR: `{npcr}%` difference between ciphertexts")
        st.progress(npcr / 100)

        st.markdown("""
        > **What is NPCR?**  
        > NPCR (Number of Pixels Change Rate) is a metric adapted from image encryption to DNA-based cryptography.  
        > It measures the percentage of different bits in two ciphertexts produced by slightly different inputs.  
        > A high NPCR indicates strong diffusion — a small change in the input leads to large change in the output.
        """)
