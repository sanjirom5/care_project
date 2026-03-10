import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL") or "postgresql+psycopg2://care_user:your_strong_password@localhost/care_platform"

