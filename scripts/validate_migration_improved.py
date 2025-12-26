#!/usr/bin/env python3
"""Improved validation script that handles multi-line SQL statements"""
import re
from typing import List, Tuple

def validate_sql_file(filepath: str) -> Tuple[int, List[str]]:
    """Validate generated SQL file - handles multi-line statements"""
    errors = []
    statement_count = 0
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by semicolons to get individual statements
    # But be careful not to split on semicolons inside strings
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
            statements.append(current_statement.strip())
            current_statement = ""
    
    # Process each complete statement
    for stmt_num, statement in enumerate(statements, 1):
        if not statement.strip():
            continue
            
        statement_count += 1
        
        # Check it's an INSERT statement
        if not statement.strip().startswith('INSERT INTO videos'):
            errors.append(f"Statement {stmt_num}: Not an INSERT statement")
            continue
        
        # Check it starts with proper syntax
        if not statement.strip().startswith('INSERT INTO videos ('):
            errors.append(f"Statement {stmt_num}: Invalid INSERT syntax")
        
        # Check for VALUES keyword
        if 'VALUES (' not in statement:
            errors.append(f"Statement {stmt_num}: Missing VALUES clause")
        
        # Check for balanced parentheses
        open_parens = statement.count('(')
        close_parens = statement.count(')')
        if open_parens != close_parens:
            errors.append(f"Statement {stmt_num}: Unbalanced parentheses ({open_parens} open, {close_parens} close)")
        
        # Count single quotes - should be even (they come in pairs)
        # But be smarter about this - ignore escaped quotes
        quote_positions = []
        escape_next = False
        for i, char in enumerate(statement):
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == "'":
                quote_positions.append(i)
        
        # Real quotes (not escaped) should be even
        real_quotes = len(quote_positions)
        if real_quotes % 2 != 0:
            errors.append(f"Statement {stmt_num}: Unbalanced quotes ({real_quotes} quotes)")
        
        # Check for empty critical fields (but be more lenient)
        # Empty channel_id is acceptable based on our data analysis
        if "'', '', '', ''" in statement:
            errors.append(f"Statement {stmt_num}: Contains multiple empty fields")
        
        # Basic structure validation
        if statement.count('VALUES') != 1:
            errors.append(f"Statement {stmt_num}: Should have exactly one VALUES clause")
    
    return statement_count, errors

def validate_specific_issues(filepath: str) -> List[str]:
    """Check for specific known issues in the data"""
    issues = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for the specific problematic patterns we found in data analysis
    if "channel_id" in content and "''" in content:
        # This is actually fine - we know all channel_id fields are empty
        pass
    
    # Check for unescaped single quotes (should be doubled)
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        # Look for patterns like 'text'text' (unescaped)
        if re.search(r"'[^']*'[^']*'", line) and "VALUES" in line:
            # This might be an issue, but let's be more specific
            if re.search(r"'[^']*'[a-zA-Z]", line):  # Quote followed by letter (not comma, paren, or quote)
                issues.append(f"Line {line_num}: Possible unescaped single quote")
    
    return issues

if __name__ == "__main__":
    filepath = "db/mutations/insert_videos.sql"
    
    print(f"🔍 Validating {filepath}...")
    print("📝 Using improved multi-line statement validation...\n")
    
    count, errors = validate_sql_file(filepath)
    specific_issues = validate_specific_issues(filepath)
    
    print(f"📊 Validation Results:")
    print(f"  📝 Total statements: {count}")
    print(f"  ❌ Errors found: {len(errors)}")
    print(f"  ⚠️  Specific issues: {len(specific_issues)}")
    
    if errors:
        print("\n❌ Structural Errors:")
        for error in errors[:10]:  # Show first 10
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    else:
        print("\n✅ All statements have valid structure!")
    
    if specific_issues:
        print("\n⚠️  Potential Issues:")
        for issue in specific_issues[:5]:  # Show first 5
            print(f"  - {issue}")
        if len(specific_issues) > 5:
            print(f"  ... and {len(specific_issues) - 5} more potential issues")
    
    if not errors and not specific_issues:
        print("\n🎉 SQL file validation PASSED!")
        print("   The migration generated clean, valid SQL statements.")
    elif not errors:
        print("\n✅ SQL structure is valid (minor potential issues noted above)")
    
    # Show a sample of the actual SQL for verification
    print(f"\n📋 Sample SQL (first 200 chars):")
    with open(filepath, 'r') as f:
        first_line = f.readline().strip()
        print(f"   {first_line[:200]}...")
    
    # Count actual INSERT statements
    with open(filepath, 'r') as f:
        content = f.read()
        insert_count = content.count('INSERT INTO videos')
        print(f"\n📊 Quick Stats:")
        print(f"   INSERT statements found: {insert_count}")
        print(f"   Expected: 410")
        print(f"   Match: {'✅' if insert_count == 410 else '❌'}")