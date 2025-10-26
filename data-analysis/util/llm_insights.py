import os
from pathlib import Path
from typing import Optional

from lib.llm_image_analyzer import LLMImageAnalyzer


def analyze_ad_image(
    image_path: Path,
    output_dir: Optional[Path] = None,
    model: str = "gpt-5-mini",
    use_web_search: bool = True
) -> Optional[Path]:
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "results" / "llm_insights"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        analyzer = LLMImageAnalyzer(model=model)
        insights = analyzer.analyze_image(image_path, use_web_search=use_web_search)
        report = analyzer.format_insights_as_text(insights, image_path)
        
        output_file = output_dir / f"{image_path.stem}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_file
    except Exception as e:
        print(f"Error analyzing {image_path.name}: {str(e)}")
        return None


def run(path: Path, output_dir: Optional[Path] = None, model: str = "gpt-5-mini"):
    from lib.file_utils import is_video_or_image
    
    file_type = is_video_or_image(path)
    
    if file_type == 'image':
        analyze_ad_image(path, output_dir, model=model)

