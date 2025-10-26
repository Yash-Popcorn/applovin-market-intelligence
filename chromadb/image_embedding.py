from __future__ import annotations

import os
from typing import List, Optional


class GeminiImageEmbedder:
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        model_name: str = "multimodalembedding@001",
    ) -> None:
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = model_name

        if not self.project:
            raise EnvironmentError(
                "GOOGLE_CLOUD_PROJECT is not set. Please export your GCP project ID."
            )

        # Lazy imports so that importing this module doesn't require deps until used.
        try:
            from vertexai import init as vertexai_init  # type: ignore
            from vertexai.vision_models import MultiModalEmbeddingModel  # type: ignore
        except Exception as exc:  # pragma: no cover - import guard
            raise ImportError(
                "google-cloud-aiplatform is required. Install with `pip install google-cloud-aiplatform`."
            ) from exc

        # Initialize Vertex AI
        vertexai_init(project=self.project, location=self.location)

        # Store type for mypy but defer actual model load to first call
        self._vertex_model_cls = MultiModalEmbeddingModel
        self._model = None

    def _get_model(self):
        if self._model is None:
            self._model = self._vertex_model_cls.from_pretrained(self.model_name)
        return self._model

    def embed_image(self, image_path: str) -> List[float]:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            from vertexai.vision_models import Image as VertexImage  # type: ignore
        except Exception as exc:  # pragma: no cover - import guard
            raise ImportError(
                "google-cloud-aiplatform is required. Install with `pip install google-cloud-aiplatform`."
            ) from exc

        model = self._get_model()
        image = VertexImage.load_from_file(image_path)
        embeddings = model.get_embeddings(image=image)

        # Vertex returns a container with image/text embeddings depending on inputs
        vec = getattr(embeddings, "image_embedding", None)
        if not vec:
            raise RuntimeError("No image_embedding returned from Vertex AI.")
        return list(vec)

    def embed_and_visualize(
        self,
        image_path: str,
        title: str = "Image Embedding (3D)",
        open_browser: bool = True,
    ) -> List[float]:
        vec = self.embed_image(image_path)
        try:
            from chromadb.visualization import visualize_embedding_3d
        except Exception as exc:
            raise ImportError(
                "Visualization helper not found. Ensure chromadb/visualization.py exists."
            ) from exc

        visualize_embedding_3d(vec, title=title, open_browser=open_browser)
        return vec

