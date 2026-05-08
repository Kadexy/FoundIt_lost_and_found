"""
Custom permission classes for items app
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the item
    """
    def has_object_permission(self, request, view, obj):
        # Owner can do anything
        return obj.reporter == request.user


class IsStudent(permissions.BasePermission):
    """
    Permission to check if user is a student
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'STUDENTS'


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is staff or admin
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['STAFFS', 'ADMIN']


class IsAuthenticated(permissions.BasePermission):
    """
    Permission to check if user is authenticated
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanCreateItem(permissions.BasePermission):
    """
    Permission to create items - only authenticated users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanModifyItem(permissions.BasePermission):
    """
    Permission to modify items - only owner or admin/staff
    """
    def has_permission(self, request, view):
        # Allow all authenticated users to access the view
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin/Staff can modify or delete any item
        if request.user.user_type in ['STAFFS', 'ADMIN']:
            return True
        # Owner can modify or delete their own item
        return obj.reporter == request.user
