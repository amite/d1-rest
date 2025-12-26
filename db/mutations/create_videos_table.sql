CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    cleaned_title TEXT,
    cleaned_description TEXT,
    channel_name TEXT,
    channel_id TEXT,
    published_at TIMESTAMP,
    duration_seconds INTEGER,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    is_indexed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);