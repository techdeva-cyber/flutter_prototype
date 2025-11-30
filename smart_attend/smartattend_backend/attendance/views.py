from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from .models import AttendanceSession, AttendanceRecord, QRCode
from .serializers import (
    AttendanceSessionSerializer, AttendanceRecordSerializer, 
    QRCodeSerializer, AttendanceSummarySerializer, StudentAttendanceSerializer
)
from classes.models import Class
from accounts.models import User
import uuid
import datetime


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attendance_sessions(request):
    # Admin can see all sessions
    # Teacher can see sessions for their classes
    # Student can see sessions for their classes
    if request.user.role == 'admin':
        sessions = AttendanceSession.objects.all()
    elif request.user.role == 'teacher':
        sessions = AttendanceSession.objects.filter(class_obj__teacher=request.user)
    elif request.user.role == 'student':
        sessions = AttendanceSession.objects.filter(class_obj__students=request.user)
    else:
        return Response({'error': 'Invalid user role'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = AttendanceSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_attendance_session(request):
    if request.user.role != 'teacher':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    class_id = request.data.get('class_id')
    session_date = request.data.get('session_date')
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    
    try:
        class_obj = Class.objects.get(id=class_id, teacher=request.user)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if session already exists for this date and class
    existing_session = AttendanceSession.objects.filter(
        class_obj=class_obj,
        session_date=session_date
    ).first()
    
    if existing_session:
        return Response({'error': 'Session already exists for this date'}, status=status.HTTP_400_BAD_REQUEST)
    
    session = AttendanceSession.objects.create(
        class_obj=class_obj,
        session_date=session_date,
        start_time=start_time,
        end_time=end_time
    )
    
    # Create attendance records for all students in the class
    for student in class_obj.students.all():
        AttendanceRecord.objects.create(
            session=session,
            student=student,
            method='manual',
            recorded_by=request.user
        )
    
    serializer = AttendanceSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_detail(request, session_id):
    try:
        session = AttendanceSession.objects.get(id=session_id)
    except AttendanceSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if request.user.role == 'student' and request.user not in session.class_obj.students.all():
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'teacher' and session.class_obj.teacher != request.user:
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AttendanceSessionSerializer(session)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request, session_id):
    try:
        session = AttendanceSession.objects.get(id=session_id)
    except AttendanceSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if session is active
    if not session.is_active:
        return Response({'error': 'Session is not active'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check permissions
    if request.user.role == 'student' and request.user not in session.class_obj.students.all():
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'teacher' and session.class_obj.teacher != request.user:
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    student_id = request.data.get('student_id')
    is_present = request.data.get('is_present', False)
    method = request.data.get('method', 'manual')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    altitude = request.data.get('altitude')
    
    # If student_id is not provided, use the current user (for student self-marking)
    if not student_id:
        if request.user.role == 'student':
            student = request.user
        else:
            return Response({'error': 'Student ID required for teacher marking'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if request.user.role != 'teacher':
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if student is enrolled in the class
    if student not in session.class_obj.students.all():
        return Response({'error': 'Student not enrolled in this class'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update or create attendance record
    record, created = AttendanceRecord.objects.update_or_create(
        session=session,
        student=student,
        defaults={
            'is_present': is_present,
            'method': method,
            'recorded_by': request.user,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude
        }
    )
    
    serializer = AttendanceRecordSerializer(record)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_qr_code(request, session_id):
    if request.user.role != 'teacher':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        session = AttendanceSession.objects.get(id=session_id, class_obj__teacher=request.user)
    except AttendanceSession.DoesNotExist:
        return Response({'error': 'Session not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate unique QR code
    code = str(uuid.uuid4())
    expires_at = timezone.now() + datetime.timedelta(minutes=15)  # QR code valid for 15 minutes
    
    qr_code = QRCode.objects.create(
        session=session,
        code=code,
        expires_at=expires_at
    )
    
    serializer = QRCodeSerializer(qr_code)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_qr_code(request):
    if request.user.role != 'student':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    code = request.data.get('code')
    
    try:
        qr_code = QRCode.objects.get(code=code, is_active=True)
    except QRCode.DoesNotExist:
        return Response({'error': 'Invalid or expired QR code'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if QR code is expired
    if timezone.now() > qr_code.expires_at:
        qr_code.is_active = False
        qr_code.save()
        return Response({'error': 'QR code has expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if student is enrolled in the class
    session = qr_code.session
    if request.user not in session.class_obj.students.all():
        return Response({'error': 'You are not enrolled in this class'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark attendance
    record, created = AttendanceRecord.objects.update_or_create(
        session=session,
        student=request.user,
        defaults={
            'is_present': True,
            'method': 'qr',
            'recorded_by': request.user
        }
    )
    
    # Deactivate QR code after use
    qr_code.is_active = False
    qr_code.save()
    
    serializer = AttendanceRecordSerializer(record)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_class_attendance_summary(request, class_id):
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if request.user.role == 'student' and request.user not in class_obj.students.all():
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'teacher' and class_obj.teacher != request.user:
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get attendance summary by date
    summary = AttendanceRecord.objects.filter(
        session__class_obj=class_obj
    ).values('session__session_date').annotate(
        total_students=Count('student'),
        present_students=Count('student', filter=Q(is_present=True)),
        absent_students=Count('student', filter=Q(is_present=False))
    ).order_by('session__session_date')
    
    # Calculate percentages
    summary_data = []
    for item in summary:
        total = item['total_students']
        present = item['present_students']
        absent = item['absent_students']
        percentage = (present / total * 100) if total > 0 else 0
        
        summary_data.append({
            'date': item['session__session_date'],
            'total_students': total,
            'present_students': present,
            'absent_students': absent,
            'attendance_percentage': round(percentage, 2)
        })
    
    serializer = AttendanceSummarySerializer(summary_data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_attendance(request, student_id=None):
    # If no student_id provided, use current user
    if not student_id:
        if request.user.role != 'student':
            return Response({'error': 'Student ID required'}, status=status.HTTP_400_BAD_REQUEST)
        student = request.user
        student_id = student.id
    else:
        # Check permissions
        if request.user.role == 'student' and request.user.id != int(student_id):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'teacher':
            # Teacher can only see attendance for students in their classes
            try:
                student = User.objects.get(id=student_id, role='student')
                # Check if student is in any of the teacher's classes
                teacher_classes = Class.objects.filter(teacher=request.user)
                student_in_teacher_class = False
                for class_obj in teacher_classes:
                    if student in class_obj.students.all():
                        student_in_teacher_class = True
                        break
                if not student_in_teacher_class:
                    return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
            except User.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        elif request.user.role == 'admin':
            try:
                student = User.objects.get(id=student_id, role='student')
            except User.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Invalid user role'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get student's attendance records grouped by class
    records = AttendanceRecord.objects.filter(student=student).select_related(
        'session__class_obj'
    ).order_by('session__class_obj__course_name', 'session__session_date')
    
    # Group by class and calculate statistics
    class_attendance = {}
    for record in records:
        class_id = record.session.class_obj.id
        if class_id not in class_attendance:
            class_attendance[class_id] = {
                'class_name': record.session.class_obj.course_name,
                'total_classes': 0,
                'present_classes': 0,
                'absent_classes': 0
            }
        class_attendance[class_id]['total_classes'] += 1
        if record.is_present:
            class_attendance[class_id]['present_classes'] += 1
        else:
            class_attendance[class_id]['absent_classes'] += 1
    
    # Calculate percentages
    attendance_data = []
    for class_id, data in class_attendance.items():
        total = data['total_classes']
        present = data['present_classes']
        percentage = (present / total * 100) if total > 0 else 0
        
        attendance_data.append({
            'student_id': student.id,
            'student_name': student.get_full_name(),
            'class_name': data['class_name'],
            'total_classes': total,
            'present_classes': present,
            'absent_classes': data['absent_classes'],
            'attendance_percentage': round(percentage, 2)
        })
    
    serializer = StudentAttendanceSerializer(attendance_data, many=True)
    return Response(serializer.data)