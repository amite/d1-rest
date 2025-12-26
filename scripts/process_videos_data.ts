import * as fs from 'fs';
import * as path from 'path';

// Read the pipe-delimited data
const inputFile = path.join(__dirname, '../db/mutations/insert_videos.sql');
const outputFile = path.join(__dirname, '../db/mutations/insert_videos_clean.sql');

const data = fs.readFileSync(inputFile, 'utf-8');
// Lines are separated by $, not newlines
const lines = data.trim().split('$');

// Columns to keep (removing title at index 1 and description at index 3)
// Original columns: video_id, title, cleaned_title, description, cleaned_description, channel_name, channel_id, published_at, duration_seconds, view_count, like_count, comment_count, is_indexed, created_at
// Keep: video_id, cleaned_title, cleaned_description, channel_name, channel_id, published_at, duration_seconds, view_count, like_count, comment_count, is_indexed, created_at

const insertStatements: string[] = [];

for (const line of lines) {
    if (!line.trim()) continue;

    const columns = line.split('|');

    // Remove title (index 1) and description (index 3)
    const filteredColumns = columns.filter((_, index) => index !== 1 && index !== 3);

    const [
        video_id,
        cleaned_title,
        cleaned_description,
        channel_name,
        channel_id,
        published_at,
        duration_seconds,
        view_count,
        like_count,
        comment_count,
        is_indexed,
        created_at
    ] = filteredColumns;

    // Escape single quotes in text fields
    const escape = (val: string) => val ? val.replace(/'/g, "''") : '';

    const stmt = `INSERT INTO videos (video_id, cleaned_title, cleaned_description, channel_name, channel_id, published_at, duration_seconds, view_count, like_count, comment_count, is_indexed, created_at) VALUES ('${escape(video_id)}', '${escape(cleaned_title)}', '${escape(cleaned_description)}', '${escape(channel_name)}', '${escape(channel_id)}', '${escape(published_at)}', ${duration_seconds || 'NULL'}, ${view_count || 'NULL'}, ${like_count || 'NULL'}, ${comment_count || 'NULL'}, ${is_indexed || '0'}, '${escape(created_at)}');`;

    insertStatements.push(stmt);
}

// Write to output file
fs.writeFileSync(outputFile, insertStatements.join('\n'), 'utf-8');

console.log(`Processed ${insertStatements.length} records`);
console.log(`Output written to: ${outputFile}`);
