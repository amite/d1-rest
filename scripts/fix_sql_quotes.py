#!/usr/bin/env python3
"""
Fix SQL statement quotes for remote D1 execution
"""
import re

def fix_sql_quotes(content):
    """
    Fix unescaped single quotes in SQL VALUES by doubling them
    """
    # Read line by line and fix each INSERT statement
    lines = content.split('\n')
    fixed_lines = []
    
    current_statement = ""
    in_values = False
    
    for line in lines:
        if line.strip().startswith("INSERT OR IGNORE INTO videos"):
            # Start of new statement
            if current_statement:
                fixed_lines.append(current_statement)
            current_statement = line
            in_values = True
        elif in_values:
            current_statement += "\n" + line
            if line.strip().endswith(';'):
                # End of statement, fix quotes in the VALUES part
                if "VALUES (" in current_statement:
                    # Extract VALUES part and fix quotes
                    parts = current_statement.split("VALUES (", 1)
                    if len(parts) == 2:
                        values_part = "VALUES (" + parts[1]
                        # Fix single quotes by doubling them
                        fixed_values = values_part.replace("'", "''")
                        current_statement = parts[0] + fixed_values
                
                fixed_lines.append(current_statement)
                current_statement = ""
                in_values = False
    
    # Add any remaining statement
    if current_statement:
        fixed_lines.append(current_statement)
    
    return "\n".join(fixed_lines)

def main():
    # Read the original file
    with open("db/mutations/insert_videos_migrated_ignore.sql", "r") as f:
        content = f.read()
    
    print("Fixing SQL quotes...")
    fixed_content = fix_sql_quotes(content)
    
    # Write the fixed content to a new file
    with open("db/mutations/insert_videos_migrated_fixed_quotes.sql", "w") as f:
        f.write(fixed_content)
    
    print("✅ Fixed SQL file saved to: db/mutations/insert_videos_migrated_fixed_quotes.sql")
    
    # Count the number of statements
    statement_count = fixed_content.count("INSERT OR IGNORE INTO videos")
    print(f"Total INSERT statements: {statement_count}")
    
    # Test with the first statement
    first_statement = fixed_content.split('\n')[0]
    print(f"\nFirst statement preview:")
    print(first_statement[:200] + "...")

if __name__ == "__main__":
    main()