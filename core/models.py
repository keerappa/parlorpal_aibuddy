# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.core.exceptions import ValidationError
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# class CustomUser(AbstractUser):
#     email_verified = models.BooleanField(default=False, help_text="Whether the user's email has been verified")
#     verification_token = models.CharField(max_length=100, blank=True, help_text="Token for email verification")
#     token_created_at = models.DateTimeField(null=True, blank=True, help_text="When the verification token was created")
#     notifications_enabled = models.BooleanField(default=False, help_text="Whether user wants festival notifications")
    
#     def __str__(self):
#         return self.username

# class BusinessProfile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='businessprofile')
#     business_name = models.CharField(max_length=100, blank=True)
#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='uploads/', null=True, blank=True)
#     image_url = models.URLField(blank=True, help_text="Cloudinary URL for business logo")
    
#     # Detailed Location Fields
#     country = models.CharField(max_length=100, blank=True, help_text="Country")
#     state = models.CharField(max_length=100, blank=True, help_text="State/Province")
#     district = models.CharField(max_length=100, blank=True, help_text="District")
#     town = models.CharField(max_length=100, blank=True, help_text="Town/City")
#     address = models.TextField(blank=True, help_text="Complete business address")
    
#     # Legacy location field (kept for backward compatibility)
#     location = models.CharField(max_length=200, blank=True, help_text="Business address or location")
    
#     # Contact Information
#     phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    
#     # Business Hours
#     business_hours_start = models.TimeField(null=True, blank=True, help_text="Opening time")
#     business_hours_end = models.TimeField(null=True, blank=True, help_text="Closing time")
#     timing = models.CharField(max_length=100, blank=True, help_text="Business hours (e.g., 9:00 AM - 8:00 PM)")

#     class Meta:
#         verbose_name = "Business Profile"
#         verbose_name_plural = "Business Profiles"

#     def clean(self):
#         """Custom validation"""
#         if self.user_id and BusinessProfile.objects.filter(user=self.user).exclude(pk=self.pk).exists():
#             raise ValidationError({
#                 'user': f'User {self.user.username} already has a business profile.'
#             })

#     def save(self, *args, **kwargs):
#         # Only run full_clean if user is set
#         if self.user_id:
#             self.full_clean()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         if self.business_name:
#             return self.business_name
#         if self.user_id:
#             return f"Profile of {self.user.username}"
#         return "Unassigned BusinessProfile"

# # Signal to automatically create business profile for new users
# @receiver(post_save, sender=CustomUser)
# def create_business_profile(sender, instance, created, **kwargs):
#     """Create a business profile for new users"""
#     if created:
#         BusinessProfile.objects.create(
#             user=instance,
#             business_name=f"{instance.username}'s Business",
#             description=f"Business profile for {instance.username}"
#         )

# @receiver(post_save, sender=CustomUser)
# def save_business_profile(sender, instance, **kwargs):
#     """Save the business profile when user is saved"""
#     if hasattr(instance, 'businessprofile'):
#         instance.businessprofile.save()

# class SearchHistory(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     search_query = models.CharField(max_length=200)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-created_at']  # Most recent first
#         unique_together = ['user', 'search_query']  # Prevent duplicates
    
#     def __str__(self):
#         return f"{self.user.username}: {self.search_query}"


# class PosterGeneration(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     promotion_name = models.CharField(max_length=200)
#     offer_type = models.CharField(max_length=100)
#     poster_url = models.CharField(max_length=500)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-created_at']  # Most recent first
    
#     def __str__(self):
#         return f"{self.user.username}: {self.promotion_name} - {self.created_at.strftime('%Y-%m-%d')}"


# class Festival(models.Model):
#     name = models.CharField(max_length=100, help_text="Name of the festival")
#     date = models.DateField(help_text="Date of the festival")
#     notification_days = models.IntegerField(default=3, help_text="Days before festival to send notification")
#     send_on_festival_day = models.BooleanField(default=True, help_text="Send notification on the festival day itself")
#     is_active = models.BooleanField(default=True, help_text="Whether this festival is active for notifications")
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['date']
    
#     def __str__(self):
#         return f"{self.name} - {self.date}"
    
#     @property
#     def notification_date(self):
#         """Calculate when pre-festival notification should be sent"""
#         from datetime import timedelta
#         return self.date - timedelta(days=self.notification_days)
    
#     @property
#     def festival_day_date(self):
#         """Return the festival day itself"""
#         return self.date


# class UserHistory(models.Model):
#     """Track all user activities including poster generation, text generation, and logo uploads"""
#     ACTION_TYPES = [
#         ('poster_generation', 'Poster Generation'),
#         ('text_generation', 'Text Generation'),
#         ('logo_upload', 'Logo Upload'),
#     ]
    
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_history')
#     action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
#     input_data = models.JSONField(help_text="Original input data from user")
#     output_data = models.TextField(help_text="Generated content or Cloudinary URL")
#     prompt_used = models.TextField(blank=True, help_text="Final prompt sent to AI")
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "User History"
#         verbose_name_plural = "User Histories"
    
#     def __str__(self):
#         return f"{self.user.username} - {self.get_action_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
#     @property
#     def is_image_action(self):
#         """Check if this action involves an image"""
#         return self.action_type in ['poster_generation', 'logo_upload']
    
#     @property
#     def is_text_action(self):
#         """Check if this action involves text generation"""
#         return self.action_type == 'text_generation'

# # 2FA model to store TOTP secret per user
# class TwoFactorAuth(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='twofactor')
#     secret = models.CharField(max_length=64, blank=True, help_text="Base32 TOTP secret")
#     enabled = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     last_verified_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"2FA for {self.user.username} ({'enabled' if self.enabled else 'disabled'})"


# # Password Reset OTP model
# class PasswordResetOTP(models.Model):
#     METHOD_CHOICES = [
#         ('email', 'Email'),
#         ('phone', 'Phone'),
#     ]
    
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='password_reset_otps')
#     otp = models.CharField(max_length=6, help_text="6-digit OTP code")
#     method = models.CharField(max_length=10, choices=METHOD_CHOICES, help_text="OTP delivery method")
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(help_text="OTP expiration time (10 minutes from creation)")
#     is_used = models.BooleanField(default=False, help_text="Whether OTP has been used")
#     attempts = models.IntegerField(default=0, help_text="Number of verification attempts")
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Password Reset OTP"
#         verbose_name_plural = "Password Reset OTPs"
    
#     def __str__(self):
#         return f"{self.user.username} - {self.method} - {self.otp} ({'used' if self.is_used else 'active'})"
    
#     def is_valid(self):
#         """Check if OTP is still valid (not expired and not used)"""
#         from django.utils import timezone
#         return not self.is_used and self.expires_at > timezone.now()




import sys
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    email_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's email has been verified"
    )
    verification_token = models.CharField(
        max_length=100,
        blank=True,
        help_text="Token for email verification"
    )
    token_created_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the verification token was created"
    )
    notifications_enabled = models.BooleanField(
        default=False,
        help_text="Whether user wants festival notifications"
    )

    def __str__(self):
        return self.username


class BusinessProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="businessprofile"
    )
    business_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="uploads/", null=True, blank=True)
    image_url = models.URLField(blank=True, help_text="Cloudinary URL for business logo")

    # Detailed Location Fields
    country = models.CharField(max_length=100, blank=True, help_text="Country")
    state = models.CharField(max_length=100, blank=True, help_text="State/Province")
    district = models.CharField(max_length=100, blank=True, help_text="District")
    town = models.CharField(max_length=100, blank=True, help_text="Town/City")
    address = models.TextField(blank=True, help_text="Complete business address")

    # Legacy location field (kept for backward compatibility)
    location = models.CharField(max_length=200, blank=True, help_text="Business address or location")

    # Contact Information
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")

    # Business Hours
    business_hours_start = models.TimeField(null=True, blank=True, help_text="Opening time")
    business_hours_end = models.TimeField(null=True, blank=True, help_text="Closing time")
    timing = models.CharField(max_length=100, blank=True, help_text="Business hours (e.g., 9:00 AM - 8:00 PM)")

    class Meta:
        verbose_name = "Business Profile"
        verbose_name_plural = "Business Profiles"

    def clean(self):
        """Custom validation"""
        if self.user_id and BusinessProfile.objects.filter(user=self.user).exclude(pk=self.pk).exists():
            raise ValidationError({
                "user": f"User {self.user.username} already has a business profile."
            })

    def save(self, *args, **kwargs):
        # Only run full_clean if user is set
        if self.user_id:
            self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.business_name:
            return self.business_name
        if self.user_id:
            return f"Profile of {self.user.username}"
        return "Unassigned BusinessProfile"


# ✅ Signal to automatically create business profile for new users
@receiver(post_save, sender=CustomUser)
def create_business_profile(sender, instance, created, **kwargs):
    """
    Create a BusinessProfile for new users.
    IMPORTANT: Skip during loaddata, otherwise fixture import crashes due to OneToOne unique constraint.
    """
    if "loaddata" in sys.argv:
        return

    if created:
        BusinessProfile.objects.create(
            user=instance,
            business_name=f"{instance.username}'s Business",
            description=f"Business profile for {instance.username}"
        )


@receiver(post_save, sender=CustomUser)
def save_business_profile(sender, instance, **kwargs):
    """
    Save the business profile when user is saved.
    Skip during loaddata to avoid interference.
    """
    if "loaddata" in sys.argv:
        return

    if hasattr(instance, "businessprofile"):
        instance.businessprofile.save()


class SearchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    search_query = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "search_query"]

    def __str__(self):
        return f"{self.user.username}: {self.search_query}"


class PosterGeneration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # ✅ FIX: was CharField(max_length=200) -> fails in Postgres if string > 200
    promotion_name = models.TextField()

    offer_type = models.CharField(max_length=100)
    poster_url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.promotion_name[:50]} - {self.created_at.strftime('%Y-%m-%d')}"


class Festival(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the festival")
    date = models.DateField(help_text="Date of the festival")
    notification_days = models.IntegerField(default=3, help_text="Days before festival to send notification")
    send_on_festival_day = models.BooleanField(default=True, help_text="Send notification on the festival day itself")
    is_active = models.BooleanField(default=True, help_text="Whether this festival is active for notifications")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.name} - {self.date}"

    @property
    def notification_date(self):
        """Calculate when pre-festival notification should be sent"""
        from datetime import timedelta
        return self.date - timedelta(days=self.notification_days)

    @property
    def festival_day_date(self):
        """Return the festival day itself"""
        return self.date


class UserHistory(models.Model):
    """Track all user activities including poster generation, text generation, and logo uploads"""
    ACTION_TYPES = [
        ("poster_generation", "Poster Generation"),
        ("text_generation", "Text Generation"),
        ("logo_upload", "Logo Upload"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_history")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    input_data = models.JSONField(help_text="Original input data from user")
    output_data = models.TextField(help_text="Generated content or Cloudinary URL")
    prompt_used = models.TextField(blank=True, help_text="Final prompt sent to AI")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User History"
        verbose_name_plural = "User Histories"

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_image_action(self):
        return self.action_type in ["poster_generation", "logo_upload"]

    @property
    def is_text_action(self):
        return self.action_type == "text_generation"


class TwoFactorAuth(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="twofactor")
    secret = models.CharField(max_length=64, blank=True, help_text="Base32 TOTP secret")
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"2FA for {self.user.username} ({'enabled' if self.enabled else 'disabled'})"


class PasswordResetOTP(models.Model):
    METHOD_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="password_reset_otps")
    otp = models.CharField(max_length=6, help_text="6-digit OTP code")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, help_text="OTP delivery method")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="OTP expiration time (10 minutes from creation)")
    is_used = models.BooleanField(default=False, help_text="Whether OTP has been used")
    attempts = models.IntegerField(default=0, help_text="Number of verification attempts")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"

    def __str__(self):
        return f"{self.user.username} - {self.method} - {self.otp} ({'used' if self.is_used else 'active'})"

    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)"""
        from django.utils import timezone
        return (not self.is_used) and (self.expires_at > timezone.now())
