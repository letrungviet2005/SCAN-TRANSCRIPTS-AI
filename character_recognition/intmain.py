"""Compatibility wrapper for the legacy character_recognition.intmain module."""

from services.ocr_engine import process_image_with_coordinates

__all__ = ["process_image_with_coordinates"]

