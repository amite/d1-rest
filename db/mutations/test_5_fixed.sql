-- Fixed INSERT statements with explicit column specification
INSERT INTO videos (
    video_id, cleaned_title, cleaned_description, 
    channel_name, channel_id, published_at, 
    duration_seconds, view_count, like_count, 
    comment_count, is_indexed, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
