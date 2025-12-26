#!/usr/bin/env python3
"""
REST API-based migration script for moving videos from SQLite to D1
Uses the REST API endpoints to insert data in batches
"""

import sqlite3
import requests
import json
import time
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class D1VideoMigration:
    def __init__(self, source_db: str, api_url: str, auth_token: str, batch_size: int = 50):
        self.source_db = source_db
        self.api_url = api_url.rstrip('/')
        self.auth_token = auth_token
        self.batch_size = batch_size
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        self.errors = []
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
    def validate_row(self, row: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a single row of data"""
        if not row.get('video_id'):
            return False, "Missing video_id"
        
        # Validate data types
        numeric_fields = ['duration_seconds', 'view_count', 'like_count', 'comment_count']
        for field in numeric_fields:
            value = row.get(field)
            if value is not None and not isinstance(value, (int, float)):
                return False, f"Invalid type for {field}: {type(value)}"
        
        return True, ""
    
    def transform_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform row data to match D1 schema"""
        return {
            'video_id': row['video_id'],
            'cleaned_title': row.get('cleaned_title', '') or '',
            'cleaned_description': row.get('cleaned_description', '') or '',
            'channel_name': row.get('channel_name', '') or '',
            'channel_id': row.get('channel_id', '') or '',
            'published_at': row.get('published_at'),
            'duration_seconds': row.get('duration_seconds'),
            'view_count': row.get('view_count'),
            'like_count': row.get('like_count'),
            'comment_count': row.get('comment_count'),
            'is_indexed': bool(row.get('is_indexed', 0)),
            'created_at': row.get('created_at')
        }
    
    def check_video_exists(self, video_id: str) -> bool:
        """Check if a video already exists in D1"""
        query = "SELECT COUNT(*) as count FROM videos WHERE video_id = ?"
        payload = {
            'query': query,
            'params': [video_id]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/query",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                count = result.get('results', [{}])[0].get('count', 0)
                return count > 0
            else:
                logger.warning(f"Failed to check existence for {video_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"Error checking existence for {video_id}: {e}")
            return False
    
    def insert_video_batch(self, videos: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Insert a batch of videos using the REST API"""
        successful = 0
        failed = 0
        
        for video in videos:
            try:
                # Check if video already exists
                if self.check_video_exists(video['video_id']):
                    logger.info(f"Skipping existing video: {video['video_id']}")
                    self.stats['skipped'] += 1
                    continue
                
                response = requests.post(
                    f"{self.api_url}/rest/videos",
                    headers=self.headers,
                    json=video,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    successful += 1
                    logger.debug(f"Successfully inserted video: {video['video_id']}")
                else:
                    failed += 1
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.errors.append({
                        'video_id': video['video_id'],
                        'error': error_msg
                    })
                    logger.error(f"Failed to insert video {video['video_id']}: {error_msg}")
                    
            except Exception as e:
                failed += 1
                error_msg = str(e)
                self.errors.append({
                    'video_id': video['video_id'],
                    'error': error_msg
                })
                logger.error(f"Error inserting video {video['video_id']}: {error_msg}")
        
        return successful, failed
    
    def fetch_videos_from_sqlite(self) -> List[Dict[str, Any]]:
        """Fetch all videos from SQLite database"""
        logger.info(f"Fetching videos from {self.source_db}")
        conn = sqlite3.connect(self.source_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query all videos with the same structure as D1
        cursor.execute("""
            SELECT 
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
            FROM videos
            ORDER BY created_at DESC
        """)
        
        videos = []
        for row in cursor:
            video = dict(row)
            videos.append(video)
        
        conn.close()
        logger.info(f"Fetched {len(videos)} videos from SQLite")
        return videos
    
    def migrate(self) -> Dict[str, int]:
        """Execute the complete migration"""
        logger.info("Starting D1 video migration via REST API")
        
        # Fetch all videos from SQLite
        videos = self.fetch_videos_from_sqlite()
        self.stats['total'] = len(videos)
        
        if not videos:
            logger.warning("No videos found to migrate")
            return self.stats
        
        # Process videos in batches
        for i in range(0, len(videos), self.batch_size):
            batch = videos[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(videos) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} videos)")
            
            # Validate and transform batch
            valid_videos = []
            for video in batch:
                is_valid, error_msg = self.validate_row(video)
                if is_valid:
                    transformed = self.transform_row(video)
                    valid_videos.append(transformed)
                else:
                    self.stats['failed'] += 1
                    self.errors.append({
                        'video_id': video.get('video_id', 'UNKNOWN'),
                        'error': error_msg
                    })
                    logger.error(f"Validation failed for video {video.get('video_id')}: {error_msg}")
            
            if valid_videos:
                # Insert batch
                batch_successful, batch_failed = self.insert_video_batch(valid_videos)
                self.stats['successful'] += batch_successful
                self.stats['failed'] += batch_failed
                
                logger.info(f"Batch {batch_num} completed: {batch_successful} successful, {batch_failed} failed")
            
            # Rate limiting - small delay between batches
            if i + self.batch_size < len(videos):
                time.sleep(0.5)
        
        return self.stats
    
    def report_results(self):
        """Generate comprehensive migration report"""
        logger.info("\n" + "="*60)
        logger.info("MIGRATION RESULTS")
        logger.info("="*60)
        logger.info(f"Total videos processed: {self.stats['total']}")
        logger.info(f"Successfully migrated: {self.stats['successful']}")
        logger.info(f"Failed migrations: {self.stats['failed']}")
        logger.info(f"Skipped (already exist): {self.stats['skipped']}")
        
        if self.stats['total'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total']) * 100
            logger.info(f"Success rate: {success_rate:.1f}%")
        
        if self.errors:
            logger.info(f"\nERRORS ({len(self.errors)} total):")
            logger.info("-" * 40)
            for i, error in enumerate(self.errors[:10]):  # Show first 10 errors
                logger.info(f"{i+1}. video_id: {error['video_id']}")
                logger.info(f"   error: {error['error']}")
            
            if len(self.errors) > 10:
                logger.info(f"   ... and {len(self.errors) - 10} more errors")
        
        logger.info("="*60)
        
        # Save error report to file
        if self.errors:
            error_report_file = f"scripts/migration_errors_{self.api_url.replace('https://', '').replace('http://', '').replace('.workers.dev', '').replace('localhost:8787', 'local')}.json"
            with open(error_report_file, 'w') as f:
                json.dump(self.errors, f, indent=2)
            logger.info(f"Error report saved to: {error_report_file}")

def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate videos from SQLite to D1')
    parser.add_argument('--env', choices=['local', 'production'], default='local',
                       help='Target environment (default: local)')
    parser.add_argument('--batch-size', type=int, default=25,
                       help='Batch size for migration (default: 25)')
    
    args = parser.parse_args()
    
    # Configuration based on environment
    if args.env == 'production':
        source_db = "db/videos.db"
        api_url = "https://d1-rest.amite.workers.dev"
        auth_token = "**********"  # Production token
        environment = "PRODUCTION"
    else:
        source_db = "db/videos.db"
        api_url = "http://localhost:8787"
        auth_token = "my-test-secret-123"  # Local development secret
        environment = "LOCAL"
    
    batch_size = args.batch_size
    
    logger.info("D1 Video Migration via REST API")
    logger.info("="*50)
    logger.info(f"Environment: {environment}")
    logger.info(f"Source: {source_db}")
    logger.info(f"API URL: {api_url}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Auth token: {auth_token[:20]}...")
    logger.info("="*50)
    
    try:
        # Initialize migration
        migrator = D1VideoMigration(
            source_db=source_db,
            api_url=api_url,
            auth_token=auth_token,
            batch_size=batch_size
        )
        
        # Execute migration
        stats = migrator.migrate()
        
        # Report results
        migrator.report_results()
        
        # Exit with appropriate code
        if stats['failed'] > 0:
            logger.error(f"Migration completed with {stats['failed']} failures")
            sys.exit(1)
        else:
            logger.info("Migration completed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()