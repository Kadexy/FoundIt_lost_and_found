from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from django.utils import timezone
from difflib import SequenceMatcher
import logging
from .models import LostReport, FoundReport, Category, Location
from .serializers import LostReportSerializer, FoundReportSerializer, CategorySerializer, LocationSerializer
from .permissions import IsStudent, IsStaffOrAdmin, IsOwner, CanModifyItem

logger = logging.getLogger(__name__)

# Create your views here.

def Index(request):
    """Render the main index page"""
    return render(request, 'index.html')


# ==================== LOST REPORT VIEWS ====================

class LostReportListView(generics.ListAPIView):
    """List all lost reports - with privacy filtering for students"""
    serializer_class = LostReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins/Staff can see all lost reports
        if user.user_type in ['ADMIN', 'STAFFS']:
            return LostReport.objects.all().order_by('-date_reported')

        # Students can only see their own lost reports
        return LostReport.objects.filter(reporter=user).order_by('-date_reported')


class LostReportViewSet(ModelViewSet):
    """API endpoint for managing lost reports"""
    queryset = LostReport.objects.all()
    serializer_class = LostReportSerializer
    permission_classes = [permissions.IsAuthenticated, CanModifyItem]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'STUDENTS':
            return LostReport.objects.filter(reporter=user)
        return LostReport.objects.all()

    def perform_create(self, serializer):
        report = serializer.save()
        self.send_lost_report_notification(report)
        self.auto_match_lost_report(report)

    def perform_destroy(self, instance):
        if instance.reporter != self.request.user and self.request.user.user_type not in ['STAFFS', 'ADMIN']:
            self.permission_denied(self.request, message="You do not have permission to delete this report.")
        instance.delete()

    def _calculate_weighted_score(self, lost_report, found_report):
        score = 0.0
        if lost_report.category == found_report.category:
            score += 30
        else:
            return 0.0

        if lost_report.colour and found_report.colour and lost_report.colour.lower() == found_report.colour.lower():
            score += 20

        desc_similarity = self._text_similarity(lost_report.description, found_report.description)
        score += desc_similarity * 20

        if lost_report.location and found_report.location:
            location_similarity = self._text_similarity(lost_report.location.name, found_report.location.name)
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

    def _text_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def auto_match_lost_report(self, lost_report):
        """Auto-match lost report with found reports"""
        potential_found = FoundReport.objects.filter(
            category=lost_report.category,
            status='found',
            matched_with__isnull=True
        )

        best_match = None
        best_score = 0

        for candidate in potential_found:
            score = self._calculate_weighted_score(lost_report, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_match and best_score >= 60:
            lost_report.matched_with = best_match
            best_match.matched_with = lost_report
            lost_report.status = 'matched'
            best_match.status = 'matched'
            lost_report.save()
            best_match.save()

            self.send_match_found_notification(lost_report, best_match)

    def send_notification_email(self, subject, message, recipient_list):
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                recipient_list=recipient_list,
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send notification email", extra={"recipient_list": recipient_list, "subject": subject})

    def send_lost_report_notification(self, report):
        if not report.reporter.email:
            return

        location_text = report.location.name if report.location else 'No specific location was provided.'
        subject = f"Item reported successfully: {report.title}"
        message = (
            f"Hello {report.reporter.firstname},\n\n"
            f"Your item has been reported successfully. We have received your lost item report for the following item:\n"
            f"- Category: {report.category.name}\n"
            f"- Title: {report.title}\n"
            f"- Description: {report.description}\n"
            f"- Location: {location_text}\n\n"
            f"As soon as an item matching this description is found, we will send you an email update with the next steps.\n\n"
            f"Thank you for using the Lost and Found service.\n"
            f"Regards,\n"
            f"Lost and Found Team"
        )
        self.send_notification_email(subject, message, [report.reporter.email])

    def send_match_found_notification(self, lost_report, found_report):
        if not lost_report.reporter.email:
            return

        found_location = found_report.dropped_location.name if found_report.dropped_location else 'the Lost and Found office'
        found_when = found_report.date_reported.strftime('%Y-%m-%d %H:%M') if found_report.date_reported else 'a recent time'
        subject = f"A possible match has been found for your lost {lost_report.category.name}"
        message = (
            f"Hello {lost_report.reporter.firstname},\n\n"
            f"A found item that appears to match your reported lost item has been located.\n\n"
            f"Lost item reported:\n"
            f"- Category: {lost_report.category.name}\n"
            f"- Title: {lost_report.title}\n"
            f"- Description: {lost_report.description}\n\n"
            f"Possible matching found item:\n"
            f"- Title: {found_report.title}\n"
            f"- Description: {found_report.description}\n"
            f"- Location to verify: {found_location}\n"
            f"- Found date: {found_when}\n\n"
            f"Please visit {found_location} to verify the item and claim it.\n\n"
            f"If this is not your item, simply ignore this email and we will continue searching for a better match.\n\n"
            f"Regards,\n"
            f"Lost and Found Team"
        )
        self.send_notification_email(subject, message, [lost_report.reporter.email])


# ==================== FOUND REPORT VIEWS ====================

class FoundReportListView(generics.ListAPIView):
    """List found reports - with privacy filtering for students"""
    serializer_class = FoundReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        min_score = 60  # 60% similarity threshold

        # Admins/Staff can see all found reports
        if user.user_type in ['ADMIN', 'STAFFS']:
            return FoundReport.objects.all().order_by('-date_reported')

        # For Students: Show only found reports that match their lost reports
        student_lost_reports = LostReport.objects.filter(reporter=user, status='matched')

        if not student_lost_reports.exists():
            return FoundReport.objects.none()

        # Get matched found reports
        visible_found = FoundReport.objects.filter(matched_with__in=student_lost_reports)
        return visible_found.order_by('-date_reported')


class FoundReportViewSet(ModelViewSet):
    """API endpoint for managing found reports"""
    queryset = FoundReport.objects.all()
    serializer_class = FoundReportSerializer
    permission_classes = [permissions.IsAuthenticated, CanModifyItem]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'STUDENTS':
            return FoundReport.objects.filter(reporter=user)
        return FoundReport.objects.all()

    def perform_create(self, serializer):
        report = serializer.save()
        self.send_found_report_notification(report)
        self.auto_match_found_report(report)

    def send_found_report_notification(self, report):
        if not report.reporter.email:
            return

        location_text = report.location.name if report.location else 'No specific location was provided.'
        subject = f"Item reported successfully: {report.title}"
        message = (
            f"Hello {report.reporter.firstname},\n\n"
            f"Your item has been reported successfully. Thank you for helping the community!\n\n"
            f"We have received your found item report for the following item:\n"
            f"- Category: {report.category.name}\n"
            f"- Title: {report.title}\n"
            f"- Description: {report.description}\n"
            f"- Location found: {location_text}\n\n"
            f"We will notify you if an owner claims this item.\n\n"
            f"Regards,\n"
            f"Lost and Found Team"
        )
        
        from django.conf import settings
        from django.core.mail import send_mail
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                recipient_list=[report.reporter.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send found report confirmation email", extra={"recipient_list": [report.reporter.email]})

    def perform_destroy(self, instance):
        if instance.reporter != self.request.user and self.request.user.user_type not in ['STAFFS', 'ADMIN']:
            self.permission_denied(self.request, message="You do not have permission to delete this report.")
        instance.delete()

    def _calculate_weighted_score(self, lost_report, found_report):
        score = 0.0
        if lost_report.category == found_report.category:
            score += 30
        else:
            return 0.0

        if lost_report.colour and found_report.colour and lost_report.colour.lower() == found_report.colour.lower():
            score += 20

        desc_similarity = self._text_similarity(lost_report.description, found_report.description)
        score += desc_similarity * 20

        if lost_report.location and found_report.location:
            location_similarity = self._text_similarity(lost_report.location.name, found_report.location.name)
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

    def _text_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def auto_match_found_report(self, found_report):
        """Auto-match found report with lost reports"""
        potential_lost = LostReport.objects.filter(
            category=found_report.category,
            status='pending',
            matched_with__isnull=True
        )

        best_match = None
        best_score = 0

        for candidate in potential_lost:
            score = self._calculate_weighted_score(candidate, found_report)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_match and best_score >= 60:
            found_report.matched_with = best_match
            best_match.matched_with = found_report
            found_report.status = 'matched'
            best_match.status = 'matched'
            found_report.save()
            best_match.save()

            # Send email to the lost report owner
            from django.conf import settings
            from django.core.mail import send_mail
            if best_match.reporter.email:
                found_location = found_report.dropped_location.name if found_report.dropped_location else 'the Lost and Found office'
                subject = f"A possible match has been found for your lost {best_match.category.name}"
                message = (
                    f"Hello {best_match.reporter.firstname},\n\n"
                    f"A found item that appears to match your reported lost item has been located.\n\n"
                    f"Lost item reported:\n"
                    f"- Category: {best_match.category.name}\n"
                    f"- Title: {best_match.title}\n"
                    f"- Description: {best_match.description}\n\n"
                    f"Possible matching found item:\n"
                    f"- Title: {found_report.title}\n"
                    f"- Description: {found_report.description}\n"
                    f"- Location to verify: {found_location}\n\n"
                    f"Please visit {found_location} to verify the item and claim it.\n\n"
                    f"Regards,\n"
                    f"Lost and Found Team"
                )
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                        recipient_list=[best_match.reporter.email],
                        fail_silently=True,
                    )
                except Exception:
                    logger.exception(
                        "Failed to send found-report match notification",
                        extra={"lost_report_id": best_match.id, "found_report_id": found_report.id},
                    )


# ==================== SHARED VIEWS ====================

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class LocationListView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
