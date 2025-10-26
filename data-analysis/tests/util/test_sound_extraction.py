"""
Comprehensive unit tests for util/sound_extraction.py module.

Tests cover happy paths, edge cases, error conditions, and various input scenarios
for audio separation functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call, mock_open
from typing import Optional, Dict

# Module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from util import sound_extraction


class TestSeparateVideoAudio:
    """Test suite for separate_video_audio function."""
    
    @pytest.fixture
    def mock_separator(self):
        """Fixture providing a mocked AudioSeparator."""
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            
            # Create mock paths for separated tracks
            mock_results = {
                'drums': Mock(spec=Path, name='drums.wav'),
                'bass': Mock(spec=Path, name='bass.wav'),
                'other': Mock(spec=Path, name='other.wav'),
                'vocals': Mock(spec=Path, name='vocals.wav'),
                'instrumental': Mock(spec=Path, name='instrumental.wav')
            }
            
            # Mock exists() for all paths
            for path in mock_results.values():
                path.exists = Mock(return_value=True)
                path.stat = Mock(return_value=Mock(st_size=2653328))
            
            mock_instance.separate_video_audio.return_value = mock_results
            MockSeparator.return_value = mock_instance
            
            yield MockSeparator, mock_instance, mock_results
    
    @pytest.fixture
    def sample_video_path(self, tmp_path):
        """Fixture providing a sample video path."""
        video_path = tmp_path / "test_video.mp4"
        video_path.write_text("fake video data")
        return video_path
    
    def test_separate_video_audio_happy_path(self, mock_separator, sample_video_path, tmp_path):
        """Test successful audio separation with default parameters."""
        MockSeparator, mock_instance, _ = mock_separator
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = sound_extraction.separate_video_audio(
            sample_video_path,
            output_dir=output_dir
        )
        
        # Verify AudioSeparator was instantiated
        MockSeparator.assert_called_once()
        
        # Verify separate_video_audio was called correctly
        mock_instance.separate_video_audio.assert_called_once_with(
            sample_video_path,
            output_dir
        )
        
        # Verify manifest file was created
        assert result is not None
        assert result == output_dir / "manifest.txt"
    
    def test_separate_video_audio_default_output_dir(self, mock_separator, sample_video_path):
        """Test audio separation with default output directory."""
        MockSeparator, mock_instance, _ = mock_separator
        
        # Need to mock Path and file operations
        with patch('builtins.open', mock_open()):
            sound_extraction.separate_video_audio(
                sample_video_path,
                output_dir=None
            )
        
        # Verify separator was called
        MockSeparator.assert_called_once()
        mock_instance.separate_video_audio.assert_called_once()
    
    def test_separate_video_audio_creates_output_directory(self, mock_separator, sample_video_path, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        _, _, _ = mock_separator
        output_dir = tmp_path / "non_existent" / "nested" / "dir"
        
        # Verify directory doesn't exist before
        assert not output_dir.exists()
        
        result = sound_extraction.separate_video_audio(
            sample_video_path,
            output_dir=output_dir
        )
        
        # Verify directory was created
        assert output_dir.exists()
        assert result is not None
    
    def test_separate_video_audio_manifest_content(self, mock_separator, sample_video_path, tmp_path):
        """Test that manifest file contains correct content."""
        _, _, _ = mock_separator
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        result = sound_extraction.separate_video_audio(
            sample_video_path,
            output_dir=output_dir
        )
        
        # Read and verify manifest content
        assert result.exists()
        content = result.read_text()
        
        # Verify header
        assert f"Audio Separation Results for: {sample_video_path.name}" in content
        assert "=" * 60 in content
        
        # Verify each track is listed
        assert "Drums:" in content
        assert "Bass:" in content
        assert "Other:" in content
        assert "Vocals:" in content
        assert "Instrumental:" in content
        
        # Verify file sizes
        assert "MB" in content
        
        # Verify footer
        assert "Total tracks: 5" in content
    
    def test_separate_video_audio_returns_none_on_separator_failure(self, sample_video_path, tmp_path):
        """Test handling when separator returns None."""
        output_dir = tmp_path / "output"
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_instance.separate_video_audio.return_value = None
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(
                sample_video_path,
                output_dir=output_dir
            )
            
            # Should return None when separator fails
            assert result is None
    
    def test_separate_video_audio_handles_missing_tracks(self, sample_video_path, tmp_path):
        """Test handling when some tracks don't exist."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            
            # Create results with some missing files
            mock_results = {
                'drums': Mock(spec=Path, name='drums.wav'),
                'bass': Mock(spec=Path, name='bass.wav'),
                'other': Mock(spec=Path, name='other.wav')
            }
            
            # Only some files exist
            mock_results['drums'].exists = Mock(return_value=True)
            mock_results['drums'].stat = Mock(return_value=Mock(st_size=1000000))
            mock_results['bass'].exists = Mock(return_value=False)
            mock_results['other'].exists = Mock(return_value=True)
            mock_results['other'].stat = Mock(return_value=Mock(st_size=2000000))
            
            mock_instance.separate_video_audio.return_value = mock_results
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(
                sample_video_path,
                output_dir=output_dir
            )
            
            # Should still create manifest
            assert result is not None
            content = result.read_text()
            
            # Only existing files should be in manifest
            assert 'drums.wav' in content
            assert 'other.wav' in content
            # bass.wav should not be listed (doesn't exist)
    
    def test_separate_video_audio_with_different_file_sizes(self, sample_video_path, tmp_path):
        """Test manifest with different file sizes."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            
            # Create results with different file sizes
            mock_results = {
                'drums': Mock(spec=Path, name='drums.wav'),
                'bass': Mock(spec=Path, name='bass.wav')
            }
            
            mock_results['drums'].exists = Mock(return_value=True)
            mock_results['drums'].stat = Mock(return_value=Mock(st_size=1048576))  # 1 MB
            mock_results['bass'].exists = Mock(return_value=True)
            mock_results['bass'].stat = Mock(return_value=Mock(st_size=2097152))  # 2 MB
            
            mock_instance.separate_video_audio.return_value = mock_results
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(
                sample_video_path,
                output_dir=output_dir
            )
            
            content = result.read_text()
            
            # Verify sizes are formatted correctly (2 decimal places)
            assert "1.00 MB" in content
            assert "2.00 MB" in content
    
    def test_separate_video_audio_with_empty_results(self, sample_video_path, tmp_path):
        """Test handling of empty results dictionary."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_instance.separate_video_audio.return_value = {}
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(
                sample_video_path,
                output_dir=output_dir
            )
            
            # Should still create manifest
            assert result is not None
            content = result.read_text()
            
            # Should show 0 tracks
            assert "Total tracks: 0" in content
    
    def test_separate_video_audio_unicode_in_video_name(self, tmp_path):
        """Test handling of unicode characters in video filename."""
        video_path = tmp_path / "视频_日本語_🎬.mp4"
        video_path.write_text("fake video")
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_instance.separate_video_audio.return_value = {
                'drums': Mock(spec=Path, name='drums.wav')
            }
            drums_mock = Mock(spec=Path, name='drums.wav')
            drums_mock.exists = Mock(return_value=True)
            drums_mock.stat = Mock(return_value=Mock(st_size=1000000))
            drums_mock.name = 'drums.wav'
            mock_instance.separate_video_audio.return_value = {'drums': drums_mock}
            mock_instance.separate_video_audio.return_value['drums'].stat = Mock(
                return_value=Mock(st_size=1000000)
            )
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(
                video_path,
                output_dir=output_dir
            )
            
            # Should handle unicode in manifest
            assert result is not None
            content = result.read_text()
            assert video_path.name in content
    
    def test_separate_video_audio_separator_exception(self, sample_video_path, tmp_path):
        """Test handling of separator exception."""
        output_dir = tmp_path / "output"
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_instance.separate_video_audio.side_effect = RuntimeError("Separation failed")
            MockSeparator.return_value = mock_instance
            
            with pytest.raises(RuntimeError):
                sound_extraction.separate_video_audio(
                    sample_video_path,
                    output_dir=output_dir
                )
    
    def test_separate_video_audio_file_write_error(self, mock_separator, sample_video_path, tmp_path):
        """Test handling of manifest file write error."""
        _, _, _ = mock_separator
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Make output_dir read-only to cause write error
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                sound_extraction.separate_video_audio(
                    sample_video_path,
                    output_dir=output_dir
                )


class TestRun:
    """Test suite for run function."""
    
    @pytest.fixture
    def mock_file_utils(self):
        """Fixture to mock file_utils module."""
        with patch('lib.file_utils.is_video_or_image') as mock_func:
            yield mock_func
    
    @pytest.fixture
    def mock_separate(self):
        """Fixture to mock separate_video_audio function."""
        with patch('util.sound_extraction.separate_video_audio') as mock_func:
            mock_func.return_value = Path("/fake/manifest.txt")
            yield mock_func
    
    def test_run_with_video_file(self, mock_file_utils, mock_separate, tmp_path):
        """Test run function with a video file."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        
        mock_file_utils.return_value = 'video'
        
        sound_extraction.run(video_path)
        
        # Verify file type check was performed
        mock_file_utils.assert_called_once_with(video_path)
        
        # Verify separate_video_audio was called with correct parameters
        mock_separate.assert_called_once_with(video_path, None)
    
    def test_run_with_image_file(self, mock_file_utils, mock_separate, tmp_path):
        """Test run function with an image file - should not separate audio."""
        image_path = tmp_path / "test.png"
        image_path.write_text("fake image")
        
        mock_file_utils.return_value = 'image'
        
        sound_extraction.run(image_path)
        
        # Verify file type check was performed
        mock_file_utils.assert_called_once_with(image_path)
        
        # Verify separate_video_audio was NOT called for image
        mock_separate.assert_not_called()
    
    def test_run_with_unknown_file(self, mock_file_utils, mock_separate, tmp_path):
        """Test run function with unknown file type."""
        unknown_path = tmp_path / "test.txt"
        unknown_path.write_text("fake text")
        
        mock_file_utils.return_value = 'unknown'
        
        sound_extraction.run(unknown_path)
        
        # Verify file type check was performed
        mock_file_utils.assert_called_once_with(unknown_path)
        
        # Verify separate_video_audio was NOT called for unknown type
        mock_separate.assert_not_called()
    
    def test_run_with_custom_output_dir(self, mock_file_utils, mock_separate, tmp_path):
        """Test run function with custom output directory."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        output_dir = tmp_path / "custom_output"
        
        mock_file_utils.return_value = 'video'
        
        sound_extraction.run(video_path, output_dir=output_dir)
        
        # Verify separate_video_audio was called with custom output dir
        mock_separate.assert_called_once_with(video_path, output_dir)
    
    def test_run_with_pathlib_path(self, mock_file_utils, mock_separate, tmp_path):
        """Test run function with pathlib.Path object."""
        video_path = Path(tmp_path / "test.mp4")
        video_path.write_text("fake video")
        
        mock_file_utils.return_value = 'video'
        
        sound_extraction.run(video_path)
        
        # Verify it works with Path objects
        mock_file_utils.assert_called_once_with(video_path)
        mock_separate.assert_called_once()
    
    def test_run_with_string_path(self, mock_file_utils, mock_separate, tmp_path):
        """Test run function with string path."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        
        mock_file_utils.return_value = 'video'
        
        sound_extraction.run(str(video_path))
        
        # Verify it works with string paths
        mock_file_utils.assert_called_once()
        mock_separate.assert_called_once()
    
    def test_run_multiple_video_types(self, mock_file_utils, mock_separate, tmp_path):
        """Test run function with various video file extensions."""
        extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        for ext in extensions:
            video_path = tmp_path / f"test{ext}"
            video_path.write_text("fake video")
            
            mock_file_utils.return_value = 'video'
            
            sound_extraction.run(video_path)
        
        # Verify separate_video_audio was called for each video type
        assert mock_separate.call_count == len(extensions)
    
    def test_run_preserves_none_return(self, mock_file_utils, mock_separate, tmp_path):
        """Test that run function properly handles None return from separate_video_audio."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        
        mock_file_utils.return_value = 'video'
        mock_separate.return_value = None
        
        # Should not raise exception
        sound_extraction.run(video_path)
        
        mock_separate.assert_called_once()


class TestIntegration:
    """Integration tests for sound_extraction module."""
    
    def test_module_imports(self):
        """Test that all required imports are available."""
        assert hasattr(sound_extraction, 'Path')
        assert hasattr(sound_extraction, 'Optional')
        assert hasattr(sound_extraction, 'separate_video_audio')
        assert hasattr(sound_extraction, 'run')
    
    def test_separate_video_audio_signature(self):
        """Test function signature for separate_video_audio."""
        import inspect
        sig = inspect.signature(sound_extraction.separate_video_audio)
        params = list(sig.parameters.keys())
        
        assert 'video_path' in params
        assert 'output_dir' in params
        
        # Check default values
        assert sig.parameters['output_dir'].default is None
    
    def test_run_signature(self):
        """Test function signature for run."""
        import inspect
        sig = inspect.signature(sound_extraction.run)
        params = list(sig.parameters.keys())
        
        assert 'path' in params
        assert 'output_dir' in params
        
        # Check default values
        assert sig.parameters['output_dir'].default is None
    
    def test_manifest_format_consistency(self, tmp_path):
        """Test that manifest format is consistent across different runs."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_results = {'drums': Mock(spec=Path, name='drums.wav')}
            mock_results['drums'].exists = Mock(return_value=True)
            mock_results['drums'].stat = Mock(return_value=Mock(st_size=1000000))
            mock_instance.separate_video_audio.return_value = mock_results
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(video_path, output_dir)
            
            content = result.read_text()
            lines = content.split('\n')
            
            # Verify format structure
            assert lines[0].startswith("Audio Separation Results for:")
            assert "=" * 60 in lines[1]
            assert lines[2] == ""  # Empty line after header
            # Track info lines
            # Empty line before footer
            # Footer with equals signs
            # Total tracks line


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_filename(self, tmp_path):
        """Test handling of very long filename."""
        long_name = "a" * 200 + ".mp4"
        video_path = tmp_path / long_name
        video_path.write_text("fake video")
        output_dir = tmp_path / "output"
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_instance.separate_video_audio.return_value = {}
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(video_path, output_dir)
            
            # Should handle long filename
            assert result is not None
    
    def test_deep_nested_output_path(self, tmp_path):
        """Test creation of deeply nested output directories."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        output_dir = tmp_path / "a" / "b" / "c" / "d" / "e" / "f"
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_instance.separate_video_audio.return_value = {}
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(video_path, output_dir)
            
            # Should create all nested directories
            assert output_dir.exists()
            assert result is not None
    
    def test_zero_byte_file_size(self, tmp_path):
        """Test handling of zero-byte audio files."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_result = Mock(spec=Path, name='drums.wav')
            mock_result.exists = Mock(return_value=True)
            mock_result.stat = Mock(return_value=Mock(st_size=0))
            mock_instance.separate_video_audio.return_value = {'drums': mock_result}
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(video_path, output_dir)
            
            content = result.read_text()
            # Should show 0.00 MB
            assert "0.00 MB" in content
    
    def test_very_large_file_size(self, tmp_path):
        """Test handling of very large file sizes."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        with patch('util.sound_extraction.AudioSeparator') as MockSeparator:
            mock_instance = Mock()
            mock_result = Mock(spec=Path, name='drums.wav')
            mock_result.exists = Mock(return_value=True)
            # 5 GB file
            mock_result.stat = Mock(return_value=Mock(st_size=5368709120))
            mock_instance.separate_video_audio.return_value = {'drums': mock_result}
            MockSeparator.return_value = mock_instance
            
            result = sound_extraction.separate_video_audio(video_path, output_dir)
            
            content = result.read_text()
            # Should format large size correctly
            assert "5120.00 MB" in content or "5.00 GB" in content.replace("5120.00 MB", "5.00 GB")