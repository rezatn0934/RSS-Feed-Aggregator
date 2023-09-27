from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rssfeeds.models import Channel, Podcast, News
from .models import Like
from .utils import get_item_model, update_recommendations


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        channel_id = request.data.get('channel_id')
        channel = Channel.objects.filter(id=channel_id)
        id = request.data.get('pk')

        item_model = get_item_model(channel)
        item = item_model.objects.get(id=id)

        like, created = Like.objects.create_or_create(user=request.user, content_object=item)

        if not created:
            return Response({'message': "You're already like it."}, status=status.HTTP_400_BAD_REQUEST)

        categories = channel.cateories.all()
        update_recommendations(user=request.user, categories=categories)
        return Response({'message': "You liked the item successfully."}, status=status.HTTP_201_CREATED)

    def delete(self, request):

        channel_id = request.data.get('channel_id')
        channel = Channel.objects.filter(id=channel_id)
        id = request.data.get('pk')

        item_model = get_item_model(channel)
        item = item_model.objects.get(id=id)


        try:
            like = Like.objects.get(user=request.user, content_object=item)
            like.delete()
            categories = channel.cateories.all()
            update_recommendations(user=request.user, categories=categories, increment_count=-1)
            return Response({'message': "You unliked the item successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({'message': "You haven't liked this item."}, status=status.HTTP_400_BAD_REQUEST)

