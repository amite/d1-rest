import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
import sys

class VideoMigration:
    def __init__(self, source_db: str, output_file: str, batch_size: int = 100):
        self.source_db = source_db
        self.output_file = output_file
        self.batch_size = batch_size
        self.errors = []
        
    def validate_row(self, row: Dict[str, Any]) -> tuple[bool, str]:
        """Validate a single row of data"""
        # Check required fields
        if not row.get('video_id'):
            return False, "Missing video_id"
        
        # Validate data types
        numeric_fields = ['duration_seconds', 'view_count', 'like_count', 'comment_count']
        for field in numeric_fields:
            if row.get(field) and not isinstance(row[field], (int, type(None))):
                return False, f"Invalid type for {field}"
        
        return True, ""
    
    def transform_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform row data (remove title and description)"""
        # Create new dict without title and description
        return {
            'video_id': row['video_id'],
            'cleaned_title': row.get('cleaned_title', ''),
            'cleaned_description': row.get('cleaned_description', ''),
            'channel_name': row.get('channel_name', ''),
            'channel_id': row.get('channel_id', ''),
            'published_at': row.get('published_at'),
            'duration_seconds': row.get('duration_seconds'),
            'view_count': row.get('view_count'),
            'like_count': row.get('like_count'),
            'comment_count': row.get('comment_count'),
            'is_indexed': row.get('is_indexed', 0),
            'created_at': row.get('created_at')
        }
    
    def escape_sql_string(self, value: Any) -> str:
        """Properly escape SQL strings"""
        if value is None:
            return 'NULL'
        if isinstance(value, (int, float)):
            return str(value)
        # Escape single quotes by doubling them
        return f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"
    
    def generate_insert_statement(self, row: Dict[str, Any]) -> str:
        """Generate a single INSERT statement"""
        columns = ', '.join(row.keys())
        values = ', '.join(self.escape_sql_string(v) for v in row.values())
        return f"INSERT INTO videos ({columns}) VALUES ({values});"
    
    def migrate(self) -> tuple[int, int]:
        """Execute the migration"""
        conn = sqlite3.connect(self.source_db)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()
        
        # Query all videos (excluding title and description)
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
        
        successful = 0
        failed = 0
        statements = []
        
        for row in cursor:
            row_dict = dict(row)
            
            # Validate
            is_valid, error_msg = self.validate_row(row_dict)
            if not is_valid:
                self.errors.append({
                    'video_id': row_dict.get('video_id', 'UNKNOWN'),
                    'error': error_msg
                })
                failed += 1
                continue
            
            # Transform
            transformed = self.transform_row(row_dict)
            
            # Generate SQL
            sql = self.generate_insert_statement(transformed)
            statements.append(sql)
            successful += 1
            
            # Write in batches to avoid memory issues
            if len(statements) >= self.batch_size:
                self._write_batch(statements)
                statements = []
        
        # Write remaining statements
        if statements:
            self._write_batch(statements)
        
        conn.close()
        
        return successful, failed
    
    def _write_batch(self, statements: List[str]):
        """Write a batch of statements to file"""
        mode = 'a' if Path(self.output_file).exists() else 'w'
        with open(self.output_file, mode) as f:
            f.write('\n'.join(statements) + '\n')
    
    def report_errors(self):
        """Generate error report"""
        if not self.errors:
            print("✅ No errors!")
            return
        
        print(f"\n❌ {len(self.errors)} rows failed validation:\n")
        for error in self.errors[:10]:  # Show first 10
            print(f"  - video_id: {error['video_id']}")
            print(f"    error: {error['error']}\n")
        
        if len(self.errors) > 10:
            print(f"  ... and {len(self.errors) - 10} more errors")

if __name__ == "__main__":
    migrator = VideoMigration(
        source_db="db/videos.db",
        output_file="db/mutations/insert_videos_migrated.sql",
        batch_size=100
    )
    
    print("🚀 Starting migration...")
    successful, failed = migrator.migrate()
    
    print(f"\n📊 Migration Results:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Output: {migrator.output_file}")
    
    migrator.report_errors()
    
    # Exit with error code if any failures
    sys.exit(1 if failed > 0 else 0)