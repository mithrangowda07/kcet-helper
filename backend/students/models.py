from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from colleges.models import Branch


class StudentCounter(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'student_counter'
        managed = True


class Student(AbstractBaseUser, PermissionsMixin):
    STUDENT_TYPE_CHOICES = [
        ('counselling', 'Counselling'),
        ('studying', 'Studying'),
    ]

    student_user_id = models.CharField(max_length=20, primary_key=True)
    type_of_student = models.CharField(max_length=20, choices=STUDENT_TYPE_CHOICES)
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=10, null=True, blank=True)
    unique_key = models.ForeignKey(
        Branch, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='unique_key'
    )
    year_of_starting = models.IntegerField(null=True, blank=True)
    college_code = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    email_id = models.EmailField(unique=True, max_length=100)
    kcet_rank = models.IntegerField(null=True, blank=True)
    hashed_password = models.CharField(max_length=255, db_column='hashed_password')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    profile_completed = models.BooleanField(default=False)
    usn = models.CharField(max_length=50, null=True, blank=True, unique=True)
    is_verified_student = models.BooleanField(default=False)
    id_card_image = models.BinaryField(null=True, blank=True)  # Store image as binary data in MySQL LONGBLOB

    USERNAME_FIELD = 'email_id'
    REQUIRED_FIELDS = ['phone_number', 'type_of_student']
    
    class Meta:
        db_table = 'student'
        managed = True
    
    # Add id property for compatibility with JWT and other Django features
    @property
    def id(self):
        return self.student_user_id
    
    @property
    def password(self):
        return self.hashed_password
    
    @password.setter
    def password(self, value):
        # Let Django's built-in helpers (set_password) handle hashing; here we
        # simply mirror whatever value AbstractBaseUser assigns.
        self.hashed_password = value

    def save(self, *args, **kwargs):
        # Generate student_user_id if not set
        if not self.student_user_id:
            self.student_user_id = self._generate_student_id()
        
        # Handle password field mapping: Django's AbstractBaseUser uses 'password'
        # but our model uses 'hashed_password' as the database field
        if 'update_fields' in kwargs and 'password' in kwargs['update_fields']:
            # Replace 'password' with 'hashed_password' in update_fields
            update_fields = list(kwargs['update_fields'])
            update_fields.remove('password')
            update_fields.append('hashed_password')
            kwargs['update_fields'] = update_fields
        
        super().save(*args, **kwargs)

    def _generate_student_id(self):
        """Generate student_user_id based on type_of_student"""
        # Insert into student_counter to get next ID
        counter = StudentCounter.objects.create()
        next_id = counter.id
        
        if self.type_of_student == 'counselling':
            # Format: YYYYNNNNNN
            current_year = timezone.now().year
            return f"{current_year}{next_id:06d}"
        elif self.type_of_student == 'studying':
            # Format: <college_code><NNNNNN>
            if not self.college_code:
                raise ValueError("college_code is required for studying students")
            return f"{self.college_code}{next_id:06d}"
        else:
            raise ValueError(f"Invalid type_of_student: {self.type_of_student}")

    def __str__(self):
        return f"{self.student_user_id} - {self.email_id}"


class StudentVerification(models.Model):
    """Model to store student verification data including the ID image"""
    verification_id = models.AutoField(primary_key=True)
    college_name = models.CharField(max_length=255)
    student_name = models.CharField(max_length=255)
    usn = models.CharField(max_length=50)
    id_image = models.BinaryField()  # Store image as binary data in MySQL
    college_score = models.FloatField()
    name_score = models.FloatField()
    usn_score = models.FloatField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_verification'
        managed = True
