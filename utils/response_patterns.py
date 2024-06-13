status_messages = {
    200: 'Успешный успех',
    400: 'Невалидные данные',
    401: 'Ошибка авторизации',
    404: 'Не найдено',
    500: 'Ошибка сервера',
}


def generate_response(status_code: int, data: dict | None = None) -> (int, dict):
    return (
        status_code,
        {
            'message': status_messages.get(status_code, 'Неизвестный статус код'),
            'data': data if data else {}
        }
    )
