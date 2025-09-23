from rest_framework import serializers
from .models import Faculty, Year, Class, Section, Student, Exam, SeatAssignment, Room, Seat

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'

class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    # This defines the new field that will be added to the API response.
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        # We explicitly list the fields to include our new custom field.
        fields = ['id', 'name', 'year', 'faculty', 'student_count']

    def get_student_count(self, obj):
        """
        This method is automatically called by the serializer for each Class object.
        'obj' is the instance of the Class model.
        It counts how many Student records are linked to this specific class.
        """
        return Student.objects.filter(class_name=obj).count()

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    # These lines will replace the IDs with the string representation
    # (the __str__ method) of the related models.
    section = serializers.StringRelatedField(read_only=True)
    class_name = serializers.StringRelatedField(read_only=True)
    year = serializers.StringRelatedField(read_only=True)
    faculty = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        # Explicitly list the fields to control the output
        fields = ['id', 'name', 'roll_no', 'section', 'class_name', 'year', 'faculty']

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'



class ExcelUploadSerializer(serializers.Serializer):
    """Serializer for Excel file upload"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.xlsx'):
            raise serializers.ValidationError("Only Excel (.xlsx) files are allowed")
        return value

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        # We only need to send these fields to the frontend for the selection screen
        fields = ['id', 'name', 'capacity', 'building']


class SeatSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'room'] 

class SeatAssignmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    seat = SeatSerializer(read_only=True)
    
    class Meta:
        model = SeatAssignment
        fields = ['id', 'student', 'exam', 'seat']     