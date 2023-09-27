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
]

urlpatterns += router.urls
