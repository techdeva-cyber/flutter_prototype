from django.contrib import admin
from .models import LocationVerification, FacialRecognitionData, AttendanceAnalytics, Notification


@admin.register(LocationVerification)
class LocationVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_obj', 'latitude', 'longitude', 'is_verified', 'verified_at')
    list_filter = ('is_verified', 'verified_at', 'class_obj')
    search_fields = ('user__username', 'class_obj__course_name')


@admin.register(FacialRecognitionData)
class FacialRecognitionDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)


@admin.register(AttendanceAnalytics)
class AttendanceAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'total_sessions', 'total_attendance', 'average_attendance', 'last_updated')
    search_fields = ('class_obj__course_name',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title')