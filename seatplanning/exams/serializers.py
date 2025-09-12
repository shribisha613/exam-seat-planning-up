from rest_framework import serializers
from .models import Faculty, Year, Class, Section, Student, Exam, SeatAssignment

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
    class Meta:
        model = Student
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class SeatAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatAssignment
        fields = '__all__'

class ExcelUploadSerializer(serializers.Serializer):
    """Serializer for Excel file upload"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.xlsx'):
            raise serializers.ValidationError("Only Excel (.xlsx) files are allowed")
        return value