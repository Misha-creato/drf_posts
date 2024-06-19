from rest_framework import serializers

from posts_api.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'title',
            'description',
            'image',
            'hidden',
            'slug',
            'created_at',
        ]

        extra_kwargs = {
            'slug': {'read_only': True},
            'created_at': {'read_only': True},
        }
