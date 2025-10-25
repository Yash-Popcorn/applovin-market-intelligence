from pathlib import Path
from typing import Optional

from lib.audio_engineering import AudioAnalyzer


def analyze_video_audio(video_path: Path, output_dir: Optional[Path] = None):
    analyzer = AudioAnalyzer()
    
    results = analyzer.analyze_video(video_path)
    
    if results is None:
        return None
    
    volume_db, pitch_hz, bpm = results
    
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "results" / "audio_analysis"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{video_path.stem}.txt"
    
    with open(output_file, 'w') as f:
        f.write(f"Average Volume: {volume_db:.2f} dB\n")
        f.write(f"Average Pitch: {pitch_hz:.2f} Hz\n")
        f.write(f"Average BPM: {bpm:.2f}\n")
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'video':
        analyze_video_audio(path, output_dir)

