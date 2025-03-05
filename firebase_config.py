import os
import firebase_admin
from firebase_admin import credentials

# Get the credentials path from an environment variable
credentials_path = os.getenv("FIREBASE_CREDENTIALS")

if not credentials_path:
    raise ValueError("Firebase credentials path not set. Please set FIREBASE_CREDENTIALS_PATH.")

# Load the credentials and initialize Firebase
cred = credentials.Certificate(credentials_path)
firebase_admin.initialize_app(cred)
