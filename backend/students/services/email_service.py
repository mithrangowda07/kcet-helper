import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(subject: str, message: str, recipient: str) -> None:
    if not recipient:
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error('Failed to send email to %s: %s', recipient, exc, exc_info=True)
        raise


def send_registration_approved_email(*, student_name: str, recipient: str) -> None:
    subject = 'Student Registration Approved'
    message = (
        f'Hello {student_name},\n\n'
        'Your student registration has been approved.\n\n'
        'You can now access the platform.\n\n'
        'Thank you.'
    )
    _send(subject, message, recipient)


def send_registration_rejected_email(
    *,
    student_name: str,
    recipient: str,
    rejection_reason: str,
) -> None:
    subject = 'Student Registration Rejected'
    message = (
        f'Hello {student_name},\n\n'
        'Your student registration has been rejected.\n\n'
        f'Reason:\n{rejection_reason}\n\n'
        'Please contact the administrator if you need further clarification.'
    )
    _send(subject, message, recipient)
