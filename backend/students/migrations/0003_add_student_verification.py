# Generated migration for StudentVerification model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_add_usn_and_verification'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentVerification',
            fields=[
                ('verification_id', models.AutoField(primary_key=True, serialize=False)),
                ('college_name', models.CharField(max_length=255)),
                ('student_name', models.CharField(max_length=255)),
                ('usn', models.CharField(max_length=50)),
                ('id_image', models.BinaryField()),
                ('college_score', models.FloatField()),
                ('name_score', models.FloatField()),
                ('usn_score', models.FloatField()),
                ('verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'student_verification',
                'managed': True,
            },
        ),
    ]

