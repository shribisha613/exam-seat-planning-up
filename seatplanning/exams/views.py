from django.shortcuts import render
import pandas as pd
import random
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.http import HttpResponse
from rest_framework import generics
from .models import Student
from .serializers import StudentSerializer
from .models import Faculty, Year, Class, Section, Student, Exam, SeatAssignment
from .serializers import (
    FacultySerializer, YearSerializer, ClassSerializer, 
    SectionSerializer, StudentSerializer, ExamSerializer, 
    SeatAssignmentSerializer, ExcelUploadSerializer
)

class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer    

class FacultyViewSet(viewsets.ModelViewSet):
    """CRUD operations for Faculty"""
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

class YearViewSet(viewsets.ModelViewSet):
    """CRUD operations for Year"""
    queryset = Year.objects.all()
    serializer_class = YearSerializer

class ClassViewSet(viewsets.ModelViewSet):
    """CRUD operations for Class"""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_fields = ['faculty', 'year']

class SectionViewSet(viewsets.ModelViewSet):
    """CRUD operations for Section"""
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_fields = ['class_name', 'year', 'faculty']

class StudentViewSet(viewsets.ModelViewSet):
    """CRUD operations for Student"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_fields = ['section', 'class_name', 'year', 'faculty']

class ExamViewSet(viewsets.ModelViewSet):
    """CRUD operations for Exam"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class SeatAssignmentViewSet(viewsets.ModelViewSet):
    """CRUD operations for SeatAssignment"""
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer
    filter_fields = ['exam', 'student']

class ExcelUploadView(APIView):
    """Handles Excel file upload and processing"""
    
    def post(self, request, *args, **kwargs):
        serializer = ExcelUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        
        try:
            # Read Excel file
            xls = pd.ExcelFile(file)
            
            with transaction.atomic():
                # Process each sheet
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    
                    # Convert NaN to None for proper NULL handling in database
                    df = df.where(pd.notnull(df), None)
                    
                    # Process based on sheet name
                    if sheet_name.lower() == 'faculty':
                        self.process_faculty(df)
                    elif sheet_name.lower() == 'year':
                        self.process_year(df)
                    elif sheet_name.lower() == 'class':
                        self.process_class(df)
                    elif sheet_name.lower() == 'section':
                        self.process_section(df)
                    elif sheet_name.lower() == 'student':
                        self.process_student(df)
                    elif sheet_name.lower() == 'exam':
                        self.process_exam(df)
            
            return Response({"message": "Data imported successfully"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def process_faculty(self, df):
        """Process faculty data from Excel"""
        for _, row in df.iterrows():
            Faculty.objects.update_or_create(
                id=row.get('id'),
                defaults={'name': row['name']}
            )
    
    def process_year(self, df):
        """Process year data from Excel"""
        for _, row in df.iterrows():
            Year.objects.update_or_create(
                id=row.get('id'),
                defaults={'year_value': row['year_value']}
            )
    
    def process_class(self, df):
        """Process class data from Excel"""
        for _, row in df.iterrows():
            faculty = Faculty.objects.get(id=row['faculty_id'])
            year = Year.objects.get(id=row['year_id'])
            
            Class.objects.update_or_create(
                id=row.get('id'),
                defaults={
                    'name': row['name'],
                    'faculty': faculty,
                    'year': year
                }
            )
    
    def process_section(self, df):
        """Process section data from Excel"""
        for _, row in df.iterrows():
            class_name = Class.objects.get(id=row['class_name_id'])
            year = Year.objects.get(id=row['year_id'])
            faculty = Faculty.objects.get(id=row['faculty_id'])
            
            Section.objects.update_or_create(
                id=row.get('id'),
                defaults={
                    'name': row['name'],
                    'class_name': class_name,
                    'year': year,
                    'faculty': faculty
                }
            )
    
    def process_student(self, df):
        """Process student data from Excel"""
        for _, row in df.iterrows():
            section = Section.objects.get(id=row['section_id'])
            class_name = Class.objects.get(id=row['class_name_id'])
            year = Year.objects.get(id=row['year_id'])
            faculty = Faculty.objects.get(id=row['faculty_id'])
            
            Student.objects.update_or_create(
                roll_no=row['roll_no'],
                defaults={
                    'name': row['name'],
                    'section': section,
                    'class_name': class_name,
                    'year': year,
                    'faculty': faculty
                }
            )
    
    def process_exam(self, df):
        """Process exam data from Excel"""
        for _, row in df.iterrows():
            Exam.objects.update_or_create(
                id=row.get('id'),
                defaults={
                    'name': row['name'],
                    'date': row['date'],
                    'start_time': row['start_time'],
                    'end_time': row['end_time']
                }
            )

class SeatAssignmentGenerator(APIView):
    """Generates random seat assignments for exams"""
    
    def post(self, request, exam_id, *args, **kwargs):
        try:
            exam = Exam.objects.get(id=exam_id)
            rooms = request.data.get('rooms', {})  # Format: {"Room1": 30, "Room2": 40}
            
            if not rooms:
                return Response({"error": "No rooms provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get all students
            students = list(Student.objects.all())
            
            # Shuffle students to randomize
            random.shuffle(students)
            
            # Generate seat assignments
            assignments = []
            current_seat = 0
            current_room = None
            seats_per_room = 0
            
            for room, capacity in rooms.items():
                for seat in range(1, capacity + 1):
                    if current_seat >= len(students):
                        break
                    
                    student = students[current_seat]
                    
                    # Check if student is already assigned to this exam
                    if SeatAssignment.objects.filter(student=student, exam=exam).exists():
                        current_seat += 1
                        continue
                    
                    # Create assignment

                    assignment = SeatAssignment(
                    student=student,
                    exam=exam,
                    room_number=room,
                    seat_number=str(seat)
            )
                    # It needed to create instance of seat assignment in this part
                    # assignment = SeatAssignment
                    # student=student,
                    # exam=exam,
                    # room_number=room,
                    # seat_number=str(seat)
                    assignments.append(assignment)
                    current_seat += 1
            
            # Bulk create assignments
            SeatAssignment.objects.bulk_create(assignments)
            
            return Response({"message": f"Assigned {len(assignments)} students"}, status=status.HTTP_201_CREATED)
        
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ExportSeatAssignments(APIView):
    """Exports seat assignments to Excel"""
    
    def get(self, request, exam_id, *args, **kwargs):
        try:
            exam = Exam.objects.get(id=exam_id)
            assignments = SeatAssignment.objects.filter(exam=exam).select_related('student')
            
            # Prepare data for Excel
            data = []
            for assignment in assignments:
                student = assignment.student
                data.append({
                    'Exam Name': exam.name,
                    'Exam Date': exam.date,
                    'Room Number': assignment.room_number,
                    'Seat Number': assignment.seat_number,
                    'Student Name': student.name,
                    'Roll No': student.roll_no,
                    'Section': student.section.name,
                    'Class': student.class_name.name,
                    'Year': student.year.year_value,
                    'Faculty': student.faculty.name
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Create HTTP response with Excel file
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = f'attachment; filename="seat_assignments_{exam.name}.xlsx"'
            
            # Write DataFrame to Excel
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Seat Assignments')
            
            return response
        
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
