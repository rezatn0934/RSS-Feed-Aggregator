from django.db import IntegrityError
from django.db.models import Subquery
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from accounts.authentication import JWTAuthentication
from .mixins import InteractionMixin
from .models import Like, Comment, BookMark, Subscription, Recommendation
from .utils import update_recommendations
from .serializers import SubscriptionSerializer
from rssfeeds.models import Channel
from rssfeeds.serializers import ChannelSerializer


class LikeView(InteractionMixin, APIView):
    model = Like


class CommentView(InteractionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get('content')
        return self.create_object(request, Comment, content=content)


class BookMarkView(InteractionMixin, APIView):
    model = BookMark


class SubscriptionView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError as e:
            return Response({'message': _("Subscription already exists.")}, status=status.HTTP_400_BAD_REQUEST)

        channel = serializer.validated_data['channel']
        user = request.user
        categories = channel.category.all()

        update_recommendations(user=user, categories=categories, increment_count=1)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        subscription = self.get_object()
        channel = subscription.channel
        user = request.user
        categories = channel.categories.all()

        update_recommendations(user=user, categories=categories, increment_count=-1)
        return Response({_('message'): _("Your object has been deleted .")}, status=status.HTTP_200_OK)


class RecommendationRetrieveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recommendation = Recommendation.objects.filter(user=request.user).order_by('-count').first()

        if recommendation:
            channels = Channel.objects.filter(category=recommendation.category)[:5]
            serializer = ChannelSerializer(channels, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({_("message"): _("No recommendations available for this user.")}, status=status.HTTP_404_NOT_FOUND)
