from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import LocationVerification, FacialRecognitionData, AttendanceAnalytics, Notification
from .serializers import (
    LocationVerificationSerializer, FacialRecognitionDataSerializer, 
    AttendanceAnalyticsSerializer, NotificationSerializer
)
from classes.models import Class
import json
import math


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_location(request):
    """
    Verify student's location against class location
    """
    if request.user.role != 'student':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    class_id = request.data.get('class_id')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    altitude = request.data.get('altitude')
    
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if student is enrolled in the class
    if request.user not in class_obj.students.all():
        return Response({'error': 'You are not enrolled in this class'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate distance between student and class location
    distance = calculate_distance(
        float(latitude), float(longitude),
        float(class_obj.latitude), float(class_obj.longitude)
    )
    
    # Consider location verified if within 100 meters
    is_verified = distance <= 100
    
    # Create location verification record
    verification = LocationVerification.objects.create(
        user=request.user,
        class_obj=class_obj,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        is_verified=is_verified
    )
    
    serializer = LocationVerificationSerializer(verification)
    return Response(serializer.data)


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r * 1000  # Return distance in meters


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_facial_data(request):
    """
    Save facial recognition data for a user
    """
    facial_encoding = request.data.get('facial_encoding')
    
    if not facial_encoding:
        return Response({'error': 'Facial encoding required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Save or update facial data
    facial_data, created = FacialRecognitionData.objects.update_or_create(
        user=request.user,
        defaults={
            'facial_encoding': json.dumps(facial_encoding)
        }
    )
    
    serializer = FacialRecognitionDataSerializer(facial_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_facial_data(request):
    """
    Verify facial data for attendance
    """
    if request.user.role != 'student':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    class_id = request.data.get('class_id')
    facial_encoding = request.data.get('facial_encoding')
    
    if not facial_encoding:
        return Response({'error': 'Facial encoding required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if student is enrolled in the class
    if request.user not in class_obj.students.all():
        return Response({'error': 'You are not enrolled in this class'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get stored facial data
    try:
        stored_data = FacialRecognitionData.objects.get(user=request.user)
        stored_encoding = json.loads(stored_data.facial_encoding)
    except FacialRecognitionData.DoesNotExist:
        return Response({'error': 'No facial data found for user'}, status=status.HTTP_404_NOT_FOUND)
    
    # Compare facial encodings (simplified comparison)
    # In a real implementation, you would use a proper facial recognition library
    similarity = compare_facial_encodings(facial_encoding, stored_encoding)
    
    # Consider verified if similarity is above threshold
    is_verified = similarity > 0.6
    
    return Response({
        'verified': is_verified,
        'similarity': similarity
    })


def compare_facial_encodings(encoding1, encoding2):
    """
    Compare two facial encodings and return similarity score
    This is a simplified implementation - in practice, you would use
    a proper facial recognition library like face_recognition
    """
    # Calculate Euclidean distance between encodings
    if len(encoding1) != len(encoding2):
        return 0.0
    
    sum_squared_diff = sum((a - b) ** 2 for a, b in zip(encoding1, encoding2))
    distance = math.sqrt(sum_squared_diff)
    
    # Convert distance to similarity (0-1 scale)
    # This is a simplified conversion - adjust as needed
    similarity = max(0, 1 - distance / 2)
    return similarity


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """
    Get user notifications
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    notification.is_read = True
    notification.save()
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics(request, class_id):
    """
    Get attendance analytics for a class
    """
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if request.user.role == 'student' and request.user not in class_obj.students.all():
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'teacher' and class_obj.teacher != request.user:
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get or create analytics record
    analytics, created = AttendanceAnalytics.objects.get_or_create(class_obj=class_obj)
    
    serializer = AttendanceAnalyticsSerializer(analytics)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_analytics(request, class_id):
    """
    Update attendance analytics for a class
    """
    if request.user.role != 'teacher':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        class_obj = Class.objects.get(id=class_id, teacher=request.user)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create analytics record
    analytics, created = AttendanceAnalytics.objects.get_or_create(class_obj=class_obj)
    
    # Update analytics (this would typically be done automatically)
    # For now, we'll just update the last_updated field
    analytics.save()
    
    serializer = AttendanceAnalyticsSerializer(analytics)
    return Response(serializer.data)