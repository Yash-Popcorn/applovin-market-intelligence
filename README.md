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

### Running Analysis

```bash
# Activate virtual environment (if using venv)
source .venv/bin/activate

# Run the analysis on all media files
python3 data-analysis/main.py
```

This will:
- Process images: Extract color palettes (5 dominant colors)
- Process videos: Extract video lengths
- Save results to `data-analysis/data/results/`

### Output

**Color Palettes** (`results/color_palettes/`):
- Files: `{filename}_with_palette.png`
- Shows original image with color palette bar below

**Video Lengths** (`results/video_length/`):
- Files: `{filename}.txt`
- Format: "42 seconds", "1 minute 3 seconds", etc.

### Settings

Control processing in `data-analysis/main.py`:
```python
MAX_IMAGES_TO_PROCESS = 5    # or None for all
MAX_VIDEOS_TO_PROCESS = None # or a number
```
