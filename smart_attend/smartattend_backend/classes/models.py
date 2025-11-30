from django.db import models
from accounts.models import User


class Class(models.Model):
    course_id = models.CharField(max_length=20)
    course_name = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)
    section = models.CharField(max_length=10)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes')
    room_number = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    start_time = models.TimeField()
    end_time = models.TimeField()
    students = models.ManyToManyField(User, related_name='enrolled_classes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.course_name} - {self.section} ({self.semester})"


class ClassSchedule(models.Model):
    WEEKDAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.CharField(max_length=10, choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.class_obj.course_name} - {self.weekday}"