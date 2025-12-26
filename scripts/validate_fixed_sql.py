#!/usr/bin/env python3
"""
Validate the fixed SQL file for proper syntax
"""

import re
from pathlib import Path

def validate_sql_file(file_path: str) -> tuple[int, list]:
    """Validate the generated SQL file"""
    errors = []
    line_count = 0
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line_count += 1
                line = line.strip()
                
                if not line:
                    continue
                
                # Check it's an INSERT statement
                if not line.startswith('INSERT INTO videos'):
                    errors.append(f"Line {line_num}: Not an INSERT statement")
                    continue
                
                # Check it ends with semicolon
                if not line.endswith(';'):
                    errors.append(f"Line {line_num}: Missing semicolon")
                
                # Check for basic syntax issues
                if line.count("'") % 2 != 0:
                    errors.append(f"Line {line_num}: Unbalanced quotes")
                    
    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
    
    return line_count, errors

if __name__ == "__main__":
    file_path = "db/mutations/insert_videos_migrated_fixed.sql"
    
    print(f"🔍 Validating {file_path}...")
    count, errors = validate_sql_file(file_path)
    
    print(f"\n📊 Validation Results:")
    print(f"  📝 Total statements: {count}")
    print(f"  ❌ Errors found: {len(errors)}")
    
    if errors:
        print("\n❌ Errors:")
        for error in errors[:10]:  # Show first 10
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    else:
        print("\n✅ All statements valid!")
        print("✅ Ready for D1 import!")