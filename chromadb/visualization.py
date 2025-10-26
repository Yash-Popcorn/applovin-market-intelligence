from __future__ import annotations

import os
import tempfile
import webbrowser
from typing import Iterable, List


def _to_3d(vec: Iterable[float]) -> List[float]:
    arr = list(vec)
    if len(arr) >= 3:
        return arr[:3]
    # pad to 3 dims if needed
    return arr + [0.0] * (3 - len(arr))


def visualize_embedding_3d(embedding: Iterable[float], title: str = "Embedding (3D)", open_browser: bool = True) -> str:
    try:
        import plotly.graph_objects as go  # type: ignore
    except Exception as exc:  # pragma: no cover - import guard
        raise ImportError("plotly is required. Install with `pip install plotly`.") from exc

    x, y, z = _to_3d(embedding)

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=[x], y=[y], z=[z],
                mode="markers",
                marker=dict(size=6, color="#1f77b4"),
                name="embedding",
            )
        ]
    )
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Dim 1",
            yaxis_title="Dim 2",
            zaxis_title="Dim 3",
        ),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    tmpdir = tempfile.gettempdir()
    out_path = os.path.join(tmpdir, "embedding_3d.html")
    fig.write_html(out_path, auto_open=False, include_plotlyjs="cdn")

    if open_browser:
        webbrowser.open(f"file://{out_path}")

    return out_path

