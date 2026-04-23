import io
import segno
from datetime import date
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from starlette.datastructures import UploadFile
from core.config import settings

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

async def send_booking_confirmation_email(
    user_email: str, user_name: str | None, booking_id: int, desk_id: int, booking_date: date
):
    """
    Sends a booking confirmation email with a QR code for check-in.
    """
    # 1. Create QR Code in memory. This could be a simple identifier or a full URL.
    checkin_data = f"BOOKING_ID:{booking_id}"
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
            <p>Hi {user_name or user_email},</p>
            <p>Your desk booking is confirmed!</p>
            <ul>
                <li><strong>Desk ID:</strong> {desk_id}</li>
                <li><strong>Date:</strong> {booking_date.strftime('%Y-%m-%d')}</li>
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
        recipients=[user_email],
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

async def send_booking_cancellation_email(
    user_email: str, user_name: str | None, desk_id: int, booking_date: date
):
    """
    Sends a booking cancellation email to the user.
    """
    # 1. Prepare Email Body
    html_body = f"""
    <html>
        <body>
            <h2>Booking Cancellation</h2>
            <p>Hi {user_name or user_email},</p>
            <p>This email is to confirm that your booking has been successfully cancelled.</p>
            <p>Details of the cancelled booking:</p>
            <ul>
                <li><strong>Desk ID:</strong> {desk_id}</li>
                <li><strong>Date:</strong> {booking_date.strftime('%Y-%m-%d')}</li>
            </ul>
            <p>If you did not request this cancellation, please contact support immediately.</p>
            <p>Thank you for using MyDesk.</p>
        </body>
    </html>
    """

    # 2. Prepare Email Message
    message = MessageSchema(
        subject="Your MyDesk Booking Has Been Cancelled",
        recipients=[user_email],
        body=html_body,
        subtype=MessageType.html
    )

    # 3. Send Email
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_desk_deleted_notification_email(
    user_email: str, user_name: str | None, booking_date: date, desk_id: int
):
    """
    Sends an email notifying the user that their booked desk was deleted.
    """
    html_body = f"""
    <html>
        <body>
            <h2>Important Update Regarding Your Booking</h2>
            <p>Hi {user_name or user_email},</p>
            <p>Please be advised that Desk ID <strong>{desk_id}</strong>, which you had booked for <strong>{booking_date.strftime('%Y-%m-%d')}</strong>, has been permanently removed from our system.</p>
            <p>As a result, your booking for this desk has been cancelled. We apologize for any inconvenience this may cause.</p>
            <p>Please log in to MyDesk to book an alternative desk for that date.</p>
            <p>Thank you for your understanding.</p>
            <p>The MyDesk Team</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Action Required: Your MyDesk Booking Has Been Cancelled",
        recipients=[user_email],
        body=html_body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_admin_booking_cancellation_email(
    user_email: str, user_name: str | None, desk_id: int, booking_date: date
):
    """
    Sends an email notifying the user that their booking was cancelled by an admin.
    """
    html_body = f"""
    <html>
        <body>
            <h2>Important Update Regarding Your Booking</h2>
            <p>Hi {user_name or user_email},</p>
            <p>Please be advised that your booking for Desk ID <strong>{desk_id}</strong> on <strong>{booking_date.strftime('%Y-%m-%d')}</strong> has been cancelled by an administrator.</p>
            <p>We apologize for any inconvenience this may cause.</p>
            <p>If you still require a desk for this date, please log in to MyDesk to make a new booking.</p>
            <p>Thank you for your understanding.</p>
            <p>The MyDesk Team</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Action Required: Your MyDesk Booking Has Been Cancelled",
        recipients=[user_email],
        body=html_body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_floor_deleted_notification_email(
    user_email: str, user_name: str | None, booking_date: date, desk_id: int, floor_name: str | None, floor_number: int
):
    """
    Sends an email notifying the user that their booking was cancelled because the entire floor was removed.
    """
    floor_identifier = floor_name or f"Floor {floor_number}"
    html_body = f"""
    <html>
        <body>
            <h2>Urgent: Your MyDesk Booking Has Been Cancelled</h2>
            <p>Hi {user_name or user_email},</p>
            <p>This is an important notification regarding your booking for Desk ID <strong>{desk_id}</strong> on <strong>{booking_date.strftime('%Y-%m-%d')}</strong>.</p>
            <p>The entire floor where this desk was located (<strong>{floor_identifier}</strong>) has been permanently removed from our system by an administrator.</p>
            <p>As a result, your booking has been cancelled. We sincerely apologize for this inconvenience.</p>
            <p>Please log in to MyDesk to book an alternative desk on a different floor.</p>
            <p>Thank you for your understanding.</p>
            <p>The MyDesk Team</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Urgent: Your MyDesk Booking Has Been Cancelled",
        recipients=[user_email],
        body=html_body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)