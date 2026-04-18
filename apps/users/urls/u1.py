from django.urls import path

from apps.users.api.v1 import (
    LogoutView,
    MeView,
    SendOTPView,
    TokenRefreshView,
    VerifyOTPView,
)


urlpatterns = [
    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    path("me/", MeView.as_view(), name="me"),
]
