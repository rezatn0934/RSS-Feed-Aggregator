from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

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
    multi_object = False

    def post(self, request):
        return self.create_object(request, self.model)

    def delete(self, request):
        return self.delete_object(request, self.model)

    def create_object(self, request, model, **kwargs):
        channel_id = request.data.get('channel_id')
        pk = request.data.get('pk')

        try:
            channel = Channel.objects.get(id=channel_id)
            item_model = get_item_model(channel)
            item = item_model.objects.get(id=pk)
            content_type = ContentType.objects.get_for_model(item)
        except Channel.DoesNotExist:
            return Response({'message': _("Channel not found.")}, status=status.HTTP_400_BAD_REQUEST)
        except item_model.DoesNotExist:
            return Response({'message': _("Item not found.")}, status=status.HTTP_400_BAD_REQUEST)
        except ContentType.DoesNotExist:
            return Response({'message': _("Content type not found.")}, status=status.HTTP_400_BAD_REQUEST)

        if not self.multi_object:
            interaction, created = model.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=item.pk,
                **kwargs
            )

            if not created:
                return Response({'message': _("You've already interacted with this item.")},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            model.objects.create(user=request.user,
                                 content_type=content_type,
                                 object_id=item.pk,
                                 **kwargs)

        categories = channel.category.all()
        update_recommendations(user=request.user, categories=categories, increment_count=1)
        return Response({'message': _("Your interaction was successful.")}, status=status.HTTP_200_OK)

    def delete_object(self, request, model):
        channel_id = request.data.get('channel_id')
        pk = request.data.get('pk')

        try:
            channel = Channel.objects.get(id=channel_id)
            item_model = get_item_model(channel)
            item = item_model.objects.get(id=pk)
            content_type = ContentType.objects.get_for_model(item)
        except Channel.DoesNotExist:
            return Response({'message': _("Channel not found.")}, status=status.HTTP_400_BAD_REQUEST)
        except item_model.DoesNotExist:
            return Response({'message': _("Item not found.")}, status=status.HTTP_400_BAD_REQUEST)
        except ContentType.DoesNotExist:
            return Response({'message': _("Content type not found.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            interaction = model.objects.get(user=request.user,
                                            content_type=content_type,
                                            object_id=item.pk)
            interaction.delete()
            categories = channel.category.all()
            update_recommendations(user=request.user, categories=categories, increment_count=-1)
            return Response({'message': _("Your interaction has been removed.")}, status=status.HTTP_200_OK)
        except model.DoesNotExist:
            return Response({'message': _("Interaction not found. You haven't interacted with this item.")},
                            status=status.HTTP_400_BAD_REQUEST)
