from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail

from notifications.models import (
    EmailConfiguration,
    EmailTemplate,
)
from users_api.models import CustomUser

from utils.logger import get_logger


logger = get_logger(__name__)


class SendMails:
    email_host_user = EMAIL_HOST_USER

    def __init__(self, email_type: str, mail_data: dict, recipient: CustomUser):
        self.email_type = email_type
        self.mail_data = mail_data
        self.recipient = recipient

    def get_email_template(self):
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

    def get_send_email_status(self) -> bool:
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
            return False
        logger.info(
            msg='Настройки email получены',
        )
        return configs.send_emails

    def formate_email_text(self) -> dict:
        logger.info(
            msg=f'Формирование текста для письма {self.email_type} \
            с данными {self.mail_data} пользователю {self.recipient}'
        )

        mail = self.get_email_template()
        if mail is None:
            logger.error(
                msg=f'Шаблон письма {self.email_type} не найден',
            )
            return {}

        logger.info(
            msg=f'Шаблон письма {self.email_type} найден',
        )

        subject = mail.subject
        try:
            message = mail.message.format(**self.mail_data)
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при форматировании текста для письма {mail} \
                с данными {self.mail_data} пользователю {self.recipient}',
                exc_info=True,
            )
            return {}

        logger.info(
            msg=f'Текст для письма {mail} успешно сформирован',
        )
        return {
            'subject': subject,
            'message': message,
        }

    def send_mail_to_user(self):
        if not self.get_send_email_status():
            logger.warning(
                msg='Отправка писем отключена',
            )
            return 403

        email_text = self.formate_email_text()
        if not email_text:
            logger.error(
                msg=f'Не удалось сформировать текст для письма {self.email_type} '
                    f'\ пользователю {self.recipient}'
            )
            return 400

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
                msg=f'Произошла ошибка при отправке письма {subject} \
                пользователю {self.recipient}',
                exc_info=True,
            )
            return 500

        logger.info(
            msg=f'Письмо {subject} пользователю {self.recipient} успешно отправлено',
        )
        return 200
