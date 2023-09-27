from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from .mixins import InteractionMixin
from .models import Like, Comment, BookMark, Subscription
from .utils import update_recommendations
from .serializers import SubscriptionSerializer


class LikeView(InteractionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.create_object(request, Like)

    def delete(self, request):
        return self.delete_object(request, Like)


class CommentView(InteractionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get('content')
        return self.create_object(request, Comment, content=content)

    def delete(self, request):
        return self.delete_object(request, Comment)


class BookMarkView(InteractionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.create_object(request, BookMark)

    def delete(self, request):
        return self.delete_object(request, BookMark)


class SubscriptionView(GenericAPIView):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objrcts.all

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        channel = serializer.validated_data['channel']
        user = request.user
        categories = channel.categories.all()

        update_recommendations(user=user, categories=categories, increment_count=1)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        subscription = self.get_object()
        channel = subscription.channel
        user = request.user
        categories = channel.categories.all()

        update_recommendations(user=user, categories=categories, increment_count=-1)
        return Response({'message': f"Your object has been deleted ."}, status=status.HTTP_200_OK)
