from rest_framework.response import Response
from rest_framework import status

from rssfeeds.models import Channel
from .utils import get_item_model, update_recommendations


class InteractionMixin:

    def create_object(self, request, model, **kwargs):
        channel_id = request.data.get('channel_id')
        channel = Channel.objects.filter(id=channel_id)
        pk = request.data.get('pk')

        item_model = get_item_model(channel)
        item = item_model.objects.get(id=pk)

        interaction, created = model.objects.get_or_create(user=request.user, content_object=item, **kwargs)

        if not created:
            return Response({'message': f"You've already interacted with this item."}, status=status.HTTP_400_BAD_REQUEST)

        categories = channel.categories.all()
        update_recommendations(user=request.user, categories=categories, increment_count=1)
        return Response({'message': f"Your object has been created successfully ."}, status=status.HTTP_200_OK)
