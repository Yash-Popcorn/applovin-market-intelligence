"""
Shared pytest fixtures for all test modules.
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory structure."""
    data_dir = tmp_path / "data"
    images_dir = data_dir / "ads" / "images"
    videos_dir = data_dir / "ads" / "videos"
    results_dir = data_dir / "results"
    
    images_dir.mkdir(parents=True)
    videos_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)
    
    return {
        'data': data_dir,
        'images': images_dir,
        'videos': videos_dir,
        'results': results_dir
    }


@pytest.fixture
def sample_image_files(temp_data_dir):
    """Create sample image files for testing."""
    images_dir = temp_data_dir['images']
    
    image_files = []
    for i in range(1, 6):
        img_path = images_dir / f"i{i:04d}.png"
        img_path.write_text(f"fake image data {i}")
        image_files.append(img_path)
    
    return image_files


@pytest.fixture
def sample_video_files(temp_data_dir):
    """Create sample video files for testing."""
    videos_dir = temp_data_dir['videos']
    
    video_files = []
    for i in range(1, 6):
        vid_path = videos_dir / f"v{i:04d}.mp4"
        vid_path.write_text(f"fake video data {i}")
        video_files.append(vid_path)
    
    return video_files