#!/usr/bin/env nu
# Insert sample users into the D1 database
# Usage: insert-users [--local|--remote]

def main [
    --local = true,  # Execute on local database (default)
    --remote = false  # Execute on remote database
] {
    let flag = if $remote { "--remote" } else { "--local" }
    
    print $"Inserting users into (if $remote { 'remote' } else { 'local' }) database..."
    
    tsx scripts/insert_users.ts $flag
}
