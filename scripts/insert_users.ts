#!/usr/bin/env node
/**
 * Insert sample users into the D1 database
 * Usage: tsx scripts/insert_users.ts [--local|--remote]
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

    // Read SQL from file
    const sqlPath = join(process.cwd(), 'db/mutations/insert_users.sql');

    if (!existsSync(sqlPath)) {
        console.error(`✗ SQL file not found: ${sqlPath}`);
        process.exit(1);
    }

    const sql = readFileSync(sqlPath, 'utf-8');

    console.log(`Inserting users into ${isLocal ? 'local' : 'remote'} database...`);
    console.log(`Database: ${dbName}`);
    console.log();

    try {
        const cmd = `npx wrangler d1 execute ${dbName} ${flag} --file "${sqlPath}"`;
        const output = execSync(cmd, { encoding: 'utf-8', stdio: 'pipe' });
        console.log(output);
        console.log('✓ Users inserted successfully!');
    } catch (error: any) {
        console.error(`✗ Error inserting users: ${error.message}`);
        if (error.stdout) console.error(error.stdout);
        if (error.stderr) console.error(error.stderr);
        process.exit(1);
    }
}

main();
