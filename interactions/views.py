from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .mixins import InteractionMixin
from .models import Like, Comment


class LikeView(InteractionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.create_object(request, Like)

    def delete(self, request):
        return self.delete_object(request, Like)

