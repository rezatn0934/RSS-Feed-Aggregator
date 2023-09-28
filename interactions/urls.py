from django.urls import path
from .views import LikeView, CommentView, BookMarkView, SubscriptionView, RecommendationRetrieveView


app_name = 'interaction'
urlpatterns = [
    path('like/', LikeView.as_view(), name='like'),
    path('comment/', CommentView.as_view(), name='comment'),
    path('bookmark/', BookMarkView.as_view(), name='bookmark'),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
    path('recommendation/', RecommendationRetrieveView.as_view(), name='recommendation'),
]
