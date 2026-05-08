from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from items.models import Category, Location, LostReport, FoundReport
from users.models import CustomUser


GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class ReportUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="student@example.com",
            password="password123",
            firstname="Test",
            lastname="Student",
            student_id="STD12345",
            user_type="STUDENTS",
        )
        self.category = Category.objects.create(name="Phone")
        self.location = Location.objects.create(name="Library")
        self.client.force_authenticate(user=self.user)

    def test_create_lost_report_with_image(self):
        image = SimpleUploadedFile("lost.gif", GIF_BYTES, content_type="image/gif")

        response = self.client.post(
            "/api/items/lost/",
            {
                "category_id": self.category.id,
                "title": "Lost Phone",
                "description": "Black phone with cracked case",
                "location_id": self.location.id,
                "image": image,
                "colour": "Black",
                "brand": "Samsung",
                "model": "A15",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LostReport.objects.count(), 1)
        self.assertTrue(LostReport.objects.first().image.name.endswith(".gif"))

    def test_create_found_report_with_image(self):
        image = SimpleUploadedFile("found.gif", GIF_BYTES, content_type="image/gif")
        dropped_location = Location.objects.create(name="Security Office")

        response = self.client.post(
            "/api/items/found/",
            {
                "category_id": self.category.id,
                "title": "Found Phone",
                "description": "Phone found near the library entrance",
                "location_id": self.location.id,
                "dropped_location_id": dropped_location.id,
                "image": image,
                "colour": "Blue",
                "brand": "Nokia",
                "model": "C32",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FoundReport.objects.count(), 1)
        self.assertTrue(FoundReport.objects.first().image.name.endswith(".gif"))
        self.assertEqual(FoundReport.objects.first().location, self.location)
        self.assertEqual(FoundReport.objects.first().dropped_location, dropped_location)
