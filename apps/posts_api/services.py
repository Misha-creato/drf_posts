from django.db.models import (
    Q,
    Prefetch,
)
from django.http.request import QueryDict

from posts_api.models import Post
from posts_api.serializers import (
    PostSerializer,
    AuthorPostSerializer,
)

from users_api.models import CustomUser

from utils.response_patterns import generate_response
from utils.logger import get_logger

logger = get_logger(__name__)


def get_posts() -> (int, dict):
    '''
    Получение списка всех постов

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg='Получение списка всех постов',
    )
    try:
        posts = Post.objects.filter(
            hidden=False,
        )
    except Exception as exc:
        logger.error(
            msg='Возникла ошибка при попытке получить список всех постов',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    data = PostSerializer(
        instance=posts,
        many=True,
    ).data
    logger.info(
        msg=f'Список всех постов получен: {data}'
    )
    return generate_response(
        status_code=200,
        data=data,
    )


def add(user: CustomUser, data: QueryDict) -> (int, dict):
    '''
    Создание поста

    Args:
        user: пользователь
        data: данные поста

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Создание поста пользователем {user}: {data}',
    )
    serializer = PostSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для создания поста\
            пользователем {user}: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    try:
        post = Post.objects.create(
            author=user,
            **validated_data,
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при попытке создании поста\
                    пользователем {user}: {validated_data}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Пост {post} пользователя {user} успешно создан',
    )
    return generate_response(
        status_code=200,
    )


def get_post(slug: str, user: CustomUser) -> (int, Post | None):
    '''
    Получение поста по slug

    Args:
        slug: слаг
        user: пользователь

    Returns:
        Кортеж из статуса и объекта Post
    '''

    logger.info(
        msg=f'Поиск поста по слагу {slug} пользователем {user}',
    )
    try:
        post = Post.objects.filter(
            Q(author=user) & Q(slug=slug) | Q(slug=slug) & Q(hidden=False)
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при поиcке поста по слагу {slug} пользователем {user}',
            exc_info=True,
        )
        return 500, None

    if post is None:
        logger.error(
            msg=f'Пост со слагом {slug} не найден пользователем {user}',
        )
        return 404, None

    logger.info(
        msg=f'Пост со слагом {slug} успешно найден пользователем {user}',
    )
    return 200, post


def detail(slug: str, user: CustomUser) -> (int, dict):
    '''
    Получение данных поста по slug

    Args:
        slug: слаг
        user: пользователь

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Получение данных поста с слагом {slug} пользователем {user}',
    )
    status_code, post = get_post(
        slug=slug,
        user=user,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    serializer = PostSerializer(
        instance=post,
    )
    data = serializer.data
    logger.info(
        msg=f'Данные поста с слагом {slug} успешно получены: {data} пользователем {user}',
    )
    return generate_response(
        status_code=200,
        data=data,
    )


def update(slug: str, user: CustomUser, data: QueryDict) -> (int, dict):
    '''
    Обновление поста по slug

    Args:
        slug: слаг
        user: пользователь
        data: данные поста

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Обновление поста по слагу {slug} пользователем {user} c данными: {data}'
    )
    status_code, post = get_post(
        slug=slug,
        user=user,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    if post.author != user:
        logger.error(
            msg=f'Обновление поста {post} пользователем {user} c данными {data} не доступно'
        )
        return generate_response(
            status_code=403,
        )

    serializer = PostSerializer(
        instance=post,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для обновления \
            поста {post} пользователем {user}: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    try:
        serializer.update(
            instance=post,
            validated_data=validated_data,
        )
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при попытке обновления поста {post} \
            пользователем {user} данными {validated_data}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    data = serializer.data
    logger.info(
        msg=f'Обновление поста {post} пользователем {user} прошло успешно',
    )
    return generate_response(
        status_code=200,
        data=data,
    )


def remove(slug: str, user: CustomUser) -> (int, dict):
    '''
    Удаление поста по slug

    Args:
        slug: слаг
        user: пользователь

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Удаление поста по слагу {slug} пользователем {user}'
    )
    status_code, post = get_post(
        slug=slug,
        user=user,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    if post.author != user:
        logger.error(
            msg=f'Удаление поста {post} пользователем {user} не доступно'
        )
        return generate_response(
            status_code=403,
        )

    title = post.title
    try:
        post.delete()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при попытке удаления поста {post} \
            пользователем {user}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Пост {title} удален пользователем {user}',
    )
    return generate_response(
        status_code=200
    )


def get_posts_by_pk(pk: int, user: CustomUser) -> (int, dict):
    '''
    Получение постов пользователя по pk

    Args:
        pk: идентификатор пользователя
        user: пользователь

    Returns:
        Кортеж из статуса и словаря данных
    '''

    logger.info(
        msg=f'Получение списка постов автора с pk {pk} пользователем {user}',
    )
    try:
        author = CustomUser.objects.filter(
            pk=pk,
        ).prefetch_related(
            Prefetch("posts", queryset=Post.objects.filter(
                Q(author=user) & Q(author__pk=pk) | Q(author__pk=pk) & Q(hidden=False)
            ))).first()
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при проверке существования автора '
                f'с pk {pk} пользователем {user}',
            exc_info=True,
        )
        return generate_response(
            status_code=500,
        )

    if author is None:
        logger.error(
            msg=f'Автор с pk {pk} не найден пользователем {user}',
        )
        return generate_response(
            status_code=404,
        )

    data = AuthorPostSerializer(
        instance=author,
    ).data

    logger.info(
        msg=f'Список постов автора с pk {pk} пользователем {user} получен: {data}',
    )
    return generate_response(
        status_code=200,
        data=data,
    )
