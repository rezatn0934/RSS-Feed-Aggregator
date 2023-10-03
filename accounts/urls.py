from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'accounts'
urlpatterns = [
    path("register/", views.UserRegister.as_view(), name="register"),
    path("login/", views.UserLogin.as_view(), name="login"),
    path('user/', views.UserProfileDetailView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='user-detail'),
    path('user/change_password/', views.UserProfileDetailView.as_view({'post': 'change_password'}),
         name='user-change-password'),
    path("refresh/", views.RefreshToken.as_view(), name="refresh_token"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("forget_password/", views.ForgetPassword.as_view(), name="forget_password"),
    path("change_password_token/", views.ChangePasswordWithToken.as_view(), name="change_password_token"),
]

