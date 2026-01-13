"""Data collectors for Instagram audit."""
from .base import Collector
from .export_ingest import ExportIngestCollector
from .graph_api import GraphApiCollector

# Optional instaloader collector (requires instaloader package)
try:
    from .instaloader_collector import InstaLoaderCollector, INSTALOADER_AVAILABLE
except ImportError:
    InstaLoaderCollector = None  # type: ignore
    INSTALOADER_AVAILABLE = False

__all__ = [
    "Collector",
    "ExportIngestCollector",
    "GraphApiCollector",
    "InstaLoaderCollector",
    "INSTALOADER_AVAILABLE",
]
