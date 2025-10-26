import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict

from lib.audio_separator import AudioSeparator


def analyze_dynamics(audio_path: Path) -> Dict[str, float]:
    audio_data, sample_rate = sf.read(audio_path)
    
    if audio_data.ndim > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    audio_data = audio_data.astype(np.float64)
    
    rms = np.sqrt(np.mean(audio_data**2))
    peak = np.max(np.abs(audio_data))
    
    if peak > 0:
        crest_factor = peak / rms if rms > 0 else 0
    else:
        crest_factor = 0
    
    rms_db = 20 * np.log10(rms) if rms > 0 else -np.inf
    peak_db = 20 * np.log10(peak) if peak > 0 else -np.inf
    
    dynamic_range = peak_db - rms_db if rms_db != -np.inf else 0
    
    return {
        'rms_db': float(rms_db),
        'peak_db': float(peak_db),
        'dynamic_range_db': float(dynamic_range),
        'crest_factor': float(crest_factor)
    }


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
        f.write(f"DYNAMICS ANALYSIS\n")
        f.write(f"{'='*60}\n\n")
        
        for track_name, track_path in results.items():
            if track_path.exists():
                dynamics = analyze_dynamics(track_path)
                f.write(f"{track_name.capitalize()}:\n")
                f.write(f"  RMS Level: {dynamics['rms_db']:.2f} dB\n")
                f.write(f"  Peak Level: {dynamics['peak_db']:.2f} dB\n")
                f.write(f"  Dynamic Range: {dynamics['dynamic_range_db']:.2f} dB\n")
                f.write(f"  Crest Factor: {dynamics['crest_factor']:.2f}\n")
                f.write(f"\n")
        
        f.write(f"{'='*60}\n")
        f.write(f"Total tracks: {len(results)}\n")
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'video':
        separate_video_audio(path, output_dir)

