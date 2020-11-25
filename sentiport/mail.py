from flask import render_template
from flask_mail import Message
from threading import Thread
from email.message import EmailMessage
from sentiport import app, mail


def create_email_message(from_address, to_address, subject,
                        plaintext, html=None):
    msg = EmailMessage()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.set_content(plaintext)
    if html is not None:
        msg.add_alternative(html, subtype='html')
    return msg


def get_user_mail(targetmail):
    for i in range(len(targetmail)):
        if targetmail[i] == '@':
            uname_targetmail = (targetmail[0:i])
            domain_targetmail = (targetmail[-(len(targetmail)-i-1):])
            return uname_targetmail, domain_targetmail


# Got this from pedagogy, later will be modified
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_pw_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset your password on Pedagogy',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

