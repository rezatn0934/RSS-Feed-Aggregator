from rest_framework import serializers

from .models import Subscription, Comment


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['channel']

    def create(self, validated_data):
        channel = validated_data['channel']
        user = self.context['request'].user
        return Subscription.objects.create(user=user, channel=channel)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content']
        extra_kwargs = {
            'id': {'read_only': True}
        }