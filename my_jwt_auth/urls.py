from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import RegisterAPIView, MeAPIView, ChangePasswordAPIView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('me/', MeAPIView.as_view(), name='api_me'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='api_change_password'),
]