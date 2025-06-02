# 🔐 BioKey: DNA-Parametrized Chaotic Encryption

BioKey is a Streamlit-based hybrid encryption tool that combines DNA sequence randomness and chaotic system switching (Lorenz, Rössler, Chen) to securely encrypt text and images.

---

## 🎯 Features

### 📥 1. Input Options
- **Text**: User inputs text which is encrypted using DNA-guided chaotic XOR.
- **Image**: User uploads .jpg/.png file which is converted to bytes and encrypted similarly.

### 🧬 2. DNA Sequence Options
- **Manual** input
- **Predefined datasets**:
  - Example BRCA1
  - Example TP53
  - Synthetic Sample

---

### 🔄 3. DNA-Driven Chaotic System
- DNA is segmented (100 bases each)
- GC content determines which chaotic system is used:
  - GC < 0.4 → Chen
  - 0.4–0.6 → Lorenz
  - GC > 0.6 → Rössler
- Each segment generates a unique chaotic seed
- Output XOR-ed with data to encrypt

---

### 🔐 4. Encryption Output
- Hex (for text) or binary (for images)
- SHA-256 hash for integrity
- Shannon Entropy for randomness
- Downloadable ciphertext (`.txt` or `.bin`)

---

### 📊 5. Analysis Module
Accessible under “📊 Run Analysis Module”
- 🔵 **Chaotic system usage distribution** (Pie chart)
- 🧬 **GC content by DNA segment** (Line chart)
- 🔑 **Seed trace log** (per segment)

---

## 📂 Project Structure

```
biokey-encryption/
├── app.py                        # Main Streamlit app
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── pages/
    ├── analysis_module.py       # Analysis page
    └── decryption_module.py     # Decryption page
```

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🌐 Streamlit Cloud Deployment

1. Upload this repo to GitHub
2. Deploy via [https://share.streamlit.io/](https://share.streamlit.io/)

---

## 📝 License
MIT
