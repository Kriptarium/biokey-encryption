
import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

st.set_page_config(page_title="BioKey - Analysis Module", layout="wide")
st.title("📊 BioKey: Encryption Analysis Module")

if 'last_encrypted' not in st.session_state or not st.session_state.last_encrypted:
    st.warning("No encrypted data found. Please run encryption first.")
    st.stop()

if 'system_usage' not in st.session_state or not st.session_state.system_usage:
    st.warning("No system usage data found. Please run encryption first.")
    st.stop()

if 'last_seed_trace' not in st.session_state:
    st.session_state.last_seed_trace = []

# 1. System usage chart
st.subheader("🧠 Chaotic System Usage Distribution")
system_counts = Counter(st.session_state.system_usage)
labels = list(system_counts.keys())
values = list(system_counts.values())

fig1, ax1 = plt.subplots()
ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# 2. GC content per segment (if DNA input is available)
if 'dna_input' in st.session_state:
    st.subheader("🧬 GC Content by Segment")
    segment_length = 100
    dna_seq = st.session_state.dna_input.upper()
    gc_values = []

    for i in range(0, len(dna_seq), segment_length):
        segment = dna_seq[i:i+segment_length]
        if len(segment) < segment_length:
            continue
        gc = (segment.count("G") + segment.count("C")) / len(segment)
        gc_values.append(gc)

    fig2, ax2 = plt.subplots()
    ax2.plot(range(1, len(gc_values) + 1), gc_values, marker='o')
    ax2.set_xlabel("Segment Index")
    ax2.set_ylabel("GC Content")
    ax2.set_title("GC Content per DNA Segment")
    st.pyplot(fig2)

# 3. Seed trace table
if st.session_state.last_seed_trace:
    st.subheader("🔑 Seed Trace Log")
    st.write("Below are the seeds used per chaotic system per segment.")
    st.table(st.session_state.last_seed_trace)
