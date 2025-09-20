"""Configuration settings for the AI debugger."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project settings
PROJECT_ROOT = Path(__file__).parent.parent
VECTOR_DB_PATH = PROJECT_ROOT / "vector_db"

# API settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Search settings
MAX_SEARCH_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3

# File patterns to include in analysis
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".hpp"}
IGNORE_PATTERNS = {
    "__pycache__",
    "node_modules", 
    ".git",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".pytest_cache"
}