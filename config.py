import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("NVIDIA_API_KEY")
    API_URL = os.getenv("NVIDIA_API_URL")
    MODEL = os.getenv("MODEL_NAME")
    STREAM = os.getenv("STREAM", "true").lower() == "true"
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    TOP_P = float(os.getenv("TOP_P", 0.9))