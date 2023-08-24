import imp
from django.conf import settings
from django.core.mail import send_mail, EmailMessage


def send_account_activation_email(email, email_token, roll):
    print("I am here in send_account_activation_email")
    subject = "Your account needs to be verified"
    email_from = settings.EMAIL_HOST_USER
    message = f"Hi, click on the link to activate your account http://127.0.0.1:8000/accounts/activate/{roll}/{email_token}"
    send_mail(subject, message, email_from, [email])


def send_email_with_order_confirmation_pdf(subject, message, recipient_list, file_path):
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=recipient_list,
    )

    mail.attach_file(file_path)
    mail.send()
