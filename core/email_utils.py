import uuid
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Festival


def generate_verification_token():
    """Generate a unique verification token"""
    return str(uuid.uuid4())


def send_verification_email(user):
    """Send email verification email to user"""
    try:
        # Generate verification token
        token = generate_verification_token()
        user.verification_token = token
        from django.utils import timezone
        user.token_created_at = timezone.now()
        user.save()
        
        # Create verification URL
        verification_url = f"{settings.SITE_URL}/verify-email/{token}/"
        
        # Email content
        subject = "🎉 Verify Your Email - ParlorPal"
        
        # HTML Email template
        html_message = render_to_string('core/emails/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'ParlorPal'
        })
        
        # Plain text version
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def send_festival_notification_email(user, festival, notification_type='pre'):
    """Send festival notification email to user
    
    Args:
        user: CustomUser instance
        festival: Festival instance
        notification_type: 'pre' for pre-festival, 'festival-day' for on festival day
    """
    try:
        if notification_type == 'pre':
            subject = f"🎊 {festival.name} is coming! Time to boost your business!"
            countdown_text = f"Only {festival.notification_days} days to go!"
        else:  # festival-day
            subject = f"🎉 Happy {festival.name}! Special offers for your business!"
            countdown_text = "Today is the day!"
        
        # HTML Email template
        html_message = render_to_string('core/emails/festival_notification.html', {
            'user': user,
            'festival': festival,
            'site_name': 'ParlorPal',
            'notification_type': notification_type,
            'countdown_text': countdown_text
        })
        
        # Plain text version
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending festival notification: {e}")
        return False


def send_festival_notification(user, festival):
    """Legacy function - now calls the new function"""
    return send_festival_notification_email(user, festival, 'pre')


def send_festival_notifications():
    """Send festival notifications to all eligible users"""
    from django.utils import timezone
    today = timezone.now().date()
    
    # Get festivals that need notifications today
    festivals = Festival.objects.filter(
        is_active=True
    )
    
    # Filter festivals that need notifications today
    festivals_to_notify = []
    for festival in festivals:
        if festival.notification_date == today:
            festivals_to_notify.append(festival)
    
    if not festivals_to_notify:
        return
    
    # Get users who have verified emails and enabled notifications
    from .models import CustomUser
    eligible_users = CustomUser.objects.filter(
        email_verified=True,
        notifications_enabled=True,
        is_active=True
    )
    
    for festival in festivals_to_notify:
        for user in eligible_users:
            send_festival_notification(user, festival)


def is_token_valid(user, token):
    """Check if verification token is valid and not expired"""
    if user.verification_token != token:
        return False
    
    # Token expires after 24 hours
    if user.token_created_at:
        from django.utils import timezone
        expiration_time = user.token_created_at + timedelta(hours=24)
        if timezone.now() > expiration_time:
            return False
    
    return True 


def send_password_reset_otp_email(user, otp):
    """Send password reset OTP via email"""
    try:
        subject = "🔐 Your Password Reset OTP - ParlorPal"
        
        # HTML Email template
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #A88BEB, #E94560); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: white; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #A88BEB; border: 2px dashed #A88BEB; border-radius: 8px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset OTP</h1>
                </div>
                <div class="content">
                    <p>Hello <strong>{user.username}</strong>,</p>
                    
                    <p>We received a request to reset your password. Use the OTP below to proceed:</p>
                    
                    <div class="otp-box">{otp}</div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Note:</strong>
                        <ul style="margin: 10px 0;">
                            <li>This OTP is valid for <strong>10 minutes</strong></li>
                            <li>Never share this OTP with anyone</li>
                            <li>If you didn't request this, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>After entering the OTP, you'll be able to set a new password for your ParlorPal account.</p>
                    
                    <p style="margin-top: 30px;">Best regards,<br><strong>ParlorPal Team</strong></p>
                </div>
                <div class="footer">
                    <p>© 2026 ParlorPal. AI-powered marketing for businesses.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Password Reset OTP - ParlorPal
        
        Hello {user.username},
        
        We received a request to reset your password. Use the OTP below to proceed:
        
        {otp}
        
        This OTP is valid for 10 minutes.
        Never share this OTP with anyone.
        If you didn't request this, please ignore this email.
        
        Best regards,
        ParlorPal Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending password reset OTP email: {e}")
        return False 