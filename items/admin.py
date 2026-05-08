from django.contrib import admin
from .models import LostReport, FoundReport, Category, Location
from difflib import SequenceMatcher
from django.contrib import messages
from django.utils import timezone


# Register your models here.

def calculate_weighted_score(lost_report, found_report):
    score = 0.0
    if lost_report.category == found_report.category:
        score += 30
    else:
        return 0.0

    if lost_report.colour and found_report.colour and lost_report.colour.lower() == found_report.colour.lower():
        score += 20

    desc_similarity = text_similarity(lost_report.description, found_report.description)
    score += desc_similarity * 20

    if lost_report.location and found_report.location:
        location_similarity = text_similarity(lost_report.location.name, found_report.location.name)
        score += location_similarity * 15

    if lost_report.brand and found_report.brand and lost_report.brand.lower() == found_report.brand.lower():
        score += 8

    if lost_report.model and found_report.model and lost_report.model.lower() == found_report.model.lower():
        score += 7

    if lost_report.date_reported and found_report.date_reported:
        time_diff = abs((found_report.date_reported - lost_report.date_reported).days)
        if time_diff <= 7:
            score += 10
        elif time_diff <= 14:
            score += 5

    return round(score, 2)


def text_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


@admin.register(LostReport)
class LostReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'category', 'reporter', 'matched_with', 'date_reported']
    list_filter = ['status', 'category', 'date_reported']
    search_fields = ['title', 'description']
    readonly_fields = ['date_reported', 'reporter']
    actions = ['match_selected_lost_reports']

    def match_selected_lost_reports(self, request, queryset):
        matched_count = 0
        for lost in queryset:
            if lost.status == 'pending' and not lost.matched_with:
                # Find best matching found report
                potential_found = FoundReport.objects.filter(
                    category=lost.category,
                    status='found',
                    matched_with__isnull=True
                )
                best_match = None
                best_score = 0
                for found in potential_found:
                    score = calculate_weighted_score(lost, found)
                    if score > best_score:
                        best_score = score
                        best_match = found
                if best_match and best_score >= 60:
                    lost.matched_with = best_match
                    best_match.matched_with = lost
                    lost.status = 'matched'
                    best_match.status = 'matched'
                    lost.save()
                    best_match.save()
                    matched_count += 1
        if matched_count > 0:
            self.message_user(request, f'Successfully matched {matched_count} lost reports with found reports.')
        else:
            self.message_user(request, 'No reports were matched. Ensure selected reports are pending and have suitable found report matches with score >=60.')
    match_selected_lost_reports.short_description = "Match selected lost reports with best found report match (score >=60)"


@admin.register(FoundReport)
class FoundReportAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'status',
        'safe_category',
        'safe_location',
        'safe_dropped_location',
        'safe_reporter',
        'safe_matched_with',
        'claimed_by',
        'picked_up_date',
        'date_reported',
    ]
    list_filter = ['status', 'category', 'date_reported']
    search_fields = ['title', 'description', 'claimed_by']
    readonly_fields = ['date_reported', 'reporter']
    actions = ['match_selected_found_reports', 'mark_as_claimed']
    list_select_related = ['category', 'location', 'dropped_location', 'reporter', 'matched_with']

    @admin.display(description='Category')
    def safe_category(self, obj):
        try:
            return obj.category
        except Exception:
            return f"Missing category (id={obj.category_id})" if obj.category_id else "-"

    @admin.display(description='Location')
    def safe_location(self, obj):
        try:
            return obj.location
        except Exception:
            return f"Missing location (id={obj.location_id})" if obj.location_id else "-"

    @admin.display(description='Dropped location')
    def safe_dropped_location(self, obj):
        try:
            return obj.dropped_location
        except Exception:
            return f"Missing dropped location (id={obj.dropped_location_id})" if obj.dropped_location_id else "-"

    @admin.display(description='Reporter')
    def safe_reporter(self, obj):
        try:
            return obj.reporter
        except Exception:
            return f"Missing reporter (id={obj.reporter_id})" if obj.reporter_id else "-"

    @admin.display(description='Matched with')
    def safe_matched_with(self, obj):
        try:
            return obj.matched_with
        except Exception:
            return f"Missing lost report (id={obj.matched_with_id})" if obj.matched_with_id else "-"

    def match_selected_found_reports(self, request, queryset):
        matched_count = 0
        for found in queryset:
            if found.status == 'found' and not found.matched_with:
                # Find best matching lost report
                potential_lost = LostReport.objects.filter(
                    category=found.category,
                    status='pending',
                    matched_with__isnull=True
                )
                best_match = None
                best_score = 0
                for lost in potential_lost:
                    score = calculate_weighted_score(lost, found)
                    if score > best_score:
                        best_score = score
                        best_match = lost
                if best_match and best_score >= 60:
                    found.matched_with = best_match
                    best_match.matched_with = found
                    found.status = 'matched'
                    best_match.status = 'matched'
                    found.save()
                    best_match.save()
                    matched_count += 1
        if matched_count > 0:
            self.message_user(request, f'Successfully matched {matched_count} found reports with lost reports.')
        else:
            self.message_user(request, 'No reports were matched. Ensure selected reports are found and have suitable lost report matches with score >=60.')
    match_selected_found_reports.short_description = "Match selected found reports with best lost report match (score >=60)"

    def mark_as_claimed(self, request, queryset):
        """Mark selected found reports as claimed by a student"""
        for found in queryset:
            if found.status in ['found', 'matched']:
                # Get the matched lost report's reporter student_id
                if found.matched_with and found.matched_with.reporter:
                    student_id = found.matched_with.reporter.student_id
                    found.claimed_by = student_id
                    found.status = 'claimed'
                    found.picked_up_date = timezone.now()
                    found.save()
                    
                    # Also update the matched lost report status
                    if found.matched_with:
                        found.matched_with.status = 'claimed'
                        found.matched_with.save()
        self.message_user(request, f'{queryset.count()} report(s) marked as claimed.')
    mark_as_claimed.short_description = "Mark selected found reports as claimed (uses matched lost report reporter's student_id)"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
