from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.authentication import JWTAuthentication
from rssfeeds.models import Channel
from .utils import get_item_model, update_recommendations


class InteractionMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    model = None

    def post(self, request):
        return self.create_object(request, self.model)

    def delete(self, request):
        return self.delete_object(request, self.model)

    def create_object(self, request, model, **kwargs):

        channel_id = request.data.get('channel_id')
        channel = Channel.objects.filter(id=channel_id).first()
        pk = request.data.get('pk')

        item_model = get_item_model(channel)
        item = item_model.objects.get(id=pk)
        content_type = ContentType.objects.get_for_model(item)

        interaction, created = model.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=item.pk,
            **kwargs
        )

        if not created:
            return Response({'message': f"You've already interacted with this item."},
                            status=status.HTTP_400_BAD_REQUEST)

        categories = channel.category.all()
        update_recommendations(user=request.user, categories=categories, increment_count=1)
        return Response({'message': f"Your object has been created successfully ."}, status=status.HTTP_200_OK)

    def delete_object(self, request, model):
        channel_id = request.data.get('channel_id')
        channel = Channel.objects.get(id=channel_id)
        pk = request.data.get('pk')

        item_model = get_item_model(channel)
        item = item_model.objects.get(id=pk)

        try:
            content_type = ContentType.objects.get_for_model(item)

            interaction = model.objects.get(user=request.user,
                                            content_type=content_type,
                                            object_id=item.pk, )
            interaction.delete()
            categories = channel.category.all()
            update_recommendations(user=request.user, categories=categories, increment_count=-1)
            return Response({'message': f"Your object has been deleted ."}, status=status.HTTP_200_OK)
        except model.DoesNotExist:
            return Response({'message': "You haven't interacted with this item."}, status=status.HTTP_400_BAD_REQUEST)
