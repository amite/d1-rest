from typing import List

def validate_sql_file(filepath: str) -> tuple[int, List[str]]:
    """Validate generated SQL file"""
    errors = []
    line_count = 0
    
    with open(filepath, 'r') as f:
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
            
            # Check for empty string values in critical fields
            if "'', ''" in line:
                errors.append(f"Line {line_num}: Contains empty critical fields")
            
            # Check for unescaped quotes (basic check)
            # Count single quotes - should be even
            quote_count = line.count("'")
            if quote_count % 2 != 0:
                errors.append(f"Line {line_num}: Unbalanced quotes")
    
    return line_count, errors

if __name__ == "__main__":
    filepath = "db/mutations/insert_videos_migrated.sql"
    
    print(f"🔍 Validating {filepath}...")
    count, errors = validate_sql_file(filepath)
    
    print(f"\n📊 Validation Results:")
    print(f"  📝 Total statements: {count}")
    print(f"  ❌ Errors found: {len(errors)}")
    
    if errors:
        print("\n❌ Errors:")
        for error in errors[:20]:  # Show first 20
            print(f"  - {error}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors")
    else:
        print("\n✅ All statements valid!")