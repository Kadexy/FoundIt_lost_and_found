from django.urls import path
from .views import (
    SignUpView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    DeleteAccountView,
    UpdateProfilePictureView,
    VerifyEmailView,
    ResendVerificationEmailView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup/", SignUpView.as_view()),
    path("login/", LoginView.as_view()),
    path('refresh-token/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('delete-account/', DeleteAccountView.as_view()),
    path('profile-picture/', UpdateProfilePictureView.as_view()),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
]
