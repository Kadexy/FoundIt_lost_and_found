from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser


GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='student@example.com',
            password='password123',
            firstname='Test',
            lastname='Student',
            student_id='STD999',
            user_type='STUDENTS',
        )

    def test_login_returns_email_field(self):
        response = self.client.post(
            '/api/user/login/',
            {'email': 'student@example.com', 'password': 'password123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'student@example.com')

    def test_profile_endpoint_returns_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/user/profile/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'student@example.com')
        self.assertEqual(response.data['firstname'], 'Test')

    def test_change_password_endpoint_updates_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/user/change-password/',
            {
                'current_password': 'password123',
                'new_password': 'newpassword456',
                'confirm_password': 'newpassword456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

    def test_delete_account_endpoint_removes_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/user/delete-account/',
            {'password': 'password123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CustomUser.objects.filter(email='student@example.com').exists())

    def test_update_profile_picture_endpoint_saves_image(self):
        self.client.force_authenticate(user=self.user)
        image = SimpleUploadedFile("profile.gif", GIF_BYTES, content_type="image/gif")

        response = self.client.post(
            '/api/user/profile-picture/',
            {'profile_picture': image},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_picture.name.endswith('.gif'))
