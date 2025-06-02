import streamlit as st
import numpy as np

st.set_page_config(page_title="BioKey DNA-Guided Encryption", layout="centered")
st.title("🔐 BioKey: DNA-Parametrized Chaotic Encryption")

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

# BioKey encryption
def bio_key_encrypt(dna_seq, plain_text, segment_length=100):
    encrypted = b''
    data_bytes = plain_text.encode('utf-8')

    for i in range(0, len(dna_seq), segment_length):
        segment = dna_seq[i:i + segment_length]
        if len(segment) < segment_length:
            break

        gc = gc_content(segment)
        system = select_chaotic_system(gc)
        numeric = dna_to_numeric(segment)
        seed = int(sum(numeric) * 1000) % 10000

        if system == 'Lorenz':
            chaotic_seq = lorenz(len(data_bytes), seed)
        elif system == 'Chen':
            chaotic_seq = chen(len(data_bytes), seed)
        else:
            chaotic_seq = rossler(len(data_bytes), seed)

        encrypted_segment = xor_encrypt(data_bytes, chaotic_seq)
        encrypted += encrypted_segment

    return encrypted

# Streamlit interface
st.subheader("Step 1: Enter DNA Sequence")
dna_input = st.text_area("Paste your DNA sequence (A, T, G, C only):", height=150)

st.subheader("Step 2: Enter Message to Encrypt")
message_input = st.text_input("Enter a short message:")

if st.button("🔐 Encrypt"):
    if not dna_input or not message_input:
        st.warning("Please enter both DNA sequence and message.")
    else:
        cipher = bio_key_encrypt(dna_input.strip().upper(), message_input)
        st.success("Encryption Complete!")
        st.code(cipher.hex(), language='text')

st.markdown("---")
st.caption("Developed using the BioKey hybrid encryption model.")
