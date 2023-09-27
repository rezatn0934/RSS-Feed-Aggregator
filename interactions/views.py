from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .mixins import InteractionMixin
from .models import Like, Comment, BookMark


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
