import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Secret key for application (e.g., for JWT or sessions)
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")

# Other configuration can be added here
DEBUG = os.getenv("DEBUG", "False").lower() == "true"