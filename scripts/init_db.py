"""
Run this script to create database tables manually.

Usage:
    python scripts/init_db.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.database import create_tables, engine


async def main():
    try:
        await create_tables()
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
