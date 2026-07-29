"""Compatibility wrapper for the legacy title_detection.api module."""

from services.title_detector import predict_from_image

__all__ = ["predict_from_image"]

