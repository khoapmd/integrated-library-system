#!/usr/bin/env python3
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print("Tables:", tables)
        
        # Check books table structure
        result = conn.execute(text("PRAGMA table_info(books)"))
        columns = [row[1] for row in result]
        print("Books table columns:", columns)
