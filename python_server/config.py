import pytz
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# delimiter for SSE
DELIMITER = "---END OF EVENT---\n\n"

berlin_tz = pytz.timezone("Europe/Berlin")
TIMEZONE = berlin_tz

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
