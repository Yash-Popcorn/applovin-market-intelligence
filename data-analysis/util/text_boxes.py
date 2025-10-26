import cv2
from pathlib import Path
from typing import Optional

from lib.ocr_text_extractor import OCRTextExtractor


def extract_image_text_boxes(image_path: Path) -> Optional[str]:
    img = cv2.imread(str(image_path))
    
    if img is None:
        return None
    
    extractor = OCRTextExtractor()
    text_boxes = extractor.extract_text_boxes(img)
    
    if not text_boxes:
        return "No text detected"
    
    result_lines = []
    result_lines.append(f"Total text boxes detected: {len(text_boxes)}")
    result_lines.append("")
    
    for idx, box in enumerate(text_boxes, 1):
        result_lines.append(f"Text Box {idx}:")
        result_lines.append(f"  Text: {box['text']}")
        result_lines.append(f"  Position: (x={box['left']}, y={box['top']})")
        result_lines.append(f"  Size: (width={box['width']}, height={box['height']})")
        result_lines.append(f"  Block: {box['block_num']}, Paragraph: {box['par_num']}, Line: {box['line_num']}, Word: {box['word_num']}")
        result_lines.append("")
    
    return "\n".join(result_lines)


def extract_video_text_boxes(video_path: Path) -> Optional[str]:
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps <= 0:
        cap.release()
        return None
    
    extractor = OCRTextExtractor()
    result_lines = []
    current_second = 0
    frame_interval = int(fps)
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_number % frame_interval == 0:
            text_boxes = extractor.extract_text_boxes(frame)
            
            if text_boxes:
                result_lines.append(f"Second {current_second}:")
                result_lines.append(f"  Total text boxes: {len(text_boxes)}")
                
                for idx, box in enumerate(text_boxes, 1):
                    result_lines.append(f"  Text Box {idx}:")
                    result_lines.append(f"    Text: {box['text']}")
                    result_lines.append(f"    Position: (x={box['left']}, y={box['top']})")
                    result_lines.append(f"    Size: (width={box['width']}, height={box['height']})")
                
                result_lines.append("")
            else:
                result_lines.append(f"Second {current_second}: No text detected")
                result_lines.append("")
            
            current_second += 1
        
        frame_number += 1
    
    cap.release()
    
    if not result_lines:
        return "No frames processed"
    
    return "\n".join(result_lines)


def save_text_boxes(path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'image':
        text_boxes_text = extract_image_text_boxes(path)
    elif file_type == 'video':
        text_boxes_text = extract_video_text_boxes(path)
    else:
        return None
    
    if text_boxes_text is None:
        return None
    
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "results" / "text_boxes"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{path.stem}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text_boxes_text)
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    save_text_boxes(path, output_dir)

