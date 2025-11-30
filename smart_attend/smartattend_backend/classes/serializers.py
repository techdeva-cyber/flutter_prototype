from rest_framework import serializers
from .models import Class, ClassSchedule
from accounts.models import User


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = ('id', 'weekday', 'start_time', 'end_time')


class ClassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    schedules = ClassScheduleSerializer(many=True, read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ('id', 'course_id', 'course_name', 'semester', 'section', 
                  'teacher', 'teacher_name', 'room_number', 'latitude', 'longitude', 
                  'altitude', 'start_time', 'end_time', 'students', 'schedules', 'student_count')
        read_only_fields = ('id', 'teacher_name', 'schedules', 'student_count')

    def get_student_count(self, obj):
        return obj.students.count()

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


class ClassCreateSerializer(serializers.ModelSerializer):
    schedules = ClassScheduleSerializer(many=True, required=False)

    class Meta:
        model = Class
        fields = ('id', 'course_id', 'course_name', 'semester', 'section', 
                  'teacher', 'room_number', 'latitude', 'longitude', 
                  'altitude', 'start_time', 'end_time', 'students', 'schedules')

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        students_data = validated_data.pop('students', [])
        
        class_obj = Class.objects.create(**validated_data)
        
        # Add students to the class
        for student in students_data:
            class_obj.students.add(student)
        
        # Create schedules
        for schedule_data in schedules_data:
            ClassSchedule.objects.create(class_obj=class_obj, **schedule_data)
            
        return class_obj

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        students_data = validated_data.pop('students', None)
        
        # Update class fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update students if provided
        if students_data is not None:
            instance.students.set(students_data)
        
        # Update schedules
        if schedules_data:
            instance.schedules.all().delete()
            for schedule_data in schedules_data:
                ClassSchedule.objects.create(class_obj=instance, **schedule_data)
            
        return instance


class ClassEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'students')