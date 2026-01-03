import os
from dotenv import load_dotenv

load_dotenv()

# Azure Storage
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
CONTAINER_NAME = "gold"