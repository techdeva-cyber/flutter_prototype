from django.db import models
from accounts.models import User
from classes.models import Class


class AttendanceSession(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_sessions')
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_obj.course_name} - {self.session_date}"


class AttendanceRecord(models.Model):
    METHOD_CHOICES = (
        ('manual', 'Manual'),
        ('qr', 'QR Code'),
        ('facial', 'Facial Recognition'),
    )
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    is_present = models.BooleanField(default=False)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_attendances')
    recorded_at = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    altitude = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.session.class_obj.course_name} - {'Present' if self.is_present else 'Absent'}"


class QRCode(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='qr_codes')
    code = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"QR for {self.session.class_obj.course_name} - {self.session.session_date}"