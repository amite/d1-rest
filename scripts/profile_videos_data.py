#!/usr/bin/env python3
"""Profile the videos data to understand its structure"""
import sqlite3
import json

def profile_videos_table(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get schema
    cursor.execute("PRAGMA table_info(videos)")
    schema = cursor.fetchall()
    
    print("📋 Table Schema:")
    for col in schema:
        print(f"  {col[1]}: {col[2]} {'(PK)' if col[5] else ''}")
    
    # Get row count
    cursor.execute("SELECT COUNT(*) FROM videos")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total Records: {total:,}")
    
    # Check for NULLs in each column
    print("\n🔍 NULL Value Analysis:")
    for col in schema:
        col_name = col[1]
        cursor.execute(f"SELECT COUNT(*) FROM videos WHERE {col_name} IS NULL")
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"  {col_name}: {null_count:,} NULLs ({null_count/total*100:.1f}%)")
        else:
            print(f"  {col_name}: 0 NULLs ✅")
    
    # Check for empty strings
    print("\n📝 Empty String Analysis:")
    text_columns = ['cleaned_title', 'cleaned_description', 'channel_name', 'channel_id']
    for col in text_columns:
        cursor.execute(f"SELECT COUNT(*) FROM videos WHERE {col} = ''")
        empty_count = cursor.fetchone()[0]
        if empty_count > 0:
            print(f"  {col}: {empty_count:,} empty ({empty_count/total*100:.1f}%)")
        else:
            print(f"  {col}: 0 empty ✅")
    
    # Check for problematic characters
    print("\n⚠️  Problematic Characters Analysis:")
    cursor.execute("SELECT COUNT(*) FROM videos WHERE cleaned_title LIKE '%''%' OR cleaned_description LIKE '%''%'")
    quote_count = cursor.fetchone()[0]
    print(f"  Single quotes in text: {quote_count:,} rows ({quote_count/total*100:.1f}%)")
    
    cursor.execute("SELECT COUNT(*) FROM videos WHERE cleaned_title LIKE '%\"%' OR cleaned_description LIKE '%\"%'")
    dquote_count = cursor.fetchone()[0]
    print(f"  Double quotes in text: {dquote_count:,} rows ({dquote_count/total*100:.1f}%)")
    
    # Check text lengths
    print("\n📏 Text Length Analysis:")
    cursor.execute("SELECT AVG(LENGTH(cleaned_title)), MAX(LENGTH(cleaned_title)) FROM videos")
    avg_title_len, max_title_len = cursor.fetchone()
    print(f"  cleaned_title: avg={avg_title_len:.1f} chars, max={max_title_len:,} chars")
    
    cursor.execute("SELECT AVG(LENGTH(cleaned_description)), MAX(LENGTH(cleaned_description)) FROM videos")
    avg_desc_len, max_desc_len = cursor.fetchone()
    print(f"  cleaned_description: avg={avg_desc_len:.1f} chars, max={max_desc_len:,} chars")
    
    # Sample problematic rows
    print("\n⚠️  Sample Rows with Issues:")
    cursor.execute("""
        SELECT video_id, cleaned_title, channel_name 
        FROM videos 
        WHERE cleaned_title LIKE '%''%' OR cleaned_description LIKE '%''%'
        LIMIT 3
    """)
    for row in cursor.fetchall():
        print(f"  video_id: {row[0]}")
        print(f"    title: '{row[1][:100]}...'")
        print(f"    channel: '{row[2]}'")
    
    # Data distribution
    print("\n📈 Data Distribution:")
    cursor.execute("SELECT COUNT(DISTINCT channel_id) FROM videos")
    unique_channels = cursor.fetchone()[0]
    print(f"  Unique channels: {unique_channels}")
    
    cursor.execute("SELECT AVG(duration_seconds), MAX(duration_seconds), MIN(duration_seconds) FROM videos")
    avg_dur, max_dur, min_dur = cursor.fetchone()
    print(f"  Duration: avg={avg_dur:.1f}s, max={max_dur:,}s, min={min_dur:,}s")
    
    cursor.execute("SELECT AVG(view_count), MAX(view_count) FROM videos")
    avg_views, max_views = cursor.fetchone()
    print(f"  Views: avg={avg_views:,.0f}, max={max_views:,}")
    
    conn.close()

if __name__ == "__main__":
    profile_videos_table("db/videos.db")