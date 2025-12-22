# Generated migration to add public_id fields

import uuid
from django.db import migrations, models
from django.db import connection


def populate_public_ids(apps, schema_editor):
    College = apps.get_model('colleges', 'College')
    Branch = apps.get_model('colleges', 'Branch')
    
    # Check if fields already exist and have data
    with connection.cursor() as cursor:
        # Check if college.public_id column exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'college' 
            AND COLUMN_NAME = 'public_id'
        """)
        college_col_exists = cursor.fetchone()[0] > 0
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'branch' 
            AND COLUMN_NAME = 'public_id'
        """)
        branch_col_exists = cursor.fetchone()[0] > 0
    
    # If columns exist, clear any duplicate/invalid data first
    if college_col_exists:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE college SET public_id = NULL WHERE public_id IS NOT NULL")
    
    if branch_col_exists:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE branch SET public_id = NULL WHERE public_id IS NOT NULL")
    
    # Generate unique UUIDs for all colleges
    existing_uuids = set()
    for college in College.objects.all():
        if college.public_id is None:
            while True:
                new_uuid = uuid.uuid4()
                if new_uuid not in existing_uuids:
                    existing_uuids.add(new_uuid)
                    college.public_id = new_uuid
                    college.save(update_fields=['public_id'])
                    break
    
    # Generate unique UUIDs for all branches
    for branch in Branch.objects.all():
        if branch.public_id is None:
            while True:
                new_uuid = uuid.uuid4()
                if new_uuid not in existing_uuids:
                    existing_uuids.add(new_uuid)
                    branch.public_id = new_uuid
                    branch.save(update_fields=['public_id'])
                    break


def reverse_populate(apps, schema_editor):
    # No reverse needed - we'll just let the fields be removed
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('colleges', '0001_initial'),
    ]

    operations = [
        # Step 1: Add field as nullable and non-unique first (to avoid unique constraint violations)
        migrations.AddField(
            model_name='college',
            name='public_id',
            field=models.UUIDField(editable=False, null=True, unique=False, db_index=False),
        ),
        migrations.AddField(
            model_name='branch',
            name='public_id',
            field=models.UUIDField(editable=False, null=True, unique=False, db_index=False),
        ),
        # Step 2: Populate unique UUIDs for all existing records
        migrations.RunPython(populate_public_ids, reverse_populate),
        # Step 3: Make the field non-nullable and unique
        migrations.AlterField(
            model_name='college',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='branch',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]

