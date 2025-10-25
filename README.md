# applovin-market-intelligence
**applovin challenge** @ **cal hacks**

## **Ad Intelligence Challenge**

### **Your Goal:**
Create a **model** or **prototype** that processes **ad creatives** (images or videos) and extracts **novel, high-value features** or **insights** that could feed into a **recommendation engine**.

**NOTE:** We will be using the **SnapAR glasses** to properly display this data for the user to visualize (possibly with **WebXR**)

---

## Setup

### Prerequisites
- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

#### Using uv (Recommended)
```bash
# Install dependencies
uv pip install -r requirements.txt

# Or sync with pyproject.toml
uv sync
```

#### Using pip
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running Color Palette Extraction

```bash
# Activate virtual environment (if using venv)
source .venv/bin/activate

# Run the analysis on all images
python3 data-analysis/main.py
```

This will:
- Process all images in `data-analysis/data/ads/images/`
- Extract color palettes (5 dominant colors by default)
- Analyze color properties (saturation, brightness, vibrancy)
- Save visualizations to `data-analysis/data/results/color_palettes/`

### Output

Color palette visualizations are saved as `{original_filename}_with_palette.png` in the results directory. Each visualization shows:
- The original image
- A color palette bar below with the extracted dominant colors
- Console output with hex color codes and analysis metrics

