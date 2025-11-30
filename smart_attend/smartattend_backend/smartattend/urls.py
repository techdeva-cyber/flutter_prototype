"""
URL configuration for smartattend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import register_user, login_user, logout_user, user_profile, update_profile, get_students, get_teachers
from classes.views import get_classes, create_class, get_class_detail, update_class, delete_class, enroll_students, get_teacher_classes, get_student_classes
from attendance.views import get_attendance_sessions, create_attendance_session, get_session_detail, mark_attendance, generate_qr_code, scan_qr_code, get_class_attendance_summary, get_student_attendance
from core.views import verify_location, save_facial_data, verify_facial_data, get_notifications, mark_notification_read, get_analytics, update_analytics

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('api/auth/register/', register_user, name='register'),
    path('api/auth/login/', login_user, name='login'),
    path('api/auth/logout/', logout_user, name='logout'),
    path('api/auth/profile/', user_profile, name='user-profile'),
    path('api/auth/profile/update/', update_profile, name='update-profile'),
    
    # User management URLs
    path('api/users/students/', get_students, name='get-students'),
    path('api/users/teachers/', get_teachers, name='get-teachers'),
    
    # Class management URLs
    path('api/classes/', get_classes, name='get-classes'),
    path('api/classes/create/', create_class, name='create-class'),
    path('api/classes/<int:class_id>/', get_class_detail, name='class-detail'),
    path('api/classes/<int:class_id>/update/', update_class, name='update-class'),
    path('api/classes/<int:class_id>/delete/', delete_class, name='delete-class'),
    path('api/classes/<int:class_id>/enroll/', enroll_students, name='enroll-students'),
    path('api/classes/teacher/<int:teacher_id>/', get_teacher_classes, name='teacher-classes'),
    path('api/classes/student/<int:student_id>/', get_student_classes, name='student-classes'),
    
    # Attendance management URLs
    path('api/attendance/sessions/', get_attendance_sessions, name='get-sessions'),
    path('api/attendance/sessions/create/', create_attendance_session, name='create-session'),
    path('api/attendance/sessions/<int:session_id>/', get_session_detail, name='session-detail'),
    path('api/attendance/sessions/<int:session_id>/mark/', mark_attendance, name='mark-attendance'),
    path('api/attendance/sessions/<int:session_id>/qr/generate/', generate_qr_code, name='generate-qr'),
    path('api/attendance/qr/scan/', scan_qr_code, name='scan-qr'),
    path('api/attendance/classes/<int:class_id>/summary/', get_class_attendance_summary, name='class-attendance-summary'),
    path('api/attendance/student/<int:student_id>/', get_student_attendance, name='student-attendance'),
    path('api/attendance/student/', get_student_attendance, name='my-attendance'),
    
    # Core functionality URLs
    path('api/location/verify/', verify_location, name='verify-location'),
    path('api/facial/save/', save_facial_data, name='save-facial-data'),
    path('api/facial/verify/', verify_facial_data, name='verify-facial-data'),
    path('api/notifications/', get_notifications, name='get-notifications'),
    path('api/notifications/<int:notification_id>/read/', mark_notification_read, name='mark-notification-read'),
    path('api/analytics/class/<int:class_id>/', get_analytics, name='get-analytics'),
    path('api/analytics/class/<int:class_id>/update/', update_analytics, name='update-analytics'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)