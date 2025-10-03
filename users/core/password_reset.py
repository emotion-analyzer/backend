# ruff: noqa: E501
from email.message import EmailMessage

import aiosmtplib

from users.config import config


async def send_email(to_email: str, subject: str, body: str):
    """Send email to receiver, with specified subject and body."""
    message = EmailMessage()
    message["From"] = config.MAIL.ADDRESS
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content("This is the plain text version.")
    message.add_alternative(body, subtype="html")
    await aiosmtplib.send(
        message,
        hostname=config.MAIL.SMTP_SERVER,
        port=config.MAIL.SMTP_PORT,
        start_tls=True,
        username=config.MAIL.ADDRESS,
        password=config.MAIL.PASSWORD,
    )


async def send_password_reset_email(email, token):
    """Compose and send a password reset email."""
    html_content = f"""
    <html>
      <body>
        <p>Hola,</p>
        <p> Usted solicitó un cambio de contraseña. Puede acceder mediante el siguiente link:</p>
        <p>
          <a href="https://{config.FRONTEND.URL}/reset-password?token={token}" target="_blank">
            Cambie su contraseña aqui
          </a>
        </p>
        <p>Este enlace expira en 5 minutos. Si usted no solicito un cambio de contraseña, puede ignorar este mail.</p>
        <p>Gracias,</p>Equipo de Emotion Analyzer</p>
      </body>
    </html>
    """
    await send_email(to_email=email, subject="Emotion Analyzer - Recuperación de contraseña",
               body=html_content)
