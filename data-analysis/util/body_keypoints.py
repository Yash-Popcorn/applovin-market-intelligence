import cv2
from pathlib import Path
from typing import Optional

from lib.body_pose_detector import BodyPoseDetector


def extract_image_keypoints(image_path: Path) -> Optional[str]:
    img = cv2.imread(str(image_path))
    
    if img is None:
        return None
    
    detector = BodyPoseDetector()
    detector.find_pose(img)
    keypoints_data = detector.get_keypoints(img)
    detector.close()
    
    if not keypoints_data:
        return "No pose detected"
    
    result_lines = []
    result_lines.append("Body Pose:")
    for landmark_id, x, y, visibility in keypoints_data:
        result_lines.append(f"  Landmark {landmark_id}: ({x}, {y}) | Visibility: {visibility:.3f}")
    
    return "\n".join(result_lines)


def extract_video_keypoints(video_path: Path) -> Optional[str]:
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps <= 0:
        cap.release()
        return None
    
    detector = BodyPoseDetector()
    result_lines = []
    current_second = 0
    frame_interval = int(fps)
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_number % frame_interval == 0:
            detector.find_pose(frame)
            keypoints_data = detector.get_keypoints(frame)
            
            if keypoints_data:
                result_lines.append(f"Second {current_second}:")
                result_lines.append("  Body Pose:")
                for landmark_id, x, y, visibility in keypoints_data:
                    result_lines.append(f"    Landmark {landmark_id}: ({x}, {y}) | Visibility: {visibility:.3f}")
            else:
                result_lines.append(f"Second {current_second}: No pose detected")
            
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
        output_dir = script_dir / "data" / "results" / "body_keypoints"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{path.stem}.txt"
    
    with open(output_file, 'w') as f:
        f.write(keypoints_text)
    
    return output_file


def run(path: Path, output_dir: Optional[Path] = None):
    save_keypoints(path, output_dir)

