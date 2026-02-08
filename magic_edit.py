import json
import random
import os
import requests
import spacy

# ==============================================================================
# 🔑 CONFIGURATION
# ==============================================================================
PEXELS_API_KEY = "1KuMKILq9sVplvw3xq2J7Wo3GHn7paIIkpDvnLLGfAFSddfxNYUD9LP3" 

MIN_ZOOM_INTERVAL = 4   
BROLL_DURATION = 2.5    
# ==============================================================================

# 1. LOAD THE NLP BRAIN
print("🧠 Loading NLP Model (en_core_web_sm)...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("❌ Model not found! Run: python -m spacy download en_core_web_sm")
    exit()

def download_image(query, filename):
    """Downloads a relevant image from Pexels"""
    if not PEXELS_API_KEY:
        return False 

    headers = {'Authorization': PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return False
            
        data = r.json()
        if data.get('photos'):
            img_url = data['photos'][0]['src']['large']
            img_data = requests.get(img_url).content
            with open(filename, 'wb') as f:
                f.write(img_data)
            return True
    except Exception as e:
        print(f"⚠️ Error downloading {query}: {e}")
    return False

def generate_visual_plan(json_path):
    print("🎬 AI Director: analyzing speech patterns...")
    
    with open(json_path, "r") as f:
        segments = json.load(f)

    visual_events = []
    last_event_time = 0
    
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # Words that are technically nouns but we don't want images for
    banned_words = ["thing", "way", "lot", "bit", "kind", "sort", "something", "anything", "nothing"]

    for segment in segments:
        word_text = segment['word'].strip(".,!?\"'")
        start = segment['start']
        
        # 1. ANALYZE WORD WITH NLP
        doc = nlp(word_text)
        token = doc[0] # Get the token object

        # RULES FOR SELECTING AN IMAGE:
        # A. Must be a Noun (NOUN) or Proper Noun (PROPN)
        # B. Must NOT be a stop word (e.g., "it", "the")
        # C. Must NOT be in our banned list
        # D. Time since last image > 3 seconds
        
        is_visual = (token.pos_ in ["NOUN", "PROPN"]) and (not token.is_stop) and (word_text.lower() not in banned_words)

        if is_visual and (start - last_event_time > 3):
            print(f"   💡 AI detected subject: '{word_text}' ({token.pos_}) -> Fetching B-Roll...")
            
            image_filename = f"assets/{word_text}_{int(start)}.jpg"
            
            # Use the word itself as the search query
            success = download_image(word_text, image_filename)
            
            if success:
                event = {
                    "type": "image",
                    "start": start,
                    "duration": BROLL_DURATION,
                    "src": image_filename,
                    "is_placeholder": False,
                    "keyword": word_text
                }
                visual_events.append(event)
                last_event_time = start + BROLL_DURATION
            else:
                print(f"      (No good image found for '{word_text}', skipping)")

        # 2. ZOOM LOGIC (Fallback)
        elif (start - last_event_time > MIN_ZOOM_INTERVAL):
            if random.random() > 0.6: # 40% chance
                print(f"   🔍 Adding Smart Zoom at {start}s")
                event = {
                    "type": "zoom",
                    "start": start,
                    "duration": 3.0 
                }
                visual_events.append(event)
                last_event_time = start + 3.0

    with open("visual_plan.json", "w") as f:
        json.dump(visual_events, f, indent=4)
    
    print(f"✅ Visual Plan Created with NLP! {len(visual_events)} events.")

if __name__ == "__main__":
    if os.path.exists("transcription_data.json"):
        generate_visual_plan("transcription_data.json")
    else:
        print("❌ 'transcription_data.json' not found!")