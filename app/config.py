"""
Loads environment variables from .env for use across the app.
"""

import os
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-4o-mini")
API_VERSION = os.getenv("API_VERSION", "2024-05-01-preview")