#!/usr/bin/env nu
# Create the users table in D1 database
# Usage: create-users-table [--local|--remote]

def main [
    --local = true,  # Execute on local database (default)
    --remote = false  # Execute on remote database
] {
    let flag = if $remote { "--remote" } else { "--local" }
    
    print $"Creating users table in (if $remote { 'remote' } else { 'local' }) database..."
    
    tsx scripts/create_users_table.ts $flag
}
