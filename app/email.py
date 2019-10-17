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
    send_email(
            subject = '[WaykiLeaks] So you forgot your password',
            sender = app.config['SENDGRID_DEFAULT_FROM'],
            recipients = user.email,
            text_body = render_template('email/passreset.txt', user=user, token=token),
            html_body = render_template('email/passreset.html', user=user, token=token)
    )

def quote_approved_email(user, quote):
    send_email(
            subject = '[WaykiLeaks] Your quote has been approved',
            sender = app.config['SENDGRID_DEFAULT_FROM'],
            recipients = user.email,
            text_body = render_template('email/qapprove.txt', user=user, quote=quote),
            html_body = render_template('email/qapprove.html', user=user, quote=quote)
    )

def quote_denied_email(user, quote):
    send_email(
            subject = '[WaykiLeaks] Your quote has been denied',
            sender = app.config['SENDGRID_DEFAULT_FROM'],
            recipients = user.email,
            text_body = render_template('email/qdeny.txt', user=user, quote=quote),
            html_body = render_template('email/qdeny.html', user=user, quote=quote)
    )

def ban_email(user):
    send_email(
            subject = '[WaykiLeaks] You have been banned',
            sender = app.config['SENDGRID_DEFAULT_FROM'],
            recipients = user.email,
            text_body = render_template('email/ban.txt', user=user),
            html_body = render_template('email/ban.html', user=user)
    )

def unban_email(user):
    send_email(
            subject = '[WaykiLeaks] You have been unbanned',
            sender = app.config['SENDGRID_DEFAULT_FROM'],
            recipients = user.email,
            text_body = render_template('email/unban.txt', user=user),
            html_body = render_template('email/unban.html', user=user)
    )
