from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveAPIView

from accounts.authentication import JWTAuthentication
from .mixins import InteractionMixin
from .models import Like, Comment, BookMark, Subscription, Recommendation
from .utils import update_recommendations
from .serializers import SubscriptionSerializer
from .serializers import RecommendationSerializer


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
        serializer.save()

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
        return Response({'message': f"Your object has been deleted ."}, status=status.HTTP_200_OK)


class RecommendationRetrieveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationSerializer

    def get(self, request):
        recommendations = Recommendation.objects.filter(user=request.user)
        serializer = self.serializer_class(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
