import math
import colorsys
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image
import matplotlib.pyplot as plt
from scipy import cluster
import pandas as pd


def extract_palette(image_path: Path, num_colors: int = 5, return_hex: bool = True) -> List[Tuple]:
    img = plt.imread(str(image_path))
    
    red, green, blue = [], [], []
    for line in img:
        for pixel in line:
            r, g, b = pixel[:3]
            red.append(r)
            green.append(g)
            blue.append(b)
    
    df = pd.DataFrame({'red': red, 'green': green, 'blue': blue})
    
    df['standardized_red'] = cluster.vq.whiten(df['red'])
    df['standardized_green'] = cluster.vq.whiten(df['green'])
    df['standardized_blue'] = cluster.vq.whiten(df['blue'])
    
    color_palette, distortion = cluster.vq.kmeans(
        df[['standardized_red', 'standardized_green', 'standardized_blue']],
        num_colors
    )
    
    colors = []
    red_std, green_std, blue_std = df[['red', 'green', 'blue']].std()
    
    for color in color_palette:
        scaled_red, scaled_green, scaled_blue = color
        rgb_color = (
            int(max(0, min(255, math.ceil(scaled_red * red_std * 255)))),
            int(max(0, min(255, math.ceil(scaled_green * green_std * 255)))),
            int(max(0, min(255, math.ceil(scaled_blue * blue_std * 255))))
        )
        colors.append(rgb_color)
    
    colors.sort(key=lambda x: _color_sort_key(x[0], x[1], x[2], 8))
    
    if return_hex:
        return [_rgb_to_hex(color) for color in colors]
    return colors


def create_palette_visualization(image_path: Path, output_path: Optional[Path] = None, num_colors: int = 5, show_hex: bool = True) -> Path:
    colors = extract_palette(image_path, num_colors, return_hex=False)
    
    pil_img = Image.open(image_path)
    pil_width, pil_height = pil_img.size
    
    if pil_height > pil_width:
        palette_height = math.floor(pil_height / 6)
    else:
        palette_height = math.floor(pil_height / 4)
    
    palette = Image.new('RGB', (pil_width, palette_height), (255, 255, 255))
    
    single_img_offset = math.floor(pil_width / (num_colors * 14))
    total_offset = single_img_offset * (num_colors + 1)
    single_img_width = math.floor((pil_width - total_offset) / num_colors)
    single_img_space = single_img_width + single_img_offset
    
    x_offset = single_img_offset
    for i, color in enumerate(colors):
        if i == len(colors) - 1:
            final_width = pil_width - x_offset - single_img_offset
            new_img = Image.new('RGB', (final_width, palette_height), color)
            palette.paste(new_img, (x_offset, 0))
        else:
            new_img = Image.new('RGB', (single_img_width, palette_height), color)
            palette.paste(new_img, (x_offset, 0))
            x_offset += single_img_space
    
    height_offset = math.ceil(pil_height / 20)
    if pil_height > pil_width:
        height_offset = math.ceil(pil_height / 30)
    
    total_height = pil_height + palette_height + (height_offset * 2)
    combined_img = Image.new('RGB', (pil_width, total_height), (255, 255, 255))
    combined_img.paste(pil_img, (0, 0))
    combined_img.paste(palette, (0, pil_height + height_offset))
    
    if output_path is None:
        output_path = image_path.parent / f"{image_path.stem}_with_palette{image_path.suffix}"
    
    combined_img.save(output_path)
    return output_path


def get_dominant_color(image_path: Path) -> Tuple[int, int, int]:
    colors = extract_palette(image_path, num_colors=1, return_hex=False)
    return colors[0]


def _color_sort_key(r: int, g: int, b: int, repetitions: int = 1) -> Tuple:
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    lum = math.sqrt(0.241 * r_norm + 0.691 * g_norm + 0.068 * b_norm)
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    
    h2 = int(h * repetitions)
    lum2 = int(lum * repetitions)
    v2 = int(v * repetitions)
    
    if h2 % 2 == 1:
        v2 = repetitions - v2
        lum = repetitions - lum
    
    return (h2, lum, v2)


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return '#%02x%02x%02x' % rgb


def analyze_color_properties(colors: List[Tuple[int, int, int]]) -> dict:
    hsv_colors = [colorsys.rgb_to_hsv(r/255, g/255, b/255) for r, g, b in colors]
    
    hues = [h for h, s, v in hsv_colors]
    saturations = [s for h, s, v in hsv_colors]
    values = [v for h, s, v in hsv_colors]
    
    return {
        'num_colors': len(colors),
        'avg_saturation': sum(saturations) / len(saturations),
        'avg_brightness': sum(values) / len(values),
        'hue_diversity': max(hues) - min(hues) if hues else 0,
        'has_vibrant': any(s > 0.6 and v > 0.6 for h, s, v in hsv_colors),
        'has_dark': any(v < 0.3 for h, s, v in hsv_colors),
        'has_light': any(v > 0.8 for h, s, v in hsv_colors),
    }


def run(path: Path, num_colors: int = 5, output_dir: Optional[Path] = None):
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'image':
        palette = extract_palette(path, num_colors=num_colors)
        rgb_colors = extract_palette(path, num_colors=num_colors, return_hex=False)
        analysis = analyze_color_properties(rgb_colors)
        
        if output_dir is None:
            script_dir = Path(__file__).parent.parent
            output_dir = script_dir / "data" / "results" / "color_palettes"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{path.stem}_with_palette{path.suffix}"
        output_path = create_palette_visualization(path, output_path, num_colors=num_colors)
        
    elif file_type == 'video':
        pass
    else:
        pass
