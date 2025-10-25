from pathlib import Path
from lib.file_utils import is_video_or_image


def run(path):
    file_path = Path(path)
    file_type = is_video_or_image(file_path)
    print(f"Processing: {file_path}")
    print(f"File type: {file_type}")
    

