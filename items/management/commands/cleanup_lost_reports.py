from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from items.models import LostReport, FoundReport


class Command(BaseCommand):
    help = 'Delete lost reports that have been matched and claimed for more than 24 hours'

    def handle(self, *args, **options):
        # Find found reports that:
        # 1. Have been claimed
        # 2. Were claimed more than 24 hours ago
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        # Get claimed found reports older than 24 hours
        old_claimed_reports = FoundReport.objects.filter(
            status='claimed',
            picked_up_date__lt=cutoff_time
        )
        
        # Get the matched lost reports to delete
        deleted_count = 0
        for found_report in old_claimed_reports:
            if found_report.matched_with:
                lost_report = found_report.matched_with
                lost_report.delete()
                deleted_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} old lost report(s)')
        )