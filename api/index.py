import sys
import os

# Ensure current directory and backend are in Python path for Vercel Serverless
CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.app import app

# Vercel Serverless exports app
app = app
