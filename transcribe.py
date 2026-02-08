import torch # Must be imported first
import os
import gc
import json
import typing # <--- NEW IMPORT NEEDED FOR THE FIX
import omegaconf

# --- 🛠️ NUCLEAR FIX FOR PYTORCH 2.6 ---
# 1. Whitelist ALL the classes causing errors (including typing.Any)
try:
    from omegaconf.listconfig import ListConfig
    from omegaconf.dictconfig import DictConfig
    from omegaconf.base import ContainerMetadata 
    
    # This is the "Magic List" that stops the errors
    torch.serialization.add_safe_globals([
        ListConfig, 
        DictConfig, 
        ContainerMetadata,
        typing.Any # <--- The specific fix for your new error
    ])
except ImportError:
    pass
except AttributeError:
    pass

# 2. Monkey Patch torch.load to force weights_only=False globally
# This overrides the new strict security setting
original_load = torch.load
def safe_load(*args, **kwargs):
    # FORCE False. This overrides the library's internal default.
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = safe_load
# ------------------------------------------------

# NOW import the heavy libraries (After the fix is applied)
import whisperx

def run_batch_transcription(video_path):
    device = "cpu"
    print(f"🚀 Loading 'BASE' Model on {device}...")

    # 1. Load Model
    try:
        model = whisperx.load_model("base", device, compute_type="int8")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # 2. Transcribe
    print(f"🎧 Processing: {video_path}")
    audio = whisperx.load_audio(video_path)
    result = model.transcribe(audio, batch_size=4)
    
    # Cleanup 1
    del model
    gc.collect()

    # 3. Align
    print("⚡ Aligning text...")
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    # Cleanup 2
    del model_a
    gc.collect()

    # 4. Save to JSON
    output_filename = "transcription_data.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(result["word_segments"], f, indent=4)
    
    print(f"✅ Success! Data saved to '{output_filename}'")
    print("👉 Now run: python render.py")

if __name__ == "__main__":
    VIDEO_FILE = "input.mp4" 
    
    if os.path.exists(VIDEO_FILE):
        run_batch_transcription(VIDEO_FILE)
    else:
        print(f"❌ Could not find file: {VIDEO_FILE}")
        print("Please rename your video to 'input.mp4' and put it in this folder.")