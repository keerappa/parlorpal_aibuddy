"""
SMS utilities for sending OTP via Firebase Phone Authentication
"""

import os
import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings


def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_sms_otp(phone_number, otp):
    """
    Send OTP via SMS using Firebase Phone Auth
    
    Note: Firebase Phone Auth handles SMS sending automatically on the client side.
    This function is a placeholder for backend OTP generation and storage.
    The actual SMS is sent by Firebase SDK on the frontend.
    
    For backend SMS sending, you would need a paid service like:
    - Twilio
    - MSG91 (India)
    - Firebase Blaze plan
    """
    # Firebase Phone Auth works differently - the client SDK handles SMS
    # We just need to generate and store the OTP for verification
    
    print(f"DEBUG: OTP {otp} generated for phone {phone_number}")
    print(f"INFO: Firebase will handle SMS delivery on the client side")
    
    return {
        'success': True,
        'message': 'OTP generated successfully. Firebase will send SMS.',
        'otp': otp  # In production, don't return OTP in response!
    }


def send_otp_via_firebase(user, method='phone'):
    """
    Generate OTP and prepare for Firebase Phone Auth
    
    Args:
        user: CustomUser instance
        method: 'phone' or 'email'
    
    Returns:
        dict with success status and OTP (for development only)
    """
    from .models import PasswordResetOTP
    
    # Generate OTP
    otp = generate_otp()
    
    # Set expiration (10 minutes from now)
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Save OTP to database
    otp_record = PasswordResetOTP.objects.create(
        user=user,
        otp=otp,
        method=method,
        expires_at=expires_at
    )
    
    if method == 'phone':
        # Firebase Phone Auth will handle the actual SMS
        result = send_sms_otp(user.businessprofile.phone if hasattr(user, 'businessprofile') else '', otp)
    else:
        # Use email for OTP
        from .email_utils import send_otp_email
        result = send_otp_email(user.email, otp)
    
    return {
        'success': result.get('success', True),
        'otp_id': otp_record.id,
        'method': method,
        'expires_at': expires_at.isoformat()
    }


def verify_otp(user, otp_code):
    """
    Verify OTP for password reset
    
    Args:
        user: CustomUser instance
        otp_code: 6-digit OTP string
    
    Returns:
        dict with success status and message
    """
    from .models import PasswordResetOTP
    
    # Find the most recent unused OTP for this user
    try:
        otp_record = PasswordResetOTP.objects.filter(
            user=user,
            otp=otp_code,
            is_used=False
        ).latest('created_at')
    except PasswordResetOTP.DoesNotExist:
        return {'success': False, 'message': 'Invalid OTP code'}
    
    # Increment attempts
    otp_record.attempts += 1
    otp_record.save()
    
    # Check if OTP is still valid
    if not otp_record.is_valid():
        return {'success': False, 'message': 'OTP has expired or been used'}
    
    # Check max attempts (3 tries)
    if otp_record.attempts > 3:
        return {'success': False, 'message': 'Too many attempts. Please request a new OTP'}
    
    # Mark as used
    otp_record.is_used = True
    otp_record.save()
    
    return {
        'success': True,
        'message': 'OTP verified successfully',
        'otp_record': otp_record
    }
