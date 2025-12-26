#!/usr/bin/env python3
"""
D1 Database Insert Testing Script
Analyzes and tests INSERT statements for the videos table
"""

import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple

def analyze_insert_statements(filepath: str) -> Tuple[List[str], List[str]]:
    """Analyze INSERT statements for issues"""
    errors = []
    warnings = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split into individual INSERT statements
    statements = []
    current_statement = ""
    in_string = False
    escape_next = False
    
    for char in content:
        current_statement += char
        
        if escape_next:
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            continue
            
        if char == "'" and not escape_next:
            in_string = not in_string
            
        if char == ';' and not in_string:
            if current_statement.strip():
                statements.append(current_statement.strip())
            current_statement = ""
    
    print(f"📊 Found {len(statements)} INSERT statements")
    
    # Expected column order for videos table
    expected_columns = [
        'video_id', 'cleaned_title', 'cleaned_description', 
        'channel_name', 'channel_id', 'published_at', 
        'duration_seconds', 'view_count', 'like_count', 
        'comment_count', 'is_indexed', 'created_at'
    ]
    
    for i, stmt in enumerate(statements, 1):
        print(f"\n🔍 Analyzing statement {i}:")
        
        # Check if it specifies columns
        if 'INSERT INTO videos (' in stmt:
            print("  ✅ Uses explicit column specification")
            # Extract column list
            columns_match = re.search(r'INSERT INTO videos \(([^)]+)\)', stmt)
            if columns_match:
                columns = [col.strip() for col in columns_match.group(1).split(',')]
                print(f"  📝 Columns: {len(columns)} specified")
                if len(columns) != len(expected_columns):
                    warnings.append(f"Statement {i}: Expected {len(expected_columns)} columns, got {len(columns)}")
        else:
            print("  ⚠️  Uses implicit column order (dangerous!)")
            warnings.append(f"Statement {i}: Should specify explicit column names")
        
        # Count values in VALUES clause
        values_match = re.search(r'VALUES\s*\((.*)\)', stmt, re.DOTALL)
        if values_match:
            values_str = values_match.group(1)
            # Simple count of comma-separated values (rough estimate)
            values_count = values_str.count(',') + 1
            print(f"  📊 Values count: {values_count}")
            
            if 'INSERT INTO videos (' not in stmt:  # Implicit order
                if values_count != len(expected_columns):
                    errors.append(f"Statement {i}: Expected {len(expected_columns)} values, got {values_count}")
        
        # Check for potential issues
        if 'replace(' in stmt:
            print("  🔧 Uses replace() function")
            
        # Check for unescaped quotes
        if re.search(r"'[^']*'[^']*'", stmt) and "VALUES" in stmt:
            print("  ⚠️  Potential unescaped quotes detected")
    
    return errors, warnings

def create_test_database() -> str:
    """Create a temporary SQLite database for testing"""
    db_path = "/tmp/test_videos.db"
    
    # Create videos table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE videos (
            video_id TEXT PRIMARY KEY,
            cleaned_title TEXT,
            cleaned_description TEXT,
            channel_name TEXT,
            channel_id TEXT,
            published_at TIMESTAMP,
            duration_seconds INTEGER,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,
            is_indexed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

def test_inserts_with_sqlite(sql_file: str, db_path: str) -> List[str]:
    """Test INSERT statements using SQLite (local testing)"""
    errors = []
    
    with open(sql_file, 'r') as f:
        content = f.read()
    
    # Split into statements
    statements = []
    current_statement = ""
    in_string = False
    escape_next = False
    
    for char in content:
        current_statement += char
        
        if escape_next:
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            continue
            
        if char == "'" and not escape_next:
            in_string = not in_string
            
        if char == ';' and not in_string:
            if current_statement.strip():
                statements.append(current_statement.strip())
            current_statement = ""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for i, stmt in enumerate(statements, 1):
        try:
            print(f"🧪 Testing statement {i}...")
            cursor.execute(stmt)
            print(f"  ✅ Success")
        except Exception as e:
            error_msg = f"Statement {i} failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)
    
    conn.commit()
    
    # Check what was inserted
    cursor.execute("SELECT COUNT(*) FROM videos")
    count = cursor.fetchone()[0]
    print(f"\n📊 Total records inserted: {count}")
    
    if count > 0:
        cursor.execute("SELECT video_id, cleaned_title, channel_name FROM videos LIMIT 3")
        sample = cursor.fetchall()
        print("📋 Sample data:")
        for row in sample:
            print(f"  - {row[0]}: {row[1]} ({row[2]})")
    
    conn.close()
    return errors

def generate_fixed_inserts(original_file: str) -> str:
    """Generate a fixed version of INSERT statements with explicit columns"""
    
    with open(original_file, 'r') as f:
        content = f.read()
    
    # This is a template for fixed INSERT statements
    fixed_template = '''-- Fixed INSERT statements with explicit column specification
INSERT INTO videos (
    video_id, cleaned_title, cleaned_description, 
    channel_name, channel_id, published_at, 
    duration_seconds, view_count, like_count, 
    comment_count, is_indexed, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
'''
    
    return fixed_template

def main():
    print("🚀 D1 Database Insert Testing Tool")
    print("=" * 50)
    
    # Analyze the test file
    sql_file = "db/mutations/test_5.sql"
    errors, warnings = analyze_insert_statements(sql_file)
    
    print(f"\n📋 Analysis Results:")
    print(f"  ❌ Errors: {len(errors)}")
    print(f"  ⚠️  Warnings: {len(warnings)}")
    
    if errors:
        print(f"\n❌ Critical Issues Found:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Test with SQLite
    print(f"\n🧪 Testing with SQLite...")
    db_path = create_test_database()
    test_errors = test_inserts_with_sqlite(sql_file, db_path)
    
    if test_errors:
        print(f"\n❌ SQLite Test Failures:")
        for error in test_errors:
            print(f"  - {error}")
    else:
        print(f"\n✅ All statements passed SQLite test!")
    
    # Generate fixed version
    print(f"\n🔧 Generating fixed INSERT template...")
    fixed_template = generate_fixed_inserts(sql_file)
    
    with open("db/mutations/test_5_fixed.sql", "w") as f:
        f.write(fixed_template)
    
    print(f"📝 Fixed template saved to: db/mutations/test_5_fixed.sql")
    
    print(f"\n💡 Recommendations:")
    print(f"  1. Always specify explicit column names in INSERT statements")
    print(f"  2. Use parameterized queries instead of string concatenation")
    print(f"  3. Test with SQLite first before running on D1")
    print(f"  4. Use wrangler d1 execute for D1 database operations")

if __name__ == "__main__":
    main()