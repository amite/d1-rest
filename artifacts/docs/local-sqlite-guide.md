# Local SQLite Database Guide

This guide explains how to create and use a local SQLite database to execute the same commands shown in the D1 learning guide.

## Overview

Cloudflare D1 is SQLite-based, which means you can use the same SQL commands locally for development and testing. This guide shows you three different approaches:

1. **npx wrangler Local D1** (Recommended) - Uses the same D1 interface as production
2. **SQLite CLI** - Direct access to SQLite database files
3. **Local REST API** - Run the Worker locally with the same endpoints

---

## Option 1: Using npx wrangler's Local D1 (Recommended)

This is the closest to production since it uses the same D1 interface and bindings.

### Create the Users Table

```bash
npx wrangler d1 execute cf-demo-db --local --command "CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    age INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);"
```

### Insert Users

#### Individual Inserts

```bash
# User 1
npx wrangler d1 execute cf-demo-db --local --command "INSERT INTO users (name, email, age) VALUES ('John Doe', 'john@example.com', 30);"

# User 2
npx wrangler d1 execute cf-demo-db --local --command "INSERT INTO users (name, email, age) VALUES ('Alice Smith', 'alice@example.com', 25);"

# User 3
npx wrangler d1 execute cf-demo-db --local --command "INSERT INTO users (name, email, age) VALUES ('Bob Johnson', 'bob@example.com', 35);"
```

#### Multiple Inserts in One Statement

You can execute multiple INSERT statements in a single command by separating them with semicolons:

```bash
npx wrangler d1 execute cf-demo-db --local --command "INSERT INTO users (name, email, age) VALUES ('John Doe', 'john@example.com', 30); INSERT INTO users (name, email, age) VALUES ('Alice Smith', 'alice@example.com', 25); INSERT INTO users (name, email, age) VALUES ('Bob Johnson', 'bob@example.com', 35);"
```

For better readability, you can use a multi-line command:

```bash
npx wrangler d1 execute cf-demo-db --local --command "
INSERT INTO users (name, email, age) VALUES ('John Doe', 'john@example.com', 30);
INSERT INTO users (name, email, age) VALUES ('Alice Smith', 'alice@example.com', 25);
INSERT INTO users (name, email, age) VALUES ('Bob Johnson', 'bob@example.com', 35);
"
```

#### Using a SQL File

For larger datasets, create a SQL file and execute it:

```bash
# Create a file named insert-users.sql
cat > insert-users.sql << 'EOF'
INSERT INTO users (name, email, age) VALUES ('John Doe', 'john@example.com', 30);
INSERT INTO users (name, email, age) VALUES ('Alice Smith', 'alice@example.com', 25);
INSERT INTO users (name, email, age) VALUES ('Bob Johnson', 'bob@example.com', 35);
EOF

# Execute the file
npx wrangler d1 execute cf-demo-db --local --file=insert-users.sql
```

#### Using UNION SELECT for Bulk Insert

Another approach is to use UNION SELECT to insert multiple rows in a single INSERT statement:

```bash
npx wrangler d1 execute cf-demo-db --local --command "
INSERT INTO users (name, email, age)
SELECT 'John Doe', 'john@example.com', 30
UNION ALL SELECT 'Alice Smith', 'alice@example.com', 25
UNION ALL SELECT 'Bob Johnson', 'bob@example.com', 35;
"
```

### Query Users

```bash
# Get all users
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users;"

# Get user by ID
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users WHERE id = 1;"

# Filter by age
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users WHERE age = 25;"

# Multiple filters
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users WHERE age = 30 AND name = 'John Doe';"
```

### Sort Users

```bash
# Sort by age ascending
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users ORDER BY age ASC;"

# Sort by name descending
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users ORDER BY name DESC;"
```

### Pagination

```bash
# Get first 2 users
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users LIMIT 2;"

# Skip first user, get next 2
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users LIMIT 2 OFFSET 1;"
```

### Combined Query

```bash
npx wrangler d1 execute cf-demo-db --local --command "SELECT * FROM users WHERE age = 25 ORDER BY name DESC LIMIT 10;"
```

### Update User

```bash
# Update age
npx wrangler d1 execute cf-demo-db --local --command "UPDATE users SET age = 31 WHERE id = 1;"

# Update multiple fields
npx wrangler d1 execute cf-demo-db --local --command "UPDATE users SET name = 'Alice Johnson', email = 'alice.johnson@example.com', age = 26 WHERE id = 2;"
```

### Delete User

```bash
npx wrangler d1 execute cf-demo-db --local --command "DELETE FROM users WHERE id = 3;"
```

### Verify Table Structure

```bash
# List all tables
npx wrangler d1 execute cf-demo-db --local --command "SELECT name FROM sqlite_master WHERE type='table';"

# Get table schema
npx wrangler d1 execute cf-demo-db --local --command "PRAGMA table_info(users);"
```

---

## Option 2: Using SQLite CLI Directly

This approach gives you direct access to SQLite database files without using npx wrangler.

### Install SQLite

```bash
# On Ubuntu/Debian
sudo apt-get install sqlite3

# On macOS
brew install sqlite

# On Windows
# Download from https://www.sqlite.org/download.html
```

### Create Database and Table

```bash
# Create a new database file
sqlite3 local-demo.db

# Inside the SQLite shell, create the table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    age INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

# Exit the shell
.quit
```

### Execute Commands (One-liners)

```bash
# Insert users
sqlite3 local-demo.db "INSERT INTO users (name, email, age) VALUES ('John Doe', 'john@example.com', 30);"
sqlite3 local-demo.db "INSERT INTO users (name, email, age) VALUES ('Alice Smith', 'alice@example.com', 25);"
sqlite3 local-demo.db "INSERT INTO users (name, email, age) VALUES ('Bob Johnson', 'bob@example.com', 35);"

# Query all users
sqlite3 local-demo.db "SELECT * FROM users;"

# Query with filter
sqlite3 local-demo.db "SELECT * FROM users WHERE age = 25;"

# Query with sorting
sqlite3 local-demo.db "SELECT * FROM users ORDER BY age ASC;"

# Query with pagination
sqlite3 local-demo.db "SELECT * FROM users LIMIT 2 OFFSET 1;"

# Update user
sqlite3 local-demo.db "UPDATE users SET age = 31 WHERE id = 1;"

# Delete user
sqlite3 local-demo.db "DELETE FROM users WHERE id = 3;"
```

### Interactive Mode

```bash
# Open database in interactive mode
sqlite3 local-demo.db

# Then execute commands directly
SELECT * FROM users;
INSERT INTO users (name, email, age) VALUES ('Jane Doe', 'jane@example.com', 28);
UPDATE users SET age = 29 WHERE id = 4;
DELETE FROM users WHERE id = 4;

# Exit
.quit
```

---

## Option 3: Using the REST API Locally

This approach lets you use the exact same REST API endpoints as production, but running locally.

### Authentication Setup for Local Development

Before starting the local server, you need to set up authentication. The REST API requires a Bearer token for all endpoints.

#### Create a Local Secret File

Create a `.dev.vars` file in the project root with your local secret:

```bash
# Create .dev.vars file
echo "LOCAL_SECRET=your-secret-value-here" > .dev.vars
```

Replace `your-secret-value-here` with a secure secret of your choice. This secret will be used for local development authentication.

**Important:** Add `.dev.vars` to your `.gitignore` file to prevent accidentally committing secrets:

```bash
echo ".dev.vars" >> .gitignore
```

#### How Authentication Works

The application supports two authentication methods:

1. **Local Development**: Uses the `LOCAL_SECRET` variable from `.dev.vars`
2. **Production**: Uses Cloudflare Secrets Store

The authentication middleware automatically detects which environment it's running in and uses the appropriate secret source.

### Start Local Development Server

```bash
npm run dev
```

This starts a local server (typically at `http://localhost:8787`) that uses the local D1 database and your local secret for authentication.

### Create Users via POST

```bash
# Create user 1
curl --location 'http://localhost:8787/rest/users' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
}'

# Create user 2
curl --location 'http://localhost:8787/rest/users' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Alice Smith",
    "email": "alice@example.com",
    "age": 25
}'

# Create user 3
curl --location 'http://localhost:8787/rest/users' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Bob Johnson",
    "email": "bob@example.com",
    "age": 35
}'
```

### Read Users via GET

```bash
# Get all users
curl --location 'http://localhost:8787/rest/users' \
--header 'Authorization: Bearer your-secret-value-here'

# Get user by ID
curl --location 'http://localhost:8787/rest/users/1' \
--header 'Authorization: Bearer your-secret-value-here'
```

### Filter and Sort Users

```bash
# Filter by age
curl --location 'http://localhost:8787/rest/users?age=25' \
--header 'Authorization: Bearer your-secret-value-here'

# Multiple filters
curl --location 'http://localhost:8787/rest/users?age=30&name=John%20Doe' \
--header 'Authorization: Bearer your-secret-value-here'

# Sort by age ascending
curl --location 'http://localhost:8787/rest/users?sort_by=age&order=asc' \
--header 'Authorization: Bearer your-secret-value-here'

# Sort by name descending
curl --location 'http://localhost:8787/rest/users?sort_by=name&order=desc' \
--header 'Authorization: Bearer your-secret-value-here'

# Pagination
curl --location 'http://localhost:8787/rest/users?limit=2' \
--header 'Authorization: Bearer your-secret-value-here'

curl --location 'http://localhost:8787/rest/users?limit=2&offset=1' \
--header 'Authorization: Bearer your-secret-value-here'

# Combined example
curl --location 'http://localhost:8787/rest/users?age=25&sort_by=name&order=desc&limit=10' \
--header 'Authorization: Bearer your-secret-value-here'
```

### Update User via PATCH

```bash
# Update age
curl --location --request PATCH 'http://localhost:8787/rest/users/1' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "age": 31
}'

# Update multiple fields
curl --location --request PATCH 'http://localhost:8787/rest/users/2' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Alice Johnson",
    "email": "alice.johnson@example.com",
    "age": 26
}'
```

### Delete User via DELETE

```bash
curl --location --request DELETE 'http://localhost:8787/rest/users/3' \
--header 'Authorization: Bearer your-secret-value-here'
```

### Raw SQL Queries via /query

```bash
# Complex query with parameters
curl --location 'http://localhost:8787/query' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "query": "SELECT * FROM users WHERE age > ? ORDER BY age DESC LIMIT ?;",
    "params": [25, 2]
}'

# Aggregate query
curl --location 'http://localhost:8787/query' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "query": "SELECT COUNT(*) as total_users, AVG(age) as avg_age FROM users;",
    "params": []
}'

# Search with LIKE
curl --location 'http://localhost:8787/query' \
--header 'Authorization: Bearer your-secret-value-here' \
--header 'Content-Type: application/json' \
--data '{
    "query": "SELECT * FROM users WHERE name LIKE ?;",
    "params": ["%John%"]
}'
```

---

## Comparison: Local vs Remote

| Aspect | Local Development | Remote Production |
|--------|-------------------|-------------------|
| **Command flag** | `--local` | `--remote` |
| **Database location** | `.npx wrangler/state/v3/d1/` | Cloudflare Edge |
| **REST API URL** | `http://localhost:8787` | `https://d1-rest.amite.workers.dev` |
| **SQL syntax** | Identical | Identical |
| **Performance** | Fast locally | Fast globally (edge) |
| **Replication** | None | Automatic across regions |
| **Persistence** | File on disk | Managed by Cloudflare |

---

## Architecture Diagram

```mermaid
graph TB
    subgraph "Local Development"
        A[Client] -->|HTTP| B[Local Worker<br/>npm run dev]
        B -->|env.DB binding| C[Local D1 DB<br/>.npx wrangler/state/]
        D[npx wrangler CLI] -->|--local flag| C
    end
    
    subgraph "Production"
        E[Client] -->|HTTP| F[Cloudflare Worker<br/>Deployed]
        F -->|env.DB binding| G[Remote D1 DB<br/>Cloudflare Edge]
        H[npx wrangler CLI] -->|--remote flag| G
    end
    
    style C fill:#e1f5e1
    style G fill:#ffe1e1
```

---

## Recommended Workflow

### Development Cycle

1. **Start local development server**
   ```bash
   npm run dev
   ```

2. **Create/modify tables locally**
   ```bash
   npx wrangler d1 execute cf-demo-db --local --command "YOUR_SQL"
   ```

3. **Test with REST API locally**
   ```bash
   curl http://localhost:8787/rest/users
   ```

4. **Deploy to production**
   ```bash
   npm run deploy
   ```

5. **Apply schema changes to production**
   ```bash
   npx wrangler d1 execute cf-demo-db --remote --command "YOUR_SQL"
   ```

### Best Practices

- **Always test locally first** - Use `--local` flag for development
- **Keep SQL in sync** - The same SQL works in both environments
- **Use version control** - Track your schema changes in migration files
- **Backup before production** - Export data before major changes

---

## Quick Reference Commands

### npx wrangler Commands

```bash
# Local development
npx wrangler d1 execute cf-demo-db --local --command "YOUR_SQL"
npm run dev

# Remote production
npx wrangler d1 execute cf-demo-db --remote --command "YOUR_SQL"
npm run deploy

# List databases
npx wrangler d1 list

# Create new database
npx wrangler d1 create <database-name>
```

### SQLite CLI Commands

```bash
# Create database
sqlite3 database.db

# Execute SQL from file
sqlite3 database.db < schema.sql

# Execute single command
sqlite3 database.db "SELECT * FROM users;"

# Export data
sqlite3 database.db ".dump users" > backup.sql

# Import data
sqlite3 database.db < backup.sql
```

### REST API Endpoints

| Operation | Method | Endpoint | Local URL |
|-----------|--------|----------|-----------|
| List | GET | `/rest/{table}` | `http://localhost:8787/rest/users` |
| Get One | GET | `/rest/{table}/{id}` | `http://localhost:8787/rest/users/1` |
| Create | POST | `/rest/{table}` | `http://localhost:8787/rest/users` |
| Update | PATCH | `/rest/{table}/{id}` | `http://localhost:8787/rest/users/1` |
| Delete | DELETE | `/rest/{table}/{id}` | `http://localhost:8787/rest/users/1` |
| Raw SQL | POST | `/query` | `http://localhost:8787/query` |

---

## Troubleshooting

### Authentication Setup (Fix for "Secret not found" Error)

If you encounter the error `Error: Secret "secret" not found`, this means the application is trying to access a Cloudflare Secrets Store secret that doesn't exist in your local environment.

#### Solution: Create a Local Secret File

1. Create a `.dev.vars` file in your project root:
   ```bash
   echo "LOCAL_SECRET=your-secret-value-here" > .dev.vars
   ```

2. Add `.dev.vars` to your `.gitignore`:
   ```bash
   echo ".dev.vars" >> .gitignore
   ```

3. Restart your wrangler dev server:
   ```bash
   npm run dev
   ```

4. Use the secret in your API requests:
   ```bash
   curl -H "Authorization: Bearer your-secret-value-here" http://localhost:8787/rest/users
   ```

#### How It Works

The application now supports dual authentication:
- **Local Development**: Uses `LOCAL_SECRET` from `.dev.vars`
- **Production**: Uses Cloudflare Secrets Store

The authentication middleware automatically detects the environment and uses the appropriate secret source.

### Common Issues

**Issue: "Database not found" error**
- Solution: Make sure you've created the database with `npx wrangler d1 create` or created the table first

**Issue: Local changes not reflected**
- Solution: Restart the dev server with `npm run dev` after making schema changes

**Issue: Permission denied on database file**
- Solution: Check file permissions on `.npx wrangler/state/v3/d1/` directory

**Issue: SQLite command not found**
- Solution: Install SQLite using your package manager (see installation section above)

**Issue: "Unauthorized" or "Secret not found" error**
- Solution: Make sure you've created a `.dev.vars` file with your local secret:
  ```bash
  echo "LOCAL_SECRET=your-secret-value-here" > .dev.vars
  ```
- Ensure the Authorization header matches your secret:
  ```bash
  curl -H "Authorization: Bearer your-secret-value-here"
  ```
- Restart the dev server after creating/updating `.dev.vars`

**Issue: 401 Unauthorized on all requests**
- Solution: Verify that your Authorization header matches the secret in `.dev.vars`
- Check that the `.dev.vars` file is in the project root directory
- Restart the wrangler dev server to pick up changes to `.dev.vars`

---

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [npx wrangler CLI Documentation](https://developers.cloudflare.com/workers/npx wrangler/)
- [D1 Learning Guide](../plans/d1-101-learning-guide.md)
