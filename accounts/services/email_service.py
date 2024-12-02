import threading

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string

User = get_user_model()


class EmailService:
    def send_activation_email(
        self, username: str, domain: str, to_email: str, uid: str, token: str
    ) -> None:
        mail_subject = "Activation link has been sent to your email id"
        from_email = settings.EMAIL_HOST_USER

        context = {
            "username": username,
            "domain": domain,
            "uid": uid,
            "token": token,
        }

        message = render_to_string("registration/acc_activate_email.html", context)
        send_mail(mail_subject, message, from_email, [to_email])

        # or for async
        # threading.Thread(target=send_mail, args=(mail_subject, message, from_email, [to_email])).start()
