from django.db import models
from accounts.models import User
from classes.models import Class


class LocationVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_verifications')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='location_verifications')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.class_obj.course_name} - Verified: {self.is_verified}"


class FacialRecognitionData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='facial_data')
    facial_encoding = models.TextField()  # Store as JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Facial data for {self.user.username}"


class AttendanceAnalytics(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='analytics')
    total_sessions = models.IntegerField(default=0)
    total_attendance = models.IntegerField(default=0)
    average_attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.class_obj.course_name}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('attendance', 'Attendance'),
        ('class', 'Class'),
        ('system', 'System'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"