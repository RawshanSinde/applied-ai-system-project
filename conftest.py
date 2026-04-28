import sys
import os

# Allow tests to import from src/ without requiring PYTHONPATH=src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
