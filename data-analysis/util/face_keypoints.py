import cv2
from pathlib import Path
from typing import Optional

from lib.face_mesh_detector import FaceMeshDetector


def extract_image_keypoints(image_path: Path) -> Optional[str]:
    img = cv2.imread(str(image_path))
    
    if img is None:
        return None
    
    detector = FaceMeshDetector()
    detector.find_face_mesh(img)
    keypoints_data = detector.get_keypoints(img)
    detector.close()
    
    if not keypoints_data:
        return "No faces detected"
    
    result_lines = []
    for face_idx, face_keypoints in enumerate(keypoints_data):
        result_lines.append(f"Face {face_idx + 1}:")
        for landmark_id, x, y in face_keypoints:
            result_lines.append(f"  Landmark {landmark_id}: ({x}, {y})")
    
    return "\n".join(result_lines)


def extract_video_keypoints(video_path: Path) -> Optional[str]:
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps <= 0:
        cap.release()
        return None
    
    detector = FaceMeshDetector()
    result_lines = []
    current_second = 0
    frame_interval = int(fps)
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_number % frame_interval == 0:
            detector.find_face_mesh(frame)
            keypoints_data = detector.get_keypoints(frame)
            
            if keypoints_data:
                result_lines.append(f"Second {current_second}:")
                for face_idx, face_keypoints in enumerate(keypoints_data):
                    result_lines.append(f"  Face {face_idx + 1}:")
                    for landmark_id, x, y in face_keypoints:
                        result_lines.append(f"    Landmark {landmark_id}: ({x}, {y})")
            else:
                result_lines.append(f"Second {current_second}: No faces detected")
            
            current_second += 1
        
        frame_number += 1
    
    cap.release()
    detector.close()
    
    if not result_lines:
        return "No frames processed"
    
    return "\n".join(result_lines)


def save_keypoints(path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'image':
        keypoints_text = extract_image_keypoints(path)
    elif file_type == 'video':
        keypoints_text = extract_video_keypoints(path)
    else:
        return None
    
    if keypoints_text is None:
        return None
    
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "results" / "face_keypoints"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{path.stem}.txt"
    
    with open(output_file, 'w') as f:
        f.write(keypoints_text)
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    save_keypoints(path, output_dir)

