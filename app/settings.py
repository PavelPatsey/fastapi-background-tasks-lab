from pathlib import Path

SOURCE_DIR: Path = Path(__file__).resolve().parent.parent
DB_FILE_NAME = f"{SOURCE_DIR}/database.db"
DB_URL = f"sqlite:///{DB_FILE_NAME}"
CONNECT_ARGS = {"check_same_thread": False}
