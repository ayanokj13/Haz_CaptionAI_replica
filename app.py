import streamlit as st
import os
import subprocess
import json
import shutil
import time
from moviepy.editor import VideoFileClip

# --- UI CONFIG ---
st.set_page_config(page_title="Mirage AI Editor", page_icon="⚡", layout="wide")

st.title("⚡ Mirage AI: Automated Video Editor")
st.markdown("Upload a raw video, and let AI add **Captions, B-Roll, and Zooms** automatically.")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("🎨 Visual Settings")

# 1. FONT SELECTOR
# Note: These names MUST match the keys in render.py FONT_MAPPING
font_options = [
    "Hormozi (The Bold Font)", 
    "MrBeast (Komika)", 
    "Street Soul (Vibe)", 
    "Typewriter (Bold)", 
    "Typewriter (Thin)",
    "Arial", 
    "Arial-Bold", 
    "Impact", 
    "Courier New", 
    "Verdana", 
    "Segoe UI", 
    "Tahoma"
]
selected_font = st.sidebar.selectbox("Caption Font", font_options, index=0)

# 2. POSITION SLIDER
caption_pos = st.sidebar.slider("Caption Vertical Position (%)", 0.1, 0.9, 0.8, 
                                help="0.1 = Top, 0.5 = Center, 0.9 = Bottom")

# 3. TOGGLES
use_magic_edit = st.sidebar.checkbox("✨ Enable Magic Edit (B-Roll & Zooms)", value=True)

# --- HELPER FUNCTION: LOGGING ---
def write_log(message):
    with open("process_log.txt", "a") as log_file:
        log_file.write(f"{message}\n")

# --- MAIN WORKFLOW ---
uploaded_file = st.file_uploader("📂 Upload Video (MP4)", type=["mp4", "mov"])

if uploaded_file:
    # Save input file
    with open("input.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.video("input.mp4")
    
    if st.button("🚀 START PROCESSING"):
        # Reset Log File
        if os.path.exists("process_log.txt"):
            os.remove("process_log.txt")
        
        start_total_time = time.time()
        write_log("=== MIRAGE AI PROCESSING LOG ===")
        
        # 0. ANALYZE VIDEO METADATA
        try:
            clip = VideoFileClip("input.mp4")
            duration = clip.duration
            fps = clip.fps
            total_frames = int(duration * fps) if fps else 0
            clip.close()
            
            write_log(f"VIDEO METADATA:")
            write_log(f" - Duration: {duration:.2f} seconds")
            write_log(f" - FPS: {fps}")
            write_log(f" - Total Frames: {total_frames}")
            write_log("-" * 30)
        except Exception as e:
            write_log(f"⚠️ Could not analyze video metadata: {e}")

        progress_bar = st.progress(0)
        status_text = st.empty()

        # 1. SAVE SETTINGS
        settings = {
            "font": selected_font,
            "position": caption_pos
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

        # 2. TRANSCRIBE (Step 1)
        status_text.text("🎧 AI is listening (Transcribing)...")
        t0 = time.time()
        try:
            subprocess.run(["python", "transcribe.py"], check=True)
            elapsed = time.time() - t0
            write_log(f"STEP 1: TRANSCRIPTION")
            write_log(f" - Execution Time: {elapsed:.2f} seconds")
            
            # Count detected words
            if os.path.exists("transcription_data.json"):
                with open("transcription_data.json", "r") as f:
                    data = json.load(f)
                    word_count = len(data)
                write_log(f" - Words Detected: {word_count}")
            
            progress_bar.progress(33)
        except subprocess.CalledProcessError:
            st.error("❌ Transcription Failed! Check terminal for details.")
            write_log("❌ ERROR: Transcription Failed.")
            st.stop()

        # 3. MAGIC EDIT (Step 2 - Optional)
        if use_magic_edit:
            status_text.text("🧠 AI Director is finding B-Roll...")
            t0 = time.time()
            try:
                subprocess.run(["python", "magic_edit.py"], check=True)
                elapsed = time.time() - t0
                write_log(f"STEP 2: MAGIC EDIT")
                write_log(f" - Execution Time: {elapsed:.2f} seconds")
                
                # Count visual events
                if os.path.exists("visual_plan.json"):
                    with open("visual_plan.json", "r") as f:
                        plan = json.load(f)
                        write_log(f" - Visual Events Planned: {len(plan)}")
            except subprocess.CalledProcessError:
                st.warning("⚠️ Magic Edit had an issue, skipping visuals.")
                write_log("⚠️ WARNING: Magic Edit failed or was skipped.")
        else:
            # If disabled, remove old visual plan to prevent using old images
            if os.path.exists("visual_plan.json"):
                os.remove("visual_plan.json")
            write_log("STEP 2: MAGIC EDIT (Skipped by User)")
        
        progress_bar.progress(66)

        # 4. RENDER (Step 3)
        status_text.text("🔥 Rendering final video (This takes time)...")
        t0 = time.time()
        try:
            subprocess.run(["python", "render.py"], check=True)
            elapsed = time.time() - t0
            write_log(f"STEP 3: RENDERING")
            write_log(f" - Execution Time: {elapsed:.2f} seconds")
            
            progress_bar.progress(100)
            status_text.success("✅ DONE! Processing Complete.")
            
            # Final Stats
            total_elapsed = time.time() - start_total_time
            write_log("-" * 30)
            write_log(f"TOTAL PROCESS TIME: {total_elapsed:.2f} seconds")
            
            # Show Result
            if os.path.exists("final_overlay_edit.mp4"):
                st.video("final_overlay_edit.mp4")
                
                # Display Log content in UI for quick check
                with open("process_log.txt", "r") as f:
                    st.text_area("📋 Execution Log", f.read(), height=200)

                # Download Button
                with open("final_overlay_edit.mp4", "rb") as f:
                    st.download_button("⬇️ Download Video", f, file_name="mirage_output.mp4")
            else:
                st.error("❌ Output file not found. Check terminal logs.")
                
        except subprocess.CalledProcessError:
            st.error("❌ Rendering Failed! Check terminal for details.")
            write_log("❌ ERROR: Rendering Failed.")

# Cleanup instructions
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Temporary Files"):
    files_to_clean = [
        "input.mp4", 
        "transcription_data.json", 
        "visual_plan.json", 
        "settings.json", 
        "final_overlay_edit.mp4",
        "process_log.txt"  # Added log file here
    ]
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
    if os.path.exists("assets"):
        shutil.rmtree("assets")
    st.sidebar.success("Cleaned!")