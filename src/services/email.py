from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="verified_email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):

    """
The send_email function sends an email to the user with a link that they can click on to verify their email address.
    The function takes in three parameters:
        -email: the user's email address, which is used as a unique identifier for each account.
        -username: the username of the account being created. This is included in case there are multiple accounts associated with one email address, so that we know which account we're verifying when sending out emails.
        -host: this parameter contains information about where our application is hosted (i.e., localhost or Heroku). It's needed because it will be

:param email: EmailStr: Specify the type of parameter that is expected
:param username: str: Pass the username of the user to be sent an email
:param host: str: Pass the hostname of the server to the email template
:return: The result of the await fm
:doc-author: Trelent
"""
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
