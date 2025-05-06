"""
Script to generate ambient immersive news manually.
Run this script to immediately create some ambient news articles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db
from utils.ambient_news_generator import generate_ambient_news

if __name__ == "__main__":
    with app.app_context():
        num_created = generate_ambient_news(count=5)
        print(f"Created {num_created} ambient news articles for immersion.")