"""Vercel Serverless Entry Point for FastAPI Backend."""
import sys
import os

# Add the backend directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app  # noqa: E402
