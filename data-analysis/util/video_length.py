import cv2
from pathlib import Path
from typing import Optional

from lib.time_utils import format_duration


def get_video_duration(video_path: Path) -> float:
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        return 0.0
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    cap.release()
    
    if fps > 0:
        duration = frame_count / fps
        return duration
    
    return 0.0


def save_video_length(video_path: Path, output_dir: Optional[Path] = None):
    duration_seconds = get_video_duration(video_path)
    
    if duration_seconds == 0:
        return None
    
    formatted_duration = format_duration(duration_seconds)
    
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "results" / "video_length"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{video_path.stem}.txt"
    
    with open(output_file, 'w') as f:
        f.write(formatted_duration)
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'video':
        output_file = save_video_length(path, output_dir)
        
    elif file_type == 'image':
        pass
    else:
        pass

