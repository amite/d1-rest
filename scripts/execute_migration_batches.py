#!/usr/bin/env python3
"""
Execute D1 migration in smaller batches to avoid command line size limits
"""
import subprocess
import sys

def execute_batch(batch_sql, batch_num, total_batches):
    """Execute a batch of SQL statements"""
    print(f"Executing batch {batch_num}/{total_batches}...")
    
    try:
        # Create a temporary file for this batch
        temp_file = f"/tmp/batch_{batch_num}.sql"
        with open(temp_file, 'w') as f:
            f.write(batch_sql)
        
        # Execute the batch using the file approach
        cmd = [
            "npx", "wrangler", "d1", "execute", "cf-demo-db", 
            "--file=" + temp_file, "--remote"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Batch {batch_num} executed successfully")
            return True
        else:
            print(f"❌ Batch {batch_num} failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing batch {batch_num}: {e}")
        return False

def main():
    # Read the complete SQL file
    with open("db/mutations/insert_videos_migrated_ignore.sql", "r") as f:
        content = f.read()
    
    # Split into individual INSERT statements
    statements = [stmt.strip() for stmt in content.split("INSERT OR IGNORE INTO videos") if stmt.strip()]
    
    # Add "INSERT OR IGNORE INTO videos" back to each statement
    statements = ["INSERT OR IGNORE INTO videos" + stmt for stmt in statements]
    
    print(f"Total INSERT statements to execute: {len(statements)}")
    
    # Process in batches of 50
    batch_size = 50
    total_batches = (len(statements) + batch_size - 1) // batch_size
    
    success_count = 0
    
    for i in range(0, len(statements), batch_size):
        batch_num = (i // batch_size) + 1
        batch = statements[i:i + batch_size]
        batch_sql = "\n".join(batch)
        
        if execute_batch(batch_sql, batch_num, total_batches):
            success_count += 1
        else:
            print(f"Stopping execution due to batch {batch_num} failure")
            break
    
    print(f"\nMigration Summary:")
    print(f"Total batches: {total_batches}")
    print(f"Successful batches: {success_count}")
    print(f"Failed batches: {total_batches - success_count}")
    
    if success_count == total_batches:
        print("🎉 All batches executed successfully!")
        return True
    else:
        print("⚠️ Some batches failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)