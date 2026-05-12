#!/usr/bin/env python3
"""
Standalone script to seed default users.

Usage:
    python seed_default_users.py
    
Or with uv:
    uv run python seed_default_users.py
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.seed_users import create_default_users

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Default Users Seeding Script")
    print("="*60 + "\n")
    
    create_default_users()
    
    print("\nYou can now login with any of the default users!")
    print("Example: admin@test.com / admin123\n")
