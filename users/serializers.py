from rest_framework import serializers
from .models import CustomUser
from rest_framework.exceptions import AuthenticationFailed
import uuid

class SignUpSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    email = serializers.EmailField()
    confirm_email = serializers.EmailField(write_only=True)
    password = serializers.CharField(min_length=8, max_length=68, write_only=True)
    phone = serializers.CharField()
    gender = serializers.ChoiceField(choices=["MALE", "FEMALE"])
    user_type = serializers.ChoiceField(choices=["STUDENTS", "STAFFS", "ADMIN"])
    profile_picture = serializers.ImageField(required=False)
    staff_id = serializers.CharField(required=False, allow_blank=True)
    student_id = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname',  'email', 'confirm_email', 'password', 'phone',  'gender', 'user_type', 'profile_picture', 'staff_id', 'student_id']

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        confirm_email = attrs.get('confirm_email', '').lower()

        if email != confirm_email:
            raise serializers.ValidationError({'confirm_email': 'Email addresses do not match'})

        attrs['email'] = email
        user_type = attrs.get('user_type')
        if user_type == 'STUDENTS':
            if not attrs.get('student_id'):
                raise serializers.ValidationError("Student ID is required for students")
        elif user_type == 'STAFFS':
            if not attrs.get('staff_id'):
                raise serializers.ValidationError("Staff ID is required for staff")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_email', None)
        password = validated_data.pop('password')
        user_type = validated_data.get('user_type', 'STUDENTS')
        
        user = CustomUser(**validated_data)
        user.set_password(password)
        
        # Set ID based on user type
        if user_type == 'STAFFS':
            user.id = validated_data.get('staff_id')
        elif user_type == 'STUDENTS':
            user.id = validated_data.get('student_id')
        else:
            user.id = str(uuid.uuid4())
        
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates email and password, returns JWT tokens if valid.
    """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(min_length=8, max_length=68, write_only=True)
    
    # Output fields  
    id = serializers.CharField(read_only=True, required=False)
    user_type = serializers.CharField(read_only=True, required=False)
    tokens = serializers.DictField(read_only=True, required=False)

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        # Check if user exists with this email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password")

        # Check if password is correct
        if not user.check_password(password):
            raise AuthenticationFailed("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            if not user.is_verified:
                raise AuthenticationFailed("Please verify your email before signing in")
            raise AuthenticationFailed("User account is inactive")

        # Add output data to validated_data
        attrs['id'] = user.id
        attrs['email'] = user.email
        attrs['user_type'] = user.user_type
        tokens = user.tokens()
        attrs['tokens'] = {
            "access": str(tokens['access']),
            "refresh": str(tokens['refresh'])
        }
        
        return attrs
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'firstname',
            'lastname',
            'email',
            'phone',
            'gender',
            'user_type',
            'profile_picture',
            'staff_id',
            'student_id',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, max_length=68, write_only=True)
    confirm_password = serializers.CharField(min_length=8, max_length=68, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user

        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError({'current_password': 'Current password is incorrect.'})

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'New passwords do not match.'})

        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'New password must be different from current password.'})

        return attrs


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError({'password': 'Password is incorrect.'})
        return attrs


class UpdateProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = ['profile_picture']
