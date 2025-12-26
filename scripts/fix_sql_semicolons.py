#!/usr/bin/env python3
"""
Fix missing semicolons in SQL INSERT statements
"""

def fix_sql_file(input_file, output_file):
    """Add semicolons to INSERT statements that are missing them"""
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        line = line.rstrip()
        
        # Check if this line is an INSERT statement
        if line.strip().startswith('INSERT INTO videos'):
            # Add semicolon if not present
            if not line.strip().endswith(';'):
                line = line.rstrip() + ';'
        
        fixed_lines.append(line)
    
    # Write to output file
    with open(output_file, 'w') as f:
        for line in fixed_lines:
            f.write(line + '\n')
    
    print(f"✅ Fixed SQL file: {output_file}")
    print(f"   Total lines: {len(fixed_lines)}")

if __name__ == "__main__":
    input_file = "db/mutations/insert_videos_migrated.sql"
    output_file = "db/mutations/insert_videos_migrated_fixed.sql"
    
    print("🔧 Fixing missing semicolons in SQL file...")
    fix_sql_file(input_file, output_file)
    print("Done!")