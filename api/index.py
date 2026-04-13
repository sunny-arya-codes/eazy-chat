"""
Vercel serverless entry point.
Re-exports the FastAPI app from main.py so Vercel can discover it.
"""

from main import app  # noqa: F401
