from rest_framework import serializers

from posts_api.models import Post


class PostSerializer(serializers.ModelSerializer):
    author_pk = serializers.CharField(
        source='author.pk',
        read_only=True,
    )
    author_nickname = serializers.CharField(
        source='author.nickname',
        read_only=True,
    )

    class Meta:
        model = Post
        fields = [
            'author_pk',
            'author_nickname',
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
