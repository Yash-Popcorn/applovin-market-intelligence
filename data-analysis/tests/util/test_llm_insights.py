"""
Comprehensive unit tests for util/llm_insights.py module.

Tests cover happy paths, edge cases, error conditions, and various input scenarios
for LLM-based image analysis functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from typing import Optional

# Module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from util import llm_insights


class TestAnalyzeAdImage:
    """Test suite for analyze_ad_image function."""
    
    @pytest.fixture
    def mock_analyzer(self):
        """Fixture providing a mocked LLMImageAnalyzer."""
        with patch('util.llm_insights.LLMImageAnalyzer') as MockAnalyzer:
            mock_instance = Mock()
            mock_instance.analyze_image = Mock(return_value={'ocr': 'test', 'demographics': 'test'})
            mock_instance.format_insights_as_text = Mock(return_value='Test Report Content')
            MockAnalyzer.return_value = mock_instance
            yield MockAnalyzer, mock_instance
    
    @pytest.fixture
    def sample_image_path(self, tmp_path):
        """Fixture providing a sample image path."""
        image_path = tmp_path / "test_ad.png"
        image_path.write_text("fake image data")  # Create dummy file
        return image_path
    
    def test_analyze_ad_image_happy_path(self, mock_analyzer, sample_image_path, tmp_path):
        """Test successful image analysis with default parameters."""
        MockAnalyzer, mock_instance = mock_analyzer
        output_dir = tmp_path / "output"
        
        result = llm_insights.analyze_ad_image(
            sample_image_path, 
            output_dir=output_dir
        )
        
        # Verify LLMImageAnalyzer was initialized with default model
        MockAnalyzer.assert_called_once_with(model="gpt-5-mini")
        
        # Verify analyze_image was called correctly
        mock_instance.analyze_image.assert_called_once_with(
            sample_image_path, 
            use_web_search=True
        )
        
        # Verify format_insights_as_text was called
        mock_instance.format_insights_as_text.assert_called_once_with(
            {'ocr': 'test', 'demographics': 'test'},
            sample_image_path
        )
        
        # Verify output file was created
        assert result is not None
        assert result.exists()
        assert result.name == "test_ad.txt"
        assert result.parent == output_dir
        
        # Verify file content
        content = result.read_text(encoding='utf-8')
        assert content == 'Test Report Content'
    
    def test_analyze_ad_image_custom_model(self, mock_analyzer, sample_image_path, tmp_path):
        """Test image analysis with custom model parameter."""
        MockAnalyzer, _mock_instance = mock_analyzer
        output_dir = tmp_path / "output"
        
        result = llm_insights.analyze_ad_image(
            sample_image_path,
            output_dir=output_dir,
            model="gpt-4-turbo"
        )
        
        # Verify custom model was used
        MockAnalyzer.assert_called_once_with(model="gpt-4-turbo")
        assert result is not None
    
    def test_analyze_ad_image_without_web_search(self, mock_analyzer, sample_image_path, tmp_path):
        """Test image analysis with web search disabled."""
        _MockAnalyzer, mock_instance = mock_analyzer
        output_dir = tmp_path / "output"
        
        result = llm_insights.analyze_ad_image(
            sample_image_path,
            output_dir=output_dir,
            use_web_search=False
        )
        
        # Verify use_web_search parameter was passed correctly
        mock_instance.analyze_image.assert_called_once_with(
            sample_image_path,
            use_web_search=False
        )
        assert result is not None
    
    def test_analyze_ad_image_default_output_dir(self, mock_analyzer, sample_image_path):
        """Test image analysis with default output directory."""
        MockAnalyzer, _mock_instance = mock_analyzer
        
        with patch('util.llm_insights.Path') as MockPath:
            # Setup mock to handle Path operations
            mock_parent = Mock()
            mock_parent.parent = Mock()
            mock_output_dir = Mock()
            mock_output_dir.mkdir = Mock()
            
            # Configure __file__ behavior
            MockPath.return_value = mock_parent
            mock_parent.parent.parent = Mock()
            mock_script_dir = mock_parent.parent.parent
            mock_script_dir.__truediv__ = Mock(side_effect=[
                Mock(__truediv__=Mock(side_effect=[
                    Mock(__truediv__=Mock(return_value=mock_output_dir))
                ]))
            ])
            
            # Need to actually create output for file writing
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                llm_insights.analyze_ad_image(
                    sample_image_path,
                    output_dir=None
                )
        
        # Verify analyzer was called
        MockAnalyzer.assert_called_once()
    
    def test_analyze_ad_image_creates_output_directory(self, mock_analyzer, sample_image_path, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        _MockAnalyzer, _mock_instance = mock_analyzer
        output_dir = tmp_path / "non_existent" / "nested" / "dir"
        
        # Verify directory doesn't exist before
        assert not output_dir.exists()
        
        result = llm_insights.analyze_ad_image(
            sample_image_path,
            output_dir=output_dir
        )
        
        # Verify directory was created
        assert output_dir.exists()
        assert result is not None
    
    def test_analyze_ad_image_analyzer_exception(self, sample_image_path, tmp_path):
        """Test handling of analyzer initialization exception."""
        output_dir = tmp_path / "output"
        
        with patch('util.llm_insights.LLMImageAnalyzer') as MockAnalyzer:
            MockAnalyzer.side_effect = Exception("Analyzer initialization failed")
            
            result = llm_insights.analyze_ad_image(
                sample_image_path,
                output_dir=output_dir
            )
            
            # Should return None on exception
            assert result is None
    
    def test_analyze_ad_image_analysis_exception(self, sample_image_path, tmp_path):
        """Test handling of analyze_image exception."""
        output_dir = tmp_path / "output"
        
        with patch('util.llm_insights.LLMImageAnalyzer') as MockAnalyzer:
            mock_instance = Mock()
            mock_instance.analyze_image.side_effect = ValueError("Invalid image format")
            MockAnalyzer.return_value = mock_instance
            
            result = llm_insights.analyze_ad_image(
                sample_image_path,
                output_dir=output_dir
            )
            
            # Should return None and handle exception gracefully
            assert result is None
    
    def test_analyze_ad_image_format_exception(self, sample_image_path, tmp_path):
        """Test handling of format_insights_as_text exception."""
        output_dir = tmp_path / "output"
        
        with patch('util.llm_insights.LLMImageAnalyzer') as MockAnalyzer:
            mock_instance = Mock()
            mock_instance.analyze_image.return_value = {'data': 'test'}
            mock_instance.format_insights_as_text.side_effect = RuntimeError("Format error")
            MockAnalyzer.return_value = mock_instance
            
            result = llm_insights.analyze_ad_image(
                sample_image_path,
                output_dir=output_dir
            )
            
            # Should return None on exception
            assert result is None
    
    def test_analyze_ad_image_file_write_exception(self, mock_analyzer, sample_image_path, tmp_path):
        """Test handling of file write exception."""
        _MockAnalyzer, _mock_instance = mock_analyzer
        output_dir = tmp_path / "output"
        
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = llm_insights.analyze_ad_image(
                sample_image_path,
                output_dir=output_dir
            )
            
            # Should return None on file write failure
            assert result is None
    
    def test_analyze_ad_image_unicode_content(self, mock_analyzer, sample_image_path, tmp_path):
        """Test handling of unicode characters in insights."""
        _MockAnalyzer, mock_instance = mock_analyzer
        output_dir = tmp_path / "output"
        
        # Set unicode content in mock
        unicode_content = "Analysis: 日本語 中文 العربية emoji: 🎉 ✅"
        mock_instance.format_insights_as_text.return_value = unicode_content
        
        result = llm_insights.analyze_ad_image(
            sample_image_path,
            output_dir=output_dir
        )
        
        # Verify unicode was written correctly
        assert result is not None
        content = result.read_text(encoding='utf-8')
        assert content == unicode_content
    
    def test_analyze_ad_image_empty_insights(self, mock_analyzer, sample_image_path, tmp_path):
        """Test handling of empty insights."""
        _MockAnalyzer, mock_instance = mock_analyzer
        output_dir = tmp_path / "output"
        
        mock_instance.analyze_image.return_value = {}
        mock_instance.format_insights_as_text.return_value = ""
        
        result = llm_insights.analyze_ad_image(
            sample_image_path,
            output_dir=output_dir
        )
        
        # Should still create file even with empty content
        assert result is not None
        assert result.exists()
        assert result.read_text(encoding='utf-8') == ""
    
    def test_analyze_ad_image_special_characters_in_filename(self, mock_analyzer, tmp_path):
        """Test handling of special characters in image filename."""
        _MockAnalyzer, _mock_instance = mock_analyzer
        output_dir = tmp_path / "output"
        
        # Create file with special characters
        image_path = tmp_path / "test_image_with_spaces&special#chars.png"
        image_path.write_text("fake data")
        
        result = llm_insights.analyze_ad_image(
            image_path,
            output_dir=output_dir
        )
        
        assert result is not None
        # stem should preserve the filename without extension
        assert "test_image_with_spaces&special#chars" in result.name


class TestRun:
    """Test suite for run function."""
    
    @pytest.fixture
    def mock_file_utils(self):
        """Fixture to mock file_utils module."""
        with patch('lib.file_utils.is_video_or_image') as mock_func:
            yield mock_func
    
    @pytest.fixture
    def mock_analyze(self):
        """Fixture to mock analyze_ad_image function."""
        with patch('util.llm_insights.analyze_ad_image') as mock_func:
            mock_func.return_value = Path("/fake/output.txt")
            yield mock_func
    
    def test_run_with_image_file(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with an image file."""
        image_path = tmp_path / "test.png"
        image_path.write_text("fake image")
        
        mock_file_utils.return_value = 'image'
        
        llm_insights.run(image_path)
        
        # Verify file type check was performed
        mock_file_utils.assert_called_once_with(image_path)
        
        # Verify analyze_ad_image was called with correct parameters
        mock_analyze.assert_called_once_with(image_path, None, model="gpt-5-mini")
    
    def test_run_with_video_file(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with a video file - should not analyze."""
        video_path = tmp_path / "test.mp4"
        video_path.write_text("fake video")
        
        mock_file_utils.return_value = 'video'
        
        llm_insights.run(video_path)
        
        # Verify file type check was performed
        mock_file_utils.assert_called_once_with(video_path)
        
        # Verify analyze_ad_image was NOT called for video
        mock_analyze.assert_not_called()
    
    def test_run_with_unknown_file(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with unknown file type."""
        unknown_path = tmp_path / "test.txt"
        unknown_path.write_text("fake text")
        
        mock_file_utils.return_value = 'unknown'
        
        llm_insights.run(unknown_path)
        
        # Verify file type check was performed
        mock_file_utils.assert_called_once_with(unknown_path)
        
        # Verify analyze_ad_image was NOT called for unknown type
        mock_analyze.assert_not_called()
    
    def test_run_with_custom_output_dir(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with custom output directory."""
        image_path = tmp_path / "test.jpg"
        image_path.write_text("fake image")
        output_dir = tmp_path / "custom_output"
        
        mock_file_utils.return_value = 'image'
        
        llm_insights.run(image_path, output_dir=output_dir)
        
        # Verify analyze_ad_image was called with custom output dir
        mock_analyze.assert_called_once_with(image_path, output_dir, model="gpt-5-mini")
    
    def test_run_with_custom_model(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with custom model parameter."""
        image_path = tmp_path / "test.png"
        image_path.write_text("fake image")
        
        mock_file_utils.return_value = 'image'
        
        llm_insights.run(image_path, model="gpt-4")
        
        # Verify custom model was passed through
        mock_analyze.assert_called_once_with(image_path, None, model="gpt-4")
    
    def test_run_with_pathlib_path(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with pathlib.Path object."""
        image_path = Path(tmp_path / "test.png")
        image_path.write_text("fake image")
        
        mock_file_utils.return_value = 'image'
        
        llm_insights.run(image_path)
        
        # Verify it works with Path objects
        mock_file_utils.assert_called_once_with(image_path)
        mock_analyze.assert_called_once()
    
    def test_run_with_string_path(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with string path."""
        image_path = tmp_path / "test.png"
        image_path.write_text("fake image")
        
        mock_file_utils.return_value = 'image'
        
        llm_insights.run(str(image_path))
        
        # Verify it works with string paths
        mock_file_utils.assert_called_once()
        mock_analyze.assert_called_once()
    
    def test_run_multiple_image_types(self, mock_file_utils, mock_analyze, tmp_path):
        """Test run function with various image file extensions."""
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        
        for ext in extensions:
            image_path = tmp_path / f"test{ext}"
            image_path.write_text("fake image")
            
            mock_file_utils.return_value = 'image'
            
            llm_insights.run(image_path)
        
        # Verify analyze_ad_image was called for each image type
        assert mock_analyze.call_count == len(extensions)
    
    def test_run_preserves_none_return(self, mock_file_utils, mock_analyze, tmp_path):
        """Test that run function properly handles None return from analyze_ad_image."""
        image_path = tmp_path / "test.png"
        image_path.write_text("fake image")
        
        mock_file_utils.return_value = 'image'
        mock_analyze.return_value = None
        
        # Should not raise exception
        llm_insights.run(image_path)
        
        mock_analyze.assert_called_once()


class TestIntegration:
    """Integration tests for llm_insights module."""
    
    def test_module_imports(self):
        """Test that all required imports are available."""
        assert hasattr(llm_insights, 'Path')
        assert hasattr(llm_insights, 'Optional')
        assert hasattr(llm_insights, 'analyze_ad_image')
        assert hasattr(llm_insights, 'run')
    
    def test_analyze_ad_image_signature(self):
        """Test function signature for analyze_ad_image."""
        import inspect
        sig = inspect.signature(llm_insights.analyze_ad_image)
        params = list(sig.parameters.keys())
        
        assert 'image_path' in params
        assert 'output_dir' in params
        assert 'model' in params
        assert 'use_web_search' in params
        
        # Check default values
        assert sig.parameters['output_dir'].default is None
        assert sig.parameters['model'].default == "gpt-5-mini"
        assert sig.parameters['use_web_search'].default is True
    
    def test_run_signature(self):
        """Test function signature for run."""
        import inspect
        sig = inspect.signature(llm_insights.run)
        params = list(sig.parameters.keys())
        
        assert 'path' in params
        assert 'output_dir' in params
        assert 'model' in params
        
        # Check default values
        assert sig.parameters['output_dir'].default is None
        assert sig.parameters['model'].default == "gpt-5-mini"