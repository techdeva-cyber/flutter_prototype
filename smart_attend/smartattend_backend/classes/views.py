from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Class, ClassSchedule
from .serializers import ClassSerializer, ClassCreateSerializer, ClassEnrollmentSerializer
from accounts.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_classes(request):
    # Admin can see all classes
    # Teacher can see their classes
    # Student can see their enrolled classes
    if request.user.role == 'admin':
        classes = Class.objects.all()
    elif request.user.role == 'teacher':
        classes = Class.objects.filter(teacher=request.user)
    elif request.user.role == 'student':
        classes = request.user.enrolled_classes.all()
    else:
        return Response({'error': 'Invalid user role'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_class(request):
    if request.user.role != 'admin':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ClassCreateSerializer(data=request.data)
    if serializer.is_valid():
        class_obj = serializer.save()
        return Response(ClassSerializer(class_obj).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_class_detail(request, class_id):
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if request.user.role == 'student' and request.user not in class_obj.students.all():
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'teacher' and class_obj.teacher != request.user:
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ClassSerializer(class_obj)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_class(request, class_id):
    if request.user.role != 'admin':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ClassCreateSerializer(class_obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ClassSerializer(class_obj).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_class(request, class_id):
    if request.user.role != 'admin':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    class_obj.delete()
    return Response({'message': 'Class deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_students(request, class_id):
    if request.user.role != 'admin':
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ClassEnrollmentSerializer(class_obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Students enrolled successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_classes(request, teacher_id):
    if request.user.role != 'admin' and request.user.id != int(teacher_id):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        teacher = User.objects.get(id=teacher_id, role='teacher')
    except User.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
    
    classes = Class.objects.filter(teacher=teacher)
    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_classes(request, student_id):
    if request.user.role != 'admin' and request.user.id != int(student_id):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = User.objects.get(id=student_id, role='student')
    except User.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    classes = student.enrolled_classes.all()
    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)