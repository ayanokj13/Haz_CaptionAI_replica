# ⚡ Mirage AI: Automated Video Editor (MVP)

> **Turn raw talking-head videos into viral shorts automatically using AI.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![MoviePy](https://img.shields.io/badge/Engine-MoviePy-yellow)
![Status](https://img.shields.io/badge/Status-MVP_Live-success)

## 📖 Overview

**Mirage AI** is a local Python-based video editing pipeline designed to replicate the core functionality of tools like *Captions.ai* and *OpusClip*. It automates the tedious parts of video editing by using AI to transcribe audio, understand context, and apply engagement-boosting edits.

It takes a raw `.mp4` file and outputs a polished video with:
* **Synced Captions:** Word-level animations using viral font styles.
* **Smart B-Roll:** Automatically fetches and overlays relevant stock footage based on spoken keywords (using NLP).
* **Dynamic Zooms:** Applies "Ken Burns" style zooms during long static segments to retain viewer attention.

## ✨ Key Features

* **🎧 AI Transcription:** Uses OpenAI's **Whisper** model for highly accurate, timestamped speech-to-text.
* **🧠 "AI Director" (NLP):** Uses **spaCy** to analyze the transcript, identifying nouns and concepts (e.g., "Money", "Brain", "London") to fetch relevant visuals.
* **🎨 Viral Caption Styles:** Includes presets for popular styles like **Hormozi** (Bold), **MrBeast** (Comic), and **Typewriter**.
* **🖼️ Smart Overlay System:** B-Roll images are automatically cropped to 4:3 and centered to preserve the vertical video format (TikTok/Reels safe zones).
* **📊 Execution Logging:** Tracks processing time, word counts, and metadata for performance analysis.

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.8 or higher
* A [Pexels API Key](https://www.pexels.com/api/) (Free)
* **ImageMagick** (Required for text rendering)

### 1. Clone the Repository
```bash
git clone [https://github.com/ayanokj13/Haz_CaptionAI_replica.git](https://github.com/ayanokj13/Haz_CaptionAI_replica.git)
cd Haz_CaptionAI_replica

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Install NLP Model

Download the English language model for spaCy:

```bash
python -m spacy download en_core_web_sm

```

### 4. Install ImageMagick (Critical for Windows)

MoviePy requires ImageMagick to render text.

1. Download from [ImageMagick.org](https://www.google.com/search?q=https://imagemagick.org/script/download.php%23windows).
2. **IMPORTANT:** During installation, check the box **"Install legacy utilities (e.g. convert)"**.
3. Verify the path in `render.py` matches your installation:
```python
IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

```



### 5. Configure API Key

Open `magic_edit.py` and paste your Pexels API key:

```python
PEXELS_API_KEY = "YOUR_KEY_HERE"

```

---

## 🚀 Usage

### 1. Run the Dashboard

Launch the Streamlit interface:

```bash
streamlit run app.py

```

### 2. The Workflow

1. **Upload Video:** distinct `.mp4` file (Recommended duration: 30-60s).
2. **Settings:**
* **Font:** Choose a style (e.g., Hormozi, MrBeast).
* **Position:** Adjust the vertical slider (0.8 is recommended for Reels/TikTok).
* **Magic Edit:** Toggle ON to enable B-Roll and Zooms.


3. **Process:** Click **"Start Processing"**.
4. **Download:** Once complete, watch the video in the browser or download the `mirage_output.mp4`.

---

## 📂 Project Structure

| File | Description |
| --- | --- |
| **`app.py`** | The Streamlit Frontend. Handles file uploads, UI controls, and orchestrates the pipeline. |
| **`transcribe.py`** | Uses Whisper to generate `transcription_data.json` (Word-level timestamps). |
| **`magic_edit.py`** | The "Brain". Uses spaCy to find keywords and downloads images to `assets/`. Generates `visual_plan.json`. |
| **`render.py`** | The "Editor". Combines the video, B-Roll images, and Captions into the final `.mp4` using MoviePy. |
| **`fonts/`** | Contains custom `.ttf` files for the caption styles. |
| **`assets/`** | Temporary folder where downloaded B-roll images are stored. |

---

## ⚙️ Configuration details

* **Fonts:** To add new fonts, place `.ttf` files in the `fonts/` folder and update the `FONT_MAPPING` dictionary in `render.py`.
* **B-Roll Timing:** Adjust `MIN_ZOOM_INTERVAL` in `magic_edit.py` to control how frequently zooms or images appear.

## 🤝 Contributing

This is an MVP (Minimum Viable Product). Future roadmap items include:

* [ ] Silence Removal (Jump Cuts).
* [ ] Background Music Integration.
* [ ] Face Detection for "Safe" Zooms.

## 📝 License

This project is open-source and available for educational purposes.

---

*Built with ❤️ by Aditya*

```

```
