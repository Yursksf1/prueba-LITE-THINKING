"""
Email Service for sending inventory reports.

This service handles email sending with PDF attachments,
separating email logic from the HTTP layer.
"""
from io import BytesIO
from typing import Optional
from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails with PDF attachments.
    
    This service is designed to be reusable and independent of the HTTP layer.
    It can be configured to use different email backends (SMTP, SendGrid, AWS SES, etc.)
    """
    
    def __init__(self):
        """Initialize the email service."""
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    
    def send_inventory_report(
        self,
        recipient_email: str,
        pdf_buffer: BytesIO,
        company_name: Optional[str] = None,
        company_nit: Optional[str] = None
    ) -> bool:
        """
        Send inventory report via email with PDF attachment.
        
        Args:
            recipient_email: Email address of the recipient
            pdf_buffer: BytesIO buffer containing the PDF document
            company_name: Optional company name for the email subject/body
            company_nit: Optional company NIT for the email subject/body
            
        Returns:
            bool: True if email sent successfully, False otherwise
            
        Raises:
            Exception: If email sending fails critically
            
        Example:
            >>> email_service = EmailService()
            >>> success = email_service.send_inventory_report(
            ...     'user@example.com',
            ...     pdf_buffer,
            ...     company_name='Acme Corp',
            ...     company_nit='123456789'
            ... )
        """
        try:
            # Build email subject
            if company_name:
                subject = f"Reporte de Inventario - {company_name}"
            else:
                subject = "Reporte de Inventario"
            
            # Build email body
            body_parts = ["Estimado usuario,\n\n"]
            body_parts.append("Adjunto encontrará el reporte de inventario solicitado.\n\n")
            
            if company_name:
                body_parts.append(f"Empresa: {company_name}\n")
            if company_nit:
                body_parts.append(f"NIT: {company_nit}\n")
            
            body_parts.append("\nEste es un correo automático, por favor no responder.\n\n")
            body_parts.append("Saludos cordiales,\n")
            body_parts.append("Sistema de Gestión de Inventario")
            
            body = "".join(body_parts)
            
            # Build filename
            if company_nit:
                filename = f"inventario_{company_nit}.pdf"
            else:
                filename = "inventario.pdf"
            
            # Create email message
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=self.from_email,
                to=[recipient_email],
            )
            
            # Attach PDF
            pdf_buffer.seek(0)  # Reset buffer position
            email.attach(filename, pdf_buffer.read(), 'application/pdf')
            
            # Send email
            sent_count = email.send(fail_silently=False)
            
            if sent_count > 0:
                logger.info(f"Inventory report sent successfully to {recipient_email}")
                return True
            else:
                logger.warning(f"Failed to send inventory report to {recipient_email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {str(e)}")
            raise Exception(f"Failed to send email: {str(e)}")
    
    def validate_email_configuration(self) -> bool:
        """
        Validate that email configuration is properly set up.
        
        Returns:
            bool: True if email is configured, False otherwise
        """
        # Check if email backend is configured
        email_backend = getattr(settings, 'EMAIL_BACKEND', None)
        
        if not email_backend:
            logger.warning("EMAIL_BACKEND not configured in settings")
            return False
        
        # Console backend is OK for development
        if 'console' in email_backend.lower():
            return True
        
        # For SMTP, check required settings
        if 'smtp' in email_backend.lower():
            required_settings = ['EMAIL_HOST', 'EMAIL_PORT']
            for setting in required_settings:
                if not getattr(settings, setting, None):
                    logger.warning(f"{setting} not configured in settings")
                    return False
        
        return True
