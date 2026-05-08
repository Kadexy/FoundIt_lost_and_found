from django.shortcuts import render, redirect
from rest_framework import views, status, generics
from django.contrib import messages
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db import transaction
from .serializers import (
    SignUpSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    DeleteAccountSerializer,
    UpdateProfilePictureSerializer,
)
from .models import CustomUser

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class SignUpView(generics.GenericAPIView):
    """
    API endpoint for user registration.
    Validates user data and creates new user account.
    CSRF exempt because this is a public API endpoint.
    """
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer

    def _send_verification_email(self, request, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_path = f"/api/user/verify-email/{uid}/{token}/"
        verification_url = request.build_absolute_uri(verification_path)

        subject = "Verify your Lost and Found account"
        message = (
            f"Hello {user.firstname},\n\n"
            f"Thank you for signing up for Lost and Found.\n"
            f"Please verify your email address by clicking the link below:\n\n"
            f"{verification_url}\n\n"
            f"If you did not create this account, you can ignore this email.\n\n"
            f"Regards,\n"
            f"Lost and Found Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
            recipient_list=[user.email],
            fail_silently=False,
        )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email").lower()
        phone = serializer.validated_data.get("phone")

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response(
                {"detail": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if phone already exists
        if CustomUser.objects.filter(phone=phone).exists():
            return Response(
                {"detail": "Phone number already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for student or staff ID conflicts
        user_type = serializer.validated_data.get("user_type")
        if user_type == "STUDENTS":
            student_id = serializer.validated_data.get("student_id")
            if CustomUser.objects.filter(student_id=student_id).exists():
                return Response(
                    {"detail": "Student ID already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif user_type == "STAFFS":
            staff_id = serializer.validated_data.get("staff_id")
            if CustomUser.objects.filter(staff_id=staff_id).exists():
                return Response(
                    {"detail": "Staff ID already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create user
        try:
            with transaction.atomic():
                user = serializer.save()
                user.is_active = False
                user.is_verified = False
                user.save(update_fields=['is_active', 'is_verified'])
                self._send_verification_email(request, user)
            return Response({
                "detail": "Account created. Please check your email to verify your account before signing in.",
                "user": {
                    'id': user.id,
                    'email': user.email,
                    'user_type': user.user_type,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": f"Error creating user: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyEmailView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return redirect('/login/?verified=invalid')

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.is_active = True
            user.save(update_fields=['is_verified', 'is_active'])
            return redirect('/login/?verified=success')

        return redirect('/login/?verified=invalid')

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login.
    Returns JWT access and refresh tokens upon successful authentication.
    CSRF exempt because this is a public API endpoint.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response(
                {"detail": str(e.detail)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {"detail": f"Error during login: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout.
    Blacklists the refresh token to prevent reuse.
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)   
        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "Invalid token or already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveAPIView):
    """
    Return the authenticated user's profile details.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


class DeleteAccountView(generics.GenericAPIView):
    serializer_class = DeleteAccountSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.delete()
        return Response({"detail": "Account deleted successfully."}, status=status.HTTP_200_OK)


class UpdateProfilePictureView(generics.GenericAPIView):
    serializer_class = UpdateProfilePictureSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "detail": "Profile picture updated successfully.",
                "profile_picture": serializer.data.get("profile_picture"),
            },
            status=status.HTTP_200_OK,
        )
