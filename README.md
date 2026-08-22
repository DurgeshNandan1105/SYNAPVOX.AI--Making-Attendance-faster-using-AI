# 🎙️📸 SYNAPVOX.AI — Making Attendance Faster Using Multi-Modal AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![Buildathon](https://img.shields.io/badge/Razorpay-Buildathon%20Open%20Track-0284C7.svg)](https://razorpay.com/)
[![Database](https://img.shields.io/badge/Database-Supabase-orange.svg)](https://supabase.com/)

> **SynapVox.ai** revolutionizes classroom and institutional attendance by combining **Computer Vision (Face Biometrics)** and **Deep Voice Speaker Identification**. Say goodbye to 10-minute manual roll calls and proxy attendance—mark an entire class present in under 5 seconds.

---

## 🌐 Live Demo & Video

🚀 **Live App / Landing Page**: [Visit SYNAPVOX AI](https://snap-vox-ai-landing-page.vercel.app/)

🎥 **Project Demo Video**: [![Watch Demo](https://img.shields.io/badge/Watch-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://raw.githubusercontent.com/DurgeshNandan1105/SYNAPVOX.AI--Making-Attendance-faster-using-AI/main/Demo%20video.mp4)

---

## 🎯 The Problem & Highlights

Traditional roll-call systems in educational institutions and organizations suffer from major inefficiencies:
- ⏳ **Time Wastage**: Instructors waste 5 to 10 minutes per lecture calling out names, multiplying into hundreds of lost teaching hours annually.
- 🚨 **Proxy Attendance**: Buddy-punching and physical signature forgery are widespread and difficult to verify manually.
- 📉 **Slow Manual Reporting**: Compiling attendance records into databases is tedious, manual, and error-prone.

### ✨ Key Features
- 🤖 **AI-Powered Face Recognition**: Detects and identifies students using facial embeddings from a single classroom snapshot.
- 🎤 **Voice Biometrics Verification**: Speaker embedding identification (`resemblyzer` + `librosa`) for audio roll-call verification.
- ☁️ **Cloud Integration**: Real-time cloud database synchronization via Supabase.
- 📊 **Real-Time Attendance Analytics**: View present/absent logs, timestamps, and exported analytics.
- 👨‍🏫 **Teacher Dashboard**: Create subjects, manage classes, generate QR share codes, and run instant AI attendance.
- 👨‍🎓 **Student Dashboard**: Auto-enroll via join links, register face & voice biometrics, and track personal attendance rates.

---

## 🏗️ Architecture & AI Pipelines

```text
                           +------------------------------------+
                           |    SYNAPVOX.AI Streamlit App       |
                           +-----------------+------------------+
                                             |
                   +-------------------------+-------------------------+
                   |                                                   |
        +----------v----------+                             +----------v----------+
        |   Face Recognition  |                             |   Voice Biometrics  |
        |       Pipeline      |                             |       Pipeline      |
        +----------+----------+                             +----------+----------+
                   |                                                   |
       [dlib Face Detector]                                [librosa Audio Splitter]
                   |                                                   |
   [128-D Facial Embedding Computation]                 [Resemblyzer VoiceEncoder]
                   |                                                   |
       [Euclidean Distance Matching]                      [Cosine Similarity Matching]
                   |                                                   |
                   +-------------------------+-------------------------+
                                             |
                                  +----------v----------+
                                  |   Supabase Database |
                                  +---------------------+
```

---

## 🛠️ Tech Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/) (Custom responsive UI layout)
- **Computer Vision Engine**: `dlib`, `face_recognition_models`, `scikit-learn`, `Pillow`
- **Voice Biometrics Engine**: `Resemblyzer` (`VoiceEncoder`), `Librosa` (Signal processing & utterance splitting)
- **Backend & Database**: `Supabase` Cloud DB, `bcrypt` password hashing
- **Data & QR Processing**: `NumPy`, `Pandas`, `Segno` (QR codes)

---

## ⚙️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/DurgeshNandan1105/SYNAPVOX.AI--Making-Attendance-faster-using-AI.git
   cd SYNAPVOX.AI--Making-Attendance-faster-using-AI
   ```

2. **Create & Activate Virtual Environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Secrets**
   Create a `.env` file or configure `.streamlit/secrets.toml`:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

---

## 📈 Impact & Metrics

| Metric | Traditional Method | SynapVox.ai |
| :--- | :--- | :--- |
| **Attendance Time** | 5 – 10 minutes / lecture | **< 5 seconds** |
| **Proxy Resistance** | Very Low (Physical proxy) | **High (Multi-modal Biometric)** |
| **Data Logging** | Manual paper entry | **Instant Cloud Sync** |
| **Time Saved / Semester** | ~150 hours per institution | **~145+ Hours Reclaimed** |

---

## 🤝 Razorpay Buildathon Submission Notes

Submitted for **Track 05: Open Track ("Build what you believe should exist")**.
- **Category**: AI Productivity & Multi-Modal Automation
- **Value Proposition**: Solves high-frequency operational friction in education and enterprise environments through computer vision and voice intelligence.

---

## 👨‍💻 Author

### **Durgesh Nandan**
*AI & Full-Stack Developer*

- GitHub: [@DurgeshNandan1105](https://github.com/DurgeshNandan1105)
