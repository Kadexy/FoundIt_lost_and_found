from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
import uuid
from .models import CustomUser


class CustomUserCreationForm(forms.ModelForm):
    """Form for creating a new user in admin"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'firstname', 'lastname', 'phone', 'gender', 'user_type', 'student_id', 'staff_id', 'is_active')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        student_id = cleaned_data.get('student_id')
        staff_id = cleaned_data.get('staff_id')

        if user_type == 'STUDENTS' and not student_id:
            raise forms.ValidationError("Students must have a student ID")
        
        if user_type == 'STAFFS':
            if not staff_id:
                raise forms.ValidationError("Staff must have a staff ID")
            if not cleaned_data.get('phone'):
                raise forms.ValidationError("Staff must have a phone number")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        # Set the ID based on user type
        if user.user_type == 'STAFFS':
            user.id = self.cleaned_data.get('staff_id')
        elif user.user_type == 'STUDENTS':
            user.id = self.cleaned_data.get('student_id')
        else:
            user.id = str(uuid.uuid4())
        
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """Form for editing an existing user in admin"""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Leave blank to keep the current password'
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'firstname', 'lastname', 'phone', 'gender', 'user_type', 'student_id', 'staff_id', 'is_active', 'is_staff', 'is_superuser')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        student_id = cleaned_data.get('student_id')
        staff_id = cleaned_data.get('staff_id')

        if user_type == 'STUDENTS' and not student_id:
            raise forms.ValidationError("Students must have a student ID")
        
        if user_type == 'STAFFS':
            if not staff_id:
                raise forms.ValidationError("Staff must have a staff ID")
            if not cleaned_data.get('phone'):
                raise forms.ValidationError("Staff must have a phone number")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        # Update ID if user_type or ID fields changed
        if user.user_type == 'STAFFS' and self.cleaned_data.get('staff_id'):
            user.id = self.cleaned_data.get('staff_id')
        elif user.user_type == 'STUDENTS' and self.cleaned_data.get('student_id'):
            user.id = self.cleaned_data.get('student_id')
        
        if commit:
            user.save()
        return user


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ['email', 'firstname', 'lastname', 'user_type', 'is_active']
    list_filter = ['user_type', 'is_active']
    search_fields = ['email', 'firstname', 'lastname']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('firstname', 'lastname', 'phone', 'gender', 'profile_picture')}),
        ('User Type', {'fields': ('user_type', 'student_id', 'staff_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Personal Info', {'fields': ('firstname', 'lastname', 'phone', 'gender')}),
        ('User Type', {'fields': ('user_type', 'student_id', 'staff_id'), 'description': 'Students need student_id, Staff need staff_id'}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'password')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
