from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail

from notifications.models import (
    EmailConfiguration,
    EmailTemplate,
)
from users_api.models import CustomUser

from utils.logger import get_logger


logger = get_logger(__name__)


class Email:
    email_host_user = EMAIL_HOST_USER

    def __init__(self, email_type: str, mail_data: dict, recipient: CustomUser):
        self.email_type = email_type
        self.mail_data = mail_data
        self.recipient = recipient

    def _get_email_template(self):
        '''
        Получение шаблона письма

        Returns:
            Шаблон письма или None
        '''

        logger.info(
            msg=f'Поиск шаблона для письма {self.email_type}',
        )
        try:
            mail = EmailTemplate.objects.filter(email_type=self.email_type).first()
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при поиске шаблона письма {self.email_type}',
                exc_info=True,
            )
            return None
        return mail

    @property
    def get_send_email_configs(self) -> EmailConfiguration | None:
        '''
        Получение настроек email

        Returns:
            Объет EmailConfiguration или None
        '''

        logger.info(
            msg='Получение настроек email',
        )
        try:
            configs = EmailConfiguration.get_solo()
        except Exception as exc:
            logger.error(
                msg='Ошибка при получении настроек email',
                exc_info=True,
            )
            return None
        logger.info(
            msg='Настройки email получены',
        )
        return configs

    def formate_email_text(self) -> (int, dict):
        '''
        Форматирование текста для письма

        Returns:
            Кортеж из статуса и словаря данных
        '''

        logger.info(
            msg=f'Формирование текста для письма {self.email_type} '
                f'с данными {self.mail_data} пользователю {self.recipient}'
        )

        mail = self._get_email_template()
        if mail is None:
            logger.error(
                msg=f'Шаблон письма {self.email_type} не найден',
            )
            return 501, {}

        logger.info(
            msg=f'Шаблон письма {self.email_type} найден',
        )

        subject = mail.subject
        try:
            message = mail.message.format(**self.mail_data)
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при форматировании текста для письма {mail} '
                    f'с данными {self.mail_data} пользователю {self.recipient}',
                exc_info=True,
            )
            return 500, {}

        logger.info(
            msg=f'Текст для письма {mail} успешно сформирован',
        )
        return 200, {
            'subject': subject,
            'message': message,
        }

    def send(self) -> int:
        '''
        Отправка письма

        Returns:
            Статус
        '''

        email_settings = self.get_send_email_configs
        if not email_settings or not email_settings.send_emails:
            logger.warning(
                msg='Отправка писем отключена',
            )
            return 403

        status_code, email_text = self.formate_email_text()
        if status_code != 200:
            logger.error(
                msg=f'Не удалось сформировать текст для письма {self.email_type} '
                    f'пользователю {self.recipient}'
            )
            return status_code

        subject = email_text["subject"]
        logger.info(
            msg=f'Отправка письма {subject} пользователю {self.recipient}',
        )
        try:
            send_mail(
                subject=subject,
                message=email_text['message'],
                from_email=self.email_host_user,
                recipient_list=[self.recipient],
            )
        except Exception as exc:
            logger.error(
                msg=f'Произошла ошибка при отправке письма {subject} '
                    f'пользователю {self.recipient}',
                exc_info=True,
            )
            return 500

        logger.info(
            msg=f'Письмо {subject} пользователю {self.recipient} успешно отправлено',
        )
        return 200
