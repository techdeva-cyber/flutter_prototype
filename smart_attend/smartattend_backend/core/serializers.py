from rest_framework import serializers
from .models import LocationVerification, FacialRecognitionData, AttendanceAnalytics, Notification
from classes.models import Class
from accounts.models import User


class LocationVerificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.course_name', read_only=True)

    class Meta:
        model = LocationVerification
        fields = ('id', 'user', 'user_name', 'class_obj', 'class_name', 'latitude', 
                  'longitude', 'altitude', 'verified_at', 'is_verified')
        read_only_fields = ('id', 'user_name', 'class_name', 'verified_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert Decimal fields to float for JSON serialization
        if data['latitude']:
            data['latitude'] = float(data['latitude'])
        if data['longitude']:
            data['longitude'] = float(data['longitude'])
        if data['altitude']:
            data['altitude'] = float(data['altitude'])
        return data


class FacialRecognitionDataSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = FacialRecognitionData
        fields = ('id', 'user', 'user_name', 'facial_encoding', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user_name', 'created_at', 'updated_at')


class AttendanceAnalyticsSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.course_name', read_only=True)

    class Meta:
        model = AttendanceAnalytics
        fields = ('id', 'class_obj', 'class_name', 'total_sessions', 'total_attendance', 
                  'average_attendance', 'last_updated')
        read_only_fields = ('id', 'class_name', 'last_updated')


class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'user', 'user_name', 'title', 'message', 'notification_type', 
                  'is_read', 'created_at')
        read_only_fields = ('id', 'user_name', 'created_at')