import os
import smtplib
import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def _smtp_settings() -> dict[str, object]:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM", user)

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "sender": sender,
    }


def send_activation_email(to_email: str, to_name: str, activation_url: str) -> bool:
    settings = _smtp_settings()
    if not settings["user"] or not settings["password"] or not settings["sender"]:
        return False

    msg = EmailMessage()
    msg["Subject"] = "Activa tu acceso al Modulo de Horarios"
    msg["From"] = settings["sender"]
    msg["To"] = to_email

    saludo = to_name or "Docente"
    text_body = (
        f"Hola {saludo},\n\n"
        "Bienvenido(a) al Modulo de Horarios.\n"
        "Para activar tu cuenta y crear una nueva contrasena, ingresa al siguiente enlace:\n\n"
        f"{activation_url}\n\n"
        "Si no solicitaste este acceso, puedes ignorar este mensaje.\n"
    )

    msg.set_content(text_body)
    msg.add_alternative(
        """
        <html>
          <body style="font-family: Arial, sans-serif; color: #1f2937;">
            <p>Hola <strong>{saludo}</strong>,</p>
            <p>Bienvenido(a) al Modulo de Horarios.</p>
            <p>Para activar tu cuenta y crear una nueva contrasena, ingresa al siguiente enlace:</p>
            <p><a href="{activation_url}">{activation_url}</a></p>
            <p>Si no solicitaste este acceso, puedes ignorar este mensaje.</p>
          </body>
        </html>
        """.format(saludo=saludo, activation_url=activation_url),
        subtype="html",
    )

    try:
        with smtplib.SMTP(settings["host"], settings["port"]) as server:
            server.starttls()
            server.login(settings["user"], settings["password"])
            server.send_message(msg)
    except Exception as exc:
        logger.error(f"SMTP error sending activation email to {to_email}: {exc}")
        return False

    return True
