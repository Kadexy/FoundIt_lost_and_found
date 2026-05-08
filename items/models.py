from django.db import models
from users.models import CustomUser
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
CATEGORIES = (
    ('phone', 'Phone'),
    ('wallet', 'Wallet'),
    ('id_card', 'ID Card'),
    ('keys', 'Keys'),
    ('laptop', 'Laptop'),
    ('Ipad', 'iPad'),
    ('tablet', 'Tablet'),
    ('book', 'Book'),
    ('other', 'Other'),
)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. "Phone", "Wallet", "ID Card"

    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=200, unique=True)  # e.g. "Library", "Cafeteria", "Room 101"

    def __str__(self):
        return self.name


class LostReport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('claimed', 'Claimed'),
    )
    
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lost_reports')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='items/', null=True, blank=True)
    colour = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    date_reported = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    matched_with = models.ForeignKey('FoundReport', null=True, blank=True, on_delete=models.SET_NULL, related_name='matches')

    def __str__(self):
        return f"Lost - {self.title} ({self.category})"

    class Meta:
        ordering = ['-date_reported']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['date_reported']),
        ]


class FoundReport(models.Model):
    STATUS_CHOICES = (
        ('found', 'Found'),
        ('matched', 'Matched'),
        ('claimed', 'Claimed'),
        ('returned', 'Returned'),
    )
    
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='found_reports')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="Provide a brief title for the item, e.g. 'Black iPhone 12 on' or 'Blue Backpack'.")
    description = models.TextField(help_text="Provide a detailed description of the item, including any unique features or identifiers and additional information on location.")
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='found_item_locations',
        help_text="Where the item was originally found.",
    )
    dropped_location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True, related_name='dropped_found_items')
    picked_up_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='items/', null=True, blank=True)
    colour = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    date_reported = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='found')
    matched_with = models.ForeignKey('LostReport', null=True, blank=True, on_delete=models.SET_NULL, related_name='matches')
    claimed_by = models.CharField(max_length=100, blank=True, null=True, help_text="Student ID of the person who claimed this item")

    def __str__(self):
        return f"Found - {self.title} ({self.category})"

    class Meta:
        ordering = ['-date_reported']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['date_reported']),
        ]
