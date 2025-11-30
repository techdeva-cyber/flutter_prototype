from django.contrib import admin
from .models import Class, ClassSchedule


class ClassScheduleInline(admin.TabularInline):
    model = ClassSchedule
    extra = 1


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'course_id', 'semester', 'section', 'teacher', 'room_number')
    list_filter = ('semester', 'section', 'teacher')
    search_fields = ('course_name', 'course_id', 'teacher__username')
    inlines = [ClassScheduleInline]


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'weekday', 'start_time', 'end_time')
    list_filter = ('weekday', 'class_obj')