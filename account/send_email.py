import secrets
import base64
import random
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives




def generate_verification_code():
    code = str(random.randint(100000, 999999))
    return code

def generate_token(length=150):
    token_bytes = secrets.token_bytes(length)
    token = base64.urlsafe_b64encode(token_bytes).decode('utf-8')
    return token

def send_verification_email(email, verification_code, token):
    subject = 'کد تأیید فراموشی رمز عبور'
    verification_url = f'http://localhost:8000/account/confirm_code/{token}'

    html_content = render_to_string('account/verification_email.html', {
        'verification_code': verification_code,
        'verification_url': verification_url,
    })

    from_email = 'Your Email@gmail.com' # Your Email
    recipient_list = [email]

    email_message = EmailMultiAlternatives(subject, '', from_email, recipient_list)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


def send_registration_email(email, verification_code, token):
    subject = 'کد تأیید ثبت نام'
    verification_url = f'http://localhost:8000/account/confirm_registration_code/{token}'

    html_content = render_to_string('account/verification_email.html', {
        'verification_code': verification_code,
        'verification_url': verification_url,
    })

    from_email = 'Your Email@gmail.com' # Your Email
    recipient_list = [email]

    email_message = EmailMultiAlternatives(subject, '', from_email, recipient_list)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


