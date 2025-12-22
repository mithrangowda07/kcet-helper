"""
Script to fix the database state after a failed migration.
This will remove any partially created public_id columns so the migration can run cleanly.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kcet_eduguide.settings')
django.setup()

from django.db import connection

def fix_database():
    """Remove partially created public_id columns if they exist"""
    with connection.cursor() as cursor:
        # Check if college.public_id exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'college' 
            AND COLUMN_NAME = 'public_id'
        """)
        college_col_exists = cursor.fetchone()[0] > 0
        
        # Check if branch.public_id exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'branch' 
            AND COLUMN_NAME = 'public_id'
        """)
        branch_col_exists = cursor.fetchone()[0] > 0
        
        if college_col_exists:
            print("Removing public_id column from college table...")
            try:
                # Try to drop index (check first if it exists)
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.STATISTICS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'college' 
                    AND INDEX_NAME IN ('college_public_id_unique', 'college_public_id_idx')
                """)
                if cursor.fetchone()[0] > 0:
                    cursor.execute("ALTER TABLE college DROP INDEX college_public_id_unique")
                    cursor.execute("ALTER TABLE college DROP INDEX college_public_id_idx")
            except Exception as e:
                print(f"Note (index drop): {e}")
            
            # Drop the column (MySQL doesn't support IF EXISTS for DROP COLUMN)
            try:
                cursor.execute("ALTER TABLE college DROP COLUMN public_id")
                print("✓ Removed public_id from college table")
            except Exception as e:
                print(f"Note: {e}")
        
        if branch_col_exists:
            print("Removing public_id column from branch table...")
            try:
                # Try to drop index (check first if it exists)
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.STATISTICS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'branch' 
                    AND INDEX_NAME IN ('branch_public_id_unique', 'branch_public_id_idx')
                """)
                if cursor.fetchone()[0] > 0:
                    cursor.execute("ALTER TABLE branch DROP INDEX branch_public_id_unique")
                    cursor.execute("ALTER TABLE branch DROP INDEX branch_public_id_idx")
            except Exception as e:
                print(f"Note (index drop): {e}")
            
            # Drop the column (MySQL doesn't support IF EXISTS for DROP COLUMN)
            try:
                cursor.execute("ALTER TABLE branch DROP COLUMN public_id")
                print("✓ Removed public_id from branch table")
            except Exception as e:
                print(f"Note: {e}")
        
        if not college_col_exists and not branch_col_exists:
            print("No public_id columns found. Database is clean.")
        else:
            print("\n✓ Database cleaned. You can now run migrations again.")
            print("Run: python manage.py migrate")

if __name__ == '__main__':
    print("Fixing database state...\n")
    try:
        fix_database()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

