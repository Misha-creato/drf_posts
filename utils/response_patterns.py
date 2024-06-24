status_messages = {
    200: 'Успешный успех',
    206: 'Успех наполовину',
    400: 'Невалидные данные',
    401: 'Ошибка авторизации',
    403: 'Доступ запрещен',
    404: 'Не найдено',
    406: 'Учетные данные уже существуют',
    500: 'Ошибка сервера',
    501: 'Не поддерживается',
}


def generate_response(status_code: int, data: dict | None = None) -> (int, dict):
    '''
    Генерация ответа

    Args:
        status_code: статус
        data: данные

    Returns:
        Кортеж из статуса и словаря данных
    '''

    return (
        status_code,
        {
            'message': status_messages.get(status_code, 'Неизвестный статус код'),
            'data': data if data else {}
        }
    )
