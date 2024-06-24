from rest_framework import serializers

from django.contrib.auth import get_user_model

from posts_api.models import Post


User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author_pk = serializers.CharField(
        source='author.pk',
        read_only=True,
    )
    author_nickname = serializers.SerializerMethodField(
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

    def get_author_nickname(self, obj):
        '''
        Получение никнейма пользователя

        Returns:
            Никнейм
        '''

        email = obj.author.email
        return email.split('@')[0]


class PostsSerializer(serializers.ModelSerializer):
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


class AuthorPostSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField(
        read_only=True,
    )
    posts = PostsSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'pk',
            'nickname',
            'thumbnail',
            'posts',
        ]

    def get_nickname(self, obj):
        '''
        Получение никнейма пользователя

        Returns:
            Никнейм
        '''

        email = obj.email
        return email.split('@')[0]
