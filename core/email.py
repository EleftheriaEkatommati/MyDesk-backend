import io
import segno
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from starlette.datastructures import UploadFile
from core.config import settings
from models.booking import Booking
from models.user import User

# Configuration for fastapi-mail from settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=True
)

async def send_booking_confirmation_email(user: User, booking: Booking):
    """
    Sends a booking confirmation email with a QR code for check-in.
    """
    # 1. Create QR Code in memory. This could be a simple identifier or a full URL.
    checkin_data = f"BOOKING_ID:{booking.id}"
    qr = segno.make(checkin_data, error='h') # High error correction
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=5, border=4)
    buffer.seek(0)

    # Create an UploadFile object for fastapi-mail from the in-memory buffer
    qr_upload_file = UploadFile(file=buffer, filename="checkin_qr.png")

    # 2. Prepare Email Body. For a real app, using Jinja2 templates is recommended.
    html_body = f"""
    <html>
        <body>
            <h2>Booking Confirmation</h2>
            <p>Hi {user.name or user.email},</p>
            <p>Your desk booking is confirmed!</p>
            <ul>
                <li><strong>Desk ID:</strong> {booking.desk_id}</li>
                <li><strong>Date:</strong> {booking.booking_date.strftime('%Y-%m-%d')}</li>
            </ul>
            <p>Please use the QR code below to check in at your desk:</p>
            <img src="cid:qr_code">
            <p>Thank you for using MyDesk.</p>
        </body>
    </html>
    """

    # 3. Prepare Email Message with embedded QR code
    message = MessageSchema(
        subject="Your MyDesk Booking Confirmation",
        recipients=[user.email],
        body=html_body,
        subtype=MessageType.html,
        attachments=[{
            'file': qr_upload_file,
            'headers': {'Content-ID': '<qr_code>'},
            'mime_type': 'image/png',
        }]
    )

    # 4. Send Email
    fm = FastMail(conf)
    await fm.send_message(message)