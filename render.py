import json
import os
import sys
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, ColorClip, concatenate_videoclips
from moviepy.config import change_settings

# ==============================================================================
# ⚙️ CONFIGURATION
# ==============================================================================
IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
OVERLAY_RATIO = 4/3       
OVERLAY_WIDTH_PCT = 1.0   
# ==============================================================================

if not os.path.exists(IMAGEMAGICK_BINARY):
    print("❌ ImageMagick path incorrect.")
    sys.exit(1)
else:
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

# --- LOAD SETTINGS FROM FRONTEND ---
DEFAULT_SETTINGS = {"font": "Arial", "position": 0.8}
if os.path.exists("settings.json"):
    with open("settings.json", "r") as f:
        USER_SETTINGS = json.load(f)
else:
    USER_SETTINGS = DEFAULT_SETTINGS

SELECTED_FONT_NAME = USER_SETTINGS.get("font", "Arial")
CAPTION_POSITION_Y = USER_SETTINGS.get("position", 0.8)

# --- 🅰️ FONT MAPPING LOGIC ---
# Maps the "Friendly Name" from the UI to the actual "File Path"
FONT_MAPPING = {
    # Custom Fonts (From your folder)
    "Hormozi (The Bold Font)": r"fonts/THEBOLDFONT-FREEVERSION.ttf",
    "MrBeast (Komika)": r"fonts/KOMIKAX_.ttf",
    "Street Soul (Vibe)": r"fonts/street soul.ttf",
    "Typewriter (Bold)": r"fonts/JMH Typewriter-Bold.ttf",
    "Typewriter (Thin)": r"fonts/JMH Typewriter-Thin.ttf",
    
    # System Fonts (Keep these as simple strings)
    "Arial": "Arial",
    "Arial-Bold": "Arial-Bold", 
    "Impact": "Impact", 
    "Courier New": "Courier New", 
    "Verdana": "Verdana", 
    "Segoe UI": "Segoe UI", 
    "Tahoma": "Tahoma"
}

# Resolve the actual path/name to use
# If the name isn't in the map, default to 'Arial'
FONT_PATH = FONT_MAPPING.get(SELECTED_FONT_NAME, "Arial")

def crop_to_ratio(clip, target_ratio):
    w, h = clip.size
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = h * target_ratio
        return clip.crop(x1=w/2 - new_w/2, width=new_w, height=h)
    else:
        new_h = w / target_ratio
        return clip.crop(y1=h/2 - new_h/2, width=w, height=new_h)

def apply_zoom(clip):
    w, h = clip.size
    return clip.crop(x1=w*0.15, y1=h*0.15, width=w*0.7, height=h*0.7).resize((w, h))

def create_video(video_path, json_path, visual_plan_path):
    print(f"🎬 Starting Render with Font: {SELECTED_FONT_NAME} | Path: {FONT_PATH}")
    
    with open(json_path, "r") as f:
        word_segments = json.load(f)
    
    visual_events = []
    if os.path.exists(visual_plan_path):
        with open(visual_plan_path, "r") as f:
            visual_events = json.load(f)

    main_clip = VideoFileClip(video_path)
    final_layers = [] 
    
    # 1. ZOOMS
    print("✂️ Processing Zooms...")
    clips = []
    last_t = 0
    zoom_events = [e for e in visual_events if e['type'] == 'zoom']
    zoom_events.sort(key=lambda x: x['start'])

    for event in zoom_events:
        start = event['start']
        end = start + event['duration']
        if start > last_t:
            clips.append(main_clip.subclip(last_t, start))
        zoom_part = main_clip.subclip(start, min(end, main_clip.duration))
        zoom_part = apply_zoom(zoom_part) 
        clips.append(zoom_part)
        last_t = end
    if last_t < main_clip.duration:
        clips.append(main_clip.subclip(last_t, main_clip.duration))
    base_track = concatenate_videoclips(clips) if clips else main_clip
    final_layers.append(base_track)

    # 2. B-ROLL
    print("🖼️ Overlaying B-Roll...")
    image_events = [e for e in visual_events if e['type'] == 'image']
    for event in image_events:
        start = event['start']
        duration = event['duration']
        if event.get('is_placeholder'):
            img_clip = ColorClip(size=(640, 480), color=(100,0,0), duration=duration)
            txt = TextClip(f"{event['keyword']}", fontsize=50, color='white').set_position('center').set_duration(duration)
            img_clip = CompositeVideoClip([img_clip, txt])
        elif os.path.exists(event['src']):
            img_clip = ImageClip(event['src']).set_duration(duration)
        else:
            continue
        
        img_clip = crop_to_ratio(img_clip, OVERLAY_RATIO)
        target_width = main_clip.w * OVERLAY_WIDTH_PCT
        img_clip = img_clip.resize(width=target_width).set_start(start).set_position(('center', 'center'))
        final_layers.append(img_clip)

    # 3. CAPTIONS
    print(f"📝 Generating Captions ({SELECTED_FONT_NAME})...")
    if isinstance(CAPTION_POSITION_Y, float):
        y_pos = main_clip.h * CAPTION_POSITION_Y
    else:
        y_pos = CAPTION_POSITION_Y

    for segment in word_segments:
        word = segment.get("word")
        start = segment.get("start")
        end = segment.get("end")
        if word:
            try:
                # Use FONT_PATH (which might be "fonts/Komika.ttf" OR "Arial")
                txt_clip = (TextClip(word, fontsize=70, font=FONT_PATH, 
                                     color='yellow', stroke_color='black', stroke_width=3)
                            .set_position(('center', y_pos))
                            .set_start(start)
                            .set_end(end))
                final_layers.append(txt_clip)
            except Exception as e:
                print(f"⚠️ Font '{FONT_PATH}' failed. Fallback to Arial. Error: {e}")
                txt_clip = (TextClip(word, fontsize=70, font='Arial', 
                                     color='yellow', stroke_color='black', stroke_width=3)
                            .set_position(('center', y_pos))
                            .set_start(start)
                            .set_end(end))
                final_layers.append(txt_clip)

    print("🔥 Compositing Final Video...")
    final_video = CompositeVideoClip(final_layers).set_duration(main_clip.duration)
    
    output_filename = "final_overlay_edit.mp4"
    final_video.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=main_clip.fps, preset="ultrafast", threads=4)
    print(f"✅ DONE! Saved as '{output_filename}'")

if __name__ == "__main__":
    if os.path.exists("transcription_data.json"):
        create_video("input.mp4", "transcription_data.json", "visual_plan.json")