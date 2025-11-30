from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord, QRCode


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'session_date', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active', 'session_date', 'class_obj')
    search_fields = ('class_obj__course_name', 'class_obj__course_id')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'is_present', 'method', 'recorded_at')
    list_filter = ('is_present', 'method', 'session__class_obj', 'recorded_at')
    search_fields = ('student__username', 'session__class_obj__course_name')


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('session', 'code', 'created_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('session__class_obj__course_name', 'code')