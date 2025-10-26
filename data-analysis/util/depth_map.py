import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

from lib.depth_map_generator import DepthMapGenerator


def analyze_depth_map(depth_map_path: Path, threshold: int = 128) -> Optional[Tuple[float, float]]:
    img = cv2.imread(str(depth_map_path), cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        return None
    
    total_pixels = img.shape[0] * img.shape[1]
    
    close_pixels = np.sum(img >= threshold)
    far_pixels = total_pixels - close_pixels
    
    close_percentage = (close_pixels / total_pixels) * 100
    far_percentage = (far_pixels / total_pixels) * 100
    
    return close_percentage, far_percentage


def generate_and_analyze_depth_map(image_path: Path, output_dir: Optional[Path] = None, threshold: int = 128):
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "results" / "depth_maps"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = DepthMapGenerator()
    
    depth_map_url = generator.generate_depth_map(image_path)
    
    if depth_map_url is None:
        return None
    
    depth_map_image_path = output_dir / f"{image_path.stem}_depth.png"
    
    success = generator.download_depth_map(depth_map_url, depth_map_image_path)
    
    if not success:
        return None
    
    result = analyze_depth_map(depth_map_image_path, threshold)
    
    if result is None:
        return None
    
    close_pct, far_pct = result
    
    output_file = output_dir / f"{image_path.stem}.txt"
    
    with open(output_file, 'w') as f:
        f.write(f"Depth Map Analysis (threshold={threshold}):\n")
        f.write(f"Close to camera: {close_pct:.2f}%\n")
        f.write(f"Far from camera: {far_pct:.2f}%\n")
        f.write(f"Depth map image: {depth_map_image_path.name}\n")
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'image':
        generate_and_analyze_depth_map(path, output_dir)

