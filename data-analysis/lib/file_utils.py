from pathlib import Path

def is_video_or_image(path):
    file_path = Path(path)
    extension = file_path.suffix.lower()
    
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico'}
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpeg', '.mpg'}
    
    if extension in image_extensions:
        return 'image'
    elif extension in video_extensions:
        return 'video'
    else:
        return 'unknown'

