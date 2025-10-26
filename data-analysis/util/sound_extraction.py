from pathlib import Path
from typing import Optional

from lib.audio_separator import AudioSeparator


def separate_video_audio(video_path: Path, output_dir: Optional[Path] = None):
    separator = AudioSeparator()
    
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "results" / "sound_extraction" / video_path.stem
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = separator.separate_video_audio(video_path, output_dir)
    
    if results is None:
        return None
    
    output_file = output_dir / "manifest.txt"
    
    with open(output_file, 'w') as f:
        f.write(f"Audio Separation Results for: {video_path.name}\n")
        f.write(f"{'='*60}\n\n")
        
        for track_name, track_path in results.items():
            if track_path.exists():
                file_size_mb = track_path.stat().st_size / (1024 * 1024)
                f.write(f"{track_name.capitalize()}: {track_path.name} ({file_size_mb:.2f} MB)\n")
        
        f.write(f"\n{'='*60}\n")
        f.write(f"Total tracks: {len(results)}\n")
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'video':
        separate_video_audio(path, output_dir)

