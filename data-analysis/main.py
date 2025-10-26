import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

# Add the script's directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import util.color_theory
import util.video_length
import util.face_keypoints
import util.body_keypoints
import util.sound
import util.depth_map
import util.llm_insights
import util.sound_extraction

# SETTINGS
MAX_IMAGES_TO_PROCESS = 5
MAX_VIDEOS_TO_PROCESS = 5

# Define base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ADS_DIR = DATA_DIR / "ads"
IMAGES_DIR = ADS_DIR / "images"
VIDEOS_DIR = ADS_DIR / "videos"

def print_all_media_paths():
    media_dirs = [
        (IMAGES_DIR, "*.png", MAX_IMAGES_TO_PROCESS),
        (VIDEOS_DIR, "*.mp4", MAX_VIDEOS_TO_PROCESS)
    ]
    
    for directory, pattern, max_files in media_dirs:
        if directory.exists():
            files = sorted(directory.glob(pattern))
            
            if max_files is not None:
                files = files[:max_files]
            
            for file_path in files:
                # color palette of each image
                #util.color_theory.run(file_path)

                # time lapse of each video
                #util.video_length.run(file_path)
                
                # face keypoints of each image/video
                #util.face_keypoints.run(file_path)
                
                # body keypoints of each image/video
                #util.body_keypoints.run(file_path)
                
                # audio analysis of each video (volume, pitch, BPM)
                #util.sound.run(file_path)
                
                #util.depth_map.run(file_path)
                
                # llm insights for advertisement images (OCR, demographics, pricing, etc.)
                #util.llm_insights.run(file_path)
                
                # audio separation of each video (vocals, drums, bass, other, instrumental)
                util.sound_extraction.run(file_path)

if __name__ == "__main__":
    print_all_media_paths()

