"""Compatibility wrappers for previous module names."""

from pipeline import process_multiple_images_to_groups
from services.excel_exporter import export_to_excel
from services.ocr_engine import process_image_with_coordinates
from services.table_detector import process_image

__all__ = [
    "process_multiple_images_to_groups",
    "export_to_excel",
    "process_image_with_coordinates",
    "process_image",
]
