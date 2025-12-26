# Database Scripts

This directory contains SQL mutation files and scripts for managing the D1 database.

## Structure

```
db/
├── mutations/          # SQL mutation files
│   ├── create_users_table.sql
│   └── insert_users.sql
└── queries/            # SQL query files (for future use)
```

## Usage

### Using Nushell Scripts (Recommended)

The project includes convenient Nushell scripts in `utils/nu-scripts/`:

#### Create Users Table

```bash
# Create table in local database (default)
create-users-table

# Create table in remote database
create-users-table --remote
```

#### Insert Sample Users

```bash
# Insert users in local database (default)
insert-users

# Insert users in remote database
insert-users --remote
```

### Using TypeScript Scripts Directly

You can also use the TypeScript scripts directly:

```bash
# Create table in local database
tsx scripts/create_users_table.ts --local

# Create table in remote database
tsx scripts/create_users_table.ts --remote

# Insert users in local database
tsx scripts/insert_users.ts --local

# Insert users in remote database
tsx scripts/insert_users.ts --remote
```

### Using NPM Scripts

Convenient npm scripts are also available:

```bash
# Create table in local database
npm run db:create-table

# Create table in remote database
npm run db:create-table:remote

# Insert users in local database
npm run db:insert-users

# Insert users in remote database
npm run db:insert-users:remote
```

### Using Wrangler Directly

You can execute SQL files directly with Wrangler:

```bash
# Execute SQL file on local database
npx wrangler d1 execute cf-demo-db --local --file=db/mutations/create_users_table.sql

# Execute SQL file on remote database
npx wrangler d1 execute cf-demo-db --remote --file=db/mutations/insert_users.sql
```

## Available Scripts

| Script | Description | Local | Remote |
|--------|-------------|-------|--------|
| `create-users-table` | Create the users table | `create-users-table` | `create-users-table --remote` |
| `insert-users` | Insert sample users | `insert-users` | `insert-users --remote` |
| `npm run db:create-table` | Create the users table | `npm run db:create-table` | `npm run db:create-table:remote` |
| `npm run db:insert-users` | Insert sample users | `npm run db:insert-users` | `npm run db:insert-users:remote` |

## SQL Files

### `db/mutations/create_users_table.sql`

Creates the users table with the following schema:
- `id`: Auto-incrementing primary key
- `name`: User's name (required)
- `email`: User's email (required, unique)
- `age`: User's age (optional)
- `created_at`: Timestamp (auto-generated)

### `db/mutations/insert_users.sql`

Inserts three sample users:
1. John Doe (john@example.com, age 30)
2. Alice Smith (alice@example.com, age 25)
3. Bob Johnson (bob@example.com, age 35)

## Adding New Scripts

To add new database operations:

1. Create a SQL file in `db/mutations/` or `db/queries/`
2. Create a Python script in `scripts/` that executes the SQL
3. Create a Nushell wrapper in `utils/nu-scripts/` for easy command-line access

Example TypeScript script structure:

```typescript
#!/usr/bin/env node
/**
 * Description of what this script does
 * Usage: tsx scripts/your_script.ts [--local|--remote]
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

interface Args {
  local?: boolean;
  remote?: boolean;
}

function parseArgs(): Args {
  const args = process.argv.slice(2);
  const result: Args = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--local') result.local = true;
    if (arg === '--remote') result.remote = true;
  }

  return result;
}

function main() {
  const args = parseArgs();
  const isLocal = !args.remote;
  const flag = isLocal ? '--local' : '--remote';
  const dbName = 'cf-demo-db';

  // Your logic here
  ...
}

main();
```

Example Nushell wrapper:

```nu
#!/usr/bin/env nu
# Description of what this script does
# Usage: your-script [--local|--remote]

def main [
    --local = true,
    --remote = false
] {
    let flag = if $remote { "--remote" } else { "--local" }
    tsx scripts/your_script.ts $flag
}
```
