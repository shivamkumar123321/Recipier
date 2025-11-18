"""
Email service for sending verification and password reset emails.

Supports:
- Mock mode for development/hackathon (logs emails)
- SendGrid integration for production (requires SENDGRID_API_KEY)
"""

from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import create_password_reset_token, create_verification_token

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails via SendGrid or mock mode."""

    def __init__(self):
        """Initialize email service."""
        self.use_mock = settings.ENVIRONMENT == "development" or settings.DEBUG
        self.sendgrid_api_key = getattr(settings, "SENDGRID_API_KEY", None)

        if not self.use_mock and not self.sendgrid_api_key:
            logger.warning(
                "SENDGRID_API_KEY not configured. Email service will use mock mode."
            )
            self.use_mock = True

        logger.info(
            f"Email service initialized in {'MOCK' if self.use_mock else 'SENDGRID'} mode"
        )

    async def send_verification_email(
        self, email: str, verification_url: str
    ) -> bool:
        """
        Send email verification link.

        Args:
            email: User email address
            verification_url: Full verification URL with token

        Returns:
            True if sent successfully
        """
        if self.use_mock:
            return await self._mock_send_email(
                to_email=email,
                subject="Verify Your Weight Coach Account",
                html_content=f"""
                <h1>Welcome to Weight Coach!</h1>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_url}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, you can safely ignore this email.</p>
                """,
            )
        else:
            return await self._sendgrid_send_email(
                to_email=email,
                subject="Verify Your Weight Coach Account",
                html_content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .button {{
                            background-color: #4CAF50;
                            color: white;
                            padding: 12px 24px;
                            text-decoration: none;
                            border-radius: 4px;
                            display: inline-block;
                        }}
                        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Welcome to Weight Coach!</h1>
                        <p>Thank you for signing up. Please verify your email address to get started.</p>
                        <p><a href="{verification_url}" class="button">Verify Email Address</a></p>
                        <p>Or copy and paste this link into your browser:</p>
                        <p>{verification_url}</p>
                        <p>This link will expire in 24 hours.</p>
                        <div class="footer">
                            <p>If you didn't create an account, you can safely ignore this email.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
            )

    async def send_password_reset_email(
        self, email: str, reset_url: str
    ) -> bool:
        """
        Send password reset link.

        Args:
            email: User email address
            reset_url: Full password reset URL with token

        Returns:
            True if sent successfully
        """
        if self.use_mock:
            return await self._mock_send_email(
                to_email=email,
                subject="Reset Your Weight Coach Password",
                html_content=f"""
                <h1>Password Reset Request</h1>
                <p>You requested to reset your password. Click the link below to proceed:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, you can safely ignore this email.</p>
                """,
            )
        else:
            return await self._sendgrid_send_email(
                to_email=email,
                subject="Reset Your Weight Coach Password",
                html_content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .button {{
                            background-color: #2196F3;
                            color: white;
                            padding: 12px 24px;
                            text-decoration: none;
                            border-radius: 4px;
                            display: inline-block;
                        }}
                        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                        .warning {{ color: #f44336; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Password Reset Request</h1>
                        <p>You requested to reset your Weight Coach password.</p>
                        <p><a href="{reset_url}" class="button">Reset Password</a></p>
                        <p>Or copy and paste this link into your browser:</p>
                        <p>{reset_url}</p>
                        <p class="warning">This link will expire in 1 hour.</p>
                        <div class="footer">
                            <p>If you didn't request this password reset, please ignore this email
                            or contact support if you're concerned about your account security.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
            )

    async def send_password_changed_notification(self, email: str) -> bool:
        """
        Send notification that password was changed.

        Args:
            email: User email address

        Returns:
            True if sent successfully
        """
        if self.use_mock:
            return await self._mock_send_email(
                to_email=email,
                subject="Your Password Was Changed",
                html_content="""
                <h1>Password Changed</h1>
                <p>This is a confirmation that your Weight Coach password was recently changed.</p>
                <p>If you didn't make this change, please contact support immediately.</p>
                """,
            )
        else:
            return await self._sendgrid_send_email(
                to_email=email,
                subject="Your Weight Coach Password Was Changed",
                html_content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .warning { color: #f44336; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Password Changed Successfully</h1>
                        <p>This is a confirmation that your Weight Coach password was recently changed.</p>
                        <p class="warning">If you didn't make this change, please contact our support team immediately.</p>
                        <p>For security reasons, you may want to review your recent account activity.</p>
                    </div>
                </body>
                </html>
                """,
            )

    async def _mock_send_email(
        self, to_email: str, subject: str, html_content: str
    ) -> bool:
        """
        Mock email sending for development.

        Logs email details instead of actually sending.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: Email HTML content

        Returns:
            Always True (mock always succeeds)
        """
        logger.info("=" * 80)
        logger.info("📧 MOCK EMAIL (Development Mode)")
        logger.info("=" * 80)
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 80)
        logger.info(html_content)
        logger.info("=" * 80)

        return True

    async def _sendgrid_send_email(
        self, to_email: str, subject: str, html_content: str
    ) -> bool:
        """
        Send email via SendGrid.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: Email HTML content

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Lazy import to avoid errors if sendgrid not installed
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=getattr(
                    settings, "FROM_EMAIL", "noreply@weightcoach.app"
                ),
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
            )

            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(
                    f"Failed to send email. Status: {response.status_code}"
                )
                return False

        except ImportError:
            logger.error(
                "SendGrid not installed. Install with: pip install sendgrid"
            )
            # Fall back to mock mode
            return await self._mock_send_email(to_email, subject, html_content)

        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            return False


# Singleton instance
email_service = EmailService()
