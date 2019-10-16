from flask import render_template
from app import app, mail

def send_email(subject, sender, recipients, text_body, html_body):
    mail.send_email(
            from_email=sender,
            to_email=recipients,
            subject=subject,
            text=text_body,
            html=html_body
    )

def send_password_reset_email(user):
    token = user.get_password_reset_token()
    send_email('[WaykiLeaks] So you forgot your password',
            sender = app.config['SENDGRID_DEFAULT_FROM'],
            recipients = user.email,
            text_body = render_template('email/passreset.txt', user=user, token=token),
            html_body=render_template('email/passreset.html', user=user, token=token)
    )
