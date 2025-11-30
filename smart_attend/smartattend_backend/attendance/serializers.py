from rest_framework import serializers
from .models import AttendanceSession, AttendanceRecord, QRCode
from classes.models import Class
from accounts.models import User


class AttendanceSessionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.course_name', read_only=True)
    total_students = serializers.SerializerMethodField()
    present_students = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = ('id', 'class_obj', 'class_name', 'session_date', 'start_time', 'end_time', 
                  'is_active', 'created_at', 'total_students', 'present_students')
        read_only_fields = ('id', 'class_name', 'created_at', 'total_students', 'present_students')

    def get_total_students(self, obj):
        return obj.class_obj.students.count()

    def get_present_students(self, obj):
        return obj.records.filter(is_present=True).count()


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    class_name = serializers.CharField(source='session.class_obj.course_name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ('id', 'session', 'student', 'student_name', 'class_name', 'is_present', 
                  'method', 'recorded_by', 'recorded_at', 'latitude', 'longitude', 'altitude')
        read_only_fields = ('id', 'student_name', 'class_name', 'recorded_at')

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


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ('id', 'session', 'code', 'created_at', 'expires_at', 'is_active')
        read_only_fields = ('id', 'code', 'created_at')


class AttendanceSummarySerializer(serializers.Serializer):
    date = serializers.DateField()
    total_students = serializers.IntegerField()
    present_students = serializers.IntegerField()
    absent_students = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class StudentAttendanceSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    total_classes = serializers.IntegerField()
    present_classes = serializers.IntegerField()
    absent_classes = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)