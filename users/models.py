from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.

GENDER_CHOICES = [
    ("MALE", "male"),
    ("FEMALE", "female")
    ]

USER_TYPES = [
    ("STUDENTS", "students"),
    ("STAFFS", "staffs"),
    ("ADMIN", "admin")
]

class UserManager(BaseUserManager):
    
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not password:
            raise ValueError("Password must be provided")
        user_id = extra_fields.pop('id', str(uuid.uuid4()))
        # Remove user_type from extra_fields to avoid conflict with hardcoded value
        extra_fields.pop('user_type', None)
        user = self.model(id=user_id, email=self.normalize_email(email), user_type="ADMIN", **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, firstname=None, lastname=None, **extra_fields):
        """
        Create and save a regular user.
        If user_type is not provided, defaults to STUDENTS.
        - For STUDENTS: student_id is required
        - For STAFFS: staff_id and phone are required
        """
        if email is None:
            raise TypeError("Users should have an Email")
        
        # Firstname and lastname are optional for admin operations
        firstname = firstname or extra_fields.get('firstname', '')
        lastname = lastname or extra_fields.get('lastname', '')
        
        # if not user assigned a user type, default to STUDENTS
        user_type = extra_fields.get('user_type', 'STUDENTS')
        if user_type == 'STUDENTS' and extra_fields.get('student_id') is None:
            raise TypeError("Students must have a student ID")
        
        if user_type == 'STAFFS':
            if not extra_fields.get('staff_id'):
                raise TypeError("Staff must have a staff ID")
            if not extra_fields.get('phone'):
                raise TypeError("Staff must have a phone number")

        user = self.model(firstname=firstname, lastname=lastname, email=self.normalize_email(email), **extra_fields)
        if user.user_type == 'STAFFS':
            user.id = extra_fields['staff_id']
        elif user.user_type == 'STUDENTS':
            user.id = extra_fields['student_id']
        else:
            user.id = str(uuid.uuid4())
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')

        if password is None:
            raise TypeError("Superusers must have a password.")

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(primary_key = True, editable = False, max_length = 100)
    is_verified = models.BooleanField(default = False)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    email = models.EmailField(max_length=255, unique = True)
    firstname = models.CharField(max_length = 100)
    lastname = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 15, unique = True, null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='STUDENTS')
    gender = models.CharField(max_length = 6, choices = GENDER_CHOICES, default='MALE')
    profile_picture = models.ImageField(upload_to='profile_picture/', null=True, blank=True)
    staff_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    student_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    objects = UserManager()

    def __str__(self):
        full_name = f"{self.firstname} {self.lastname}".strip()
        return f"{full_name} ({self.email})" if full_name else self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return{
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        }

    class Meta:
        db_table = "user"
