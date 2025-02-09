import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from environs import Env

# Get project root directory path
ROOT_DIR = Path(__file__).parent.parent.parent

# Load environment variables from root .env file
load_dotenv(os.path.join(ROOT_DIR, '.env'))

# Initialize environs
env = Env()

# Get configuration from environment variables
qdrant_url = f"http://localhost:{os.getenv('VECTOR_STORE_DB_PORT')}"
qdrant_api_key = os.getenv('VECTOR_STORE_DB_API_KEY')

# Print connecetion information
print(f"Qdrant URL: {qdrant_url}")
print(f"Qdrant API Key: {qdrant_api_key}")

# Make request to Qdrant
response = requests.get(
    qdrant_url,
    headers={'api-key': qdrant_api_key},
    verify=False  # Equivalent to curl's --insecure flag
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")