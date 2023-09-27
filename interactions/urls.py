from django.urls import path
from .views import LikeView, CommentView, BookMarkView, SubscriptionView


app_name = 'interaction'
urlpatterns = [
    path('like/', LikeView.as_view(), name='like'),
]
