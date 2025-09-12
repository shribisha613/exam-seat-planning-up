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
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Student
from .serializers import StudentSerializer
from .models import Faculty, Year, Class, Section, Student, Exam, SeatAssignment
from .serializers import (
    FacultySerializer, YearSerializer, ClassSerializer, 
    SectionSerializer, StudentSerializer, ExamSerializer, 
    SeatAssignmentSerializer, ExcelUploadSerializer
)

# --- NO CHANGES TO ANY OF THESE VIEWSETS ---
class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer    

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

class YearViewSet(viewsets.ModelViewSet):
    queryset = Year.objects.all()
    serializer_class = YearSerializer
class ClassViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Class.
    This version correctly defines a base queryset for the router AND
    manually applies filters for the list view.
    """
    # --- THE FIX: We must define a base queryset for the router ---
    # This is the "default" set of data for the viewset.
    queryset = Class.objects.all() 
    
    # The serializer class is correct.
    serializer_class = ClassSerializer

    def get_queryset(self):
        """
        This method is called to get the list of objects for the 'list' action.
        It starts with the original queryset and then applies our dynamic filters.
        """
        # Start with the base queryset defined above.
        queryset = super().get_queryset().distinct()

        # Look for 'faculty' in the URL parameters.
        faculty_id = self.request.query_params.get('faculty', None)
        if faculty_id is not None:
            queryset = queryset.filter(faculty__id=faculty_id)

        # Look for 'year' in the URL parameters.
        year_id = self.request.query_params.get('year', None)
        if year_id is not None:
            queryset = queryset.filter(year__id=year_id)
            
        return queryset

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_fields = ['class_name', 'year', 'faculty']

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_fields = ['section', 'class_name', 'year', 'faculty']

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class SeatAssignmentViewSet(viewsets.ModelViewSet):
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer
    filter_fields = ['exam', 'student']

# --- THIS IS THE ONLY SECTION THAT HAS BEEN MODIFIED ---
class ExcelUploadView(APIView):
    """
    Handles the bulk import of student data from a multi-sheet Excel file.
    """
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = ExcelUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        
        try:
            # Use pandas ExcelFile to get access to all sheets
            xls = pd.ExcelFile(file)
            total_students_created = 0

            # --- NEW: Loop through each sheet in the uploaded Excel file ---
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                df = df.where(pd.notnull(df), None)
                df.columns = df.columns.str.strip()

                # Basic validation to ensure the sheet has student data
                required_columns = ['University ID', 'Student Name', 'Group', 'Course']
                if not all(col in df.columns for col in required_columns):
                    # If a sheet doesn't have these columns, skip it (e.g., an info sheet)
                    continue

                # Determine the Year for all students in this sheet from the sheet's name
                try:
                    # Extracts the number from a sheet name like "Year 1", "Year 2", etc.
                    year_value = int(sheet_name.split(' ')[-1])
                    year_obj, _ = Year.objects.get_or_create(year_value=year_value)
                except (ValueError, IndexError):
                    # If the sheet name is not in the format "Year X", we can't process it.
                    # We could return an error or just skip it. Let's skip.
                    continue

                students_to_create_in_sheet = []
                for _, row in df.iterrows():
                    roll_no = str(row['University ID'])
                    
                    if Student.objects.filter(roll_no=roll_no).exists():
                        continue
                    
                    # Look up or create the foreign key objects
                    faculty_obj, _ = Faculty.objects.get_or_create(name=row['Course'])
                    
                    # A Class is unique by its name, faculty, and year
                      # A Class is unique by its name, faculty, AND year. All must be in the main query.
                    class_obj, _ = Class.objects.get_or_create(
                        name=row['Group'],
                        faculty=faculty_obj,
                        year=year_obj
                    )
                    
                    # --- MODIFIED: The same fix applies to Section ---
                    section_obj, _ = Section.objects.get_or_create(
                        name='A', # Using 'A' as a default section
                        class_name=class_obj,
                        faculty=faculty_obj,
                        year=year_obj
                    )

                    students_to_create_in_sheet.append(
                        Student(
                            name=row['Student Name'],
                            roll_no=roll_no,
                            faculty=faculty_obj,
                            year=year_obj,
                            class_name=class_obj,
                            section=section_obj
                        )
                    )
                
                Student.objects.bulk_create(students_to_create_in_sheet)
                total_students_created += len(students_to_create_in_sheet)

            return Response(
                {"message": f"Successfully imported {total_students_created} new students from {len(xls.sheet_names)} sheets."},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# --- NO CHANGES TO ANY OF THESE VIEWS ---
class SeatAssignmentGenerator(APIView):
    """Generates random seat assignments for exams"""
    
    def post(self, request, exam_id, *args, **kwargs):
        try:
            exam = Exam.objects.get(id=exam_id)
            rooms = request.data.get('rooms', {})
            
            if not rooms:
                return Response({"error": "No rooms provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            students = list(Student.objects.all())
            random.shuffle(students)
            
            assignments = []
            student_iterator = iter(students)
            
            with transaction.atomic():
                # Clear previous assignments for this exam to allow re-generation
                SeatAssignment.objects.filter(exam=exam).delete()
                
                for room, capacity in rooms.items():
                    for seat in range(1, capacity + 1):
                        try:
                            student = next(student_iterator)
                            assignments.append(SeatAssignment(
                                student=student,
                                exam=exam,
                                room_number=room,
                                seat_number=str(seat)
                            ))
                        except StopIteration:
                            break
                    else:
                        continue
                    break
            
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
            assignments = SeatAssignment.objects.filter(exam=exam).select_related(
                'student', 'student__section', 'student__class_name', 
                'student__year', 'student__faculty'
            )
            
            if not assignments.exists():
                return Response({"message": "No seat assignments found for this exam."}, status=status.HTTP_404_NOT_FOUND)

            data = [{
                'Exam Name': exam.name,
                'Exam Date': exam.date,
                'Room Number': a.room_number,
                'Seat Number': a.seat_number,
                'Student Name': a.student.name,
                'Roll No': a.student.roll_no,
                'Section': a.student.section.name,
                'Class': a.student.class_name.name,
                'Year': a.student.year.year_value,
                'Faculty': a.student.faculty.name
            } for a in assignments]
            
            df = pd.DataFrame(data)
            
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="seat_assignments_{exam.name}.xlsx"'
            
            df.to_excel(response, index=False, sheet_name='Seat Assignments')
            
            return response
        
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)