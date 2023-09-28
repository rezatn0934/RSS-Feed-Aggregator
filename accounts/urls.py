from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserProfileDetailView, basename='users')

app_name = 'accounts'
urlpatterns = [
    path("register/", views.UserRegister.as_view(), name="register"),
    path("login/", views.UserLogin.as_view(), name="login"),
    path("refresh/", views.RefreshToken.as_view(), name="refresh_token"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("forget_password/", views.ForgetPassword.as_view(), name="forget_password"),
    path("change_password_token/", views.ChangePasswordWithToken.as_view(), name="change_password_token"),
]

urlpatterns += router.urls
