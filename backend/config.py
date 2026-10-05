import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "mandisaathi.db")))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
