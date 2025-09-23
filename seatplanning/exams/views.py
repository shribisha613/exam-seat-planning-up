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
from .models import Faculty, Year, Class, Section, Student, Exam, SeatAssignment, Room, Seat
from .serializers import (
    FacultySerializer, YearSerializer, ClassSerializer, 
    SectionSerializer, StudentSerializer, ExamSerializer, 
    SeatAssignmentSerializer, ExcelUploadSerializer, RoomSerializer, SeatSerializer
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
    """
    Generates random seat assignments by filling the available seats
    from the selected rooms with the students for the exam.
    """
    @transaction.atomic
    def post(self, request, exam_id, *args, **kwargs):
        try:
            exam = Exam.objects.get(id=exam_id)
            
            # --- Get data from the React frontend's payload ---
            room_ids = request.data.get('room_ids', [])
            section_ids = request.data.get('section_ids', []) # Get the section IDs

            # --- Validation ---
            if not room_ids:
                return Response({"error": "No room IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
            if not section_ids:
                return Response({"error": "No section IDs provided to select students."}, status=status.HTTP_400_BAD_REQUEST)

            # --- THE FIX: Replace the placeholder with this logic ---
            # Filter the Student model to get only the students from the selected sections.
            students_to_assign = list(Student.objects.filter(section__id__in=section_ids))
            
            # Now, shuffle the CORRECT list of students
            random.shuffle(students_to_assign)
            
            # --- The rest of your logic remains the same ---
            
            # Get all available seats from the selected rooms, ordered consistently
            available_seats = list(Seat.objects.filter(room__id__in=room_ids).order_by('room__name', 'row_num', 'col_num'))
            
            if len(available_seats) < len(students_to_assign):
                return Response({
                    "error": f"Insufficient capacity. {len(students_to_assign)} students require seating, but only {len(available_seats)} seats are available in the selected rooms."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Clear any previous assignments for this exam
            SeatAssignment.objects.filter(exam=exam).delete()
            
            assignments_to_create = []
            for i, student in enumerate(students_to_assign):
                seat_to_assign = available_seats[i]
                assignments_to_create.append(SeatAssignment(
                    student=student,
                    exam=exam,
                    seat=seat_to_assign
                ))
            
            SeatAssignment.objects.bulk_create(assignments_to_create)
            
            return Response(
                {"message": f"Successfully assigned {len(assignments_to_create)} students to seats."},
                status=status.HTTP_201_CREATED
            )
        
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExportSeatAssignments(APIView):
    """Exports seat assignments to a comprehensive Excel file."""
    
    def get(self, request, exam_id, *args, **kwargs):
        try:
            exam = Exam.objects.get(id=exam_id)
            
            # This is an optimized query to fetch all related data efficiently.
            assignments = SeatAssignment.objects.filter(exam=exam).select_related(
                'student', 'student__section', 'student__class_name', 
                'student__year', 'student__faculty',
                'seat', 'seat__room'  # <-- Fetches seat and room data
            )
            
            if not assignments.exists():
                return Response({"message": "No seat assignments found for this exam."}, status=status.HTTP_404_NOT_FOUND)

            # --- THE FIX IS HERE ---
            # We access the data by following the relationships: a.seat.room.name
            data = [{
                'Exam Name': exam.name,
                'Exam Date': exam.date,
                'Building': a.seat.room.building,
                'Room Name': a.seat.room.name,      # Correct: a -> seat -> room -> name
                'Seat Number': a.seat.seat_number,    # Correct: a -> seat -> seat_number
                'Student Name': a.student.name,
                'Roll No': a.student.roll_no,
                'Section': str(a.student.section),
                'Class': str(a.student.class_name),
                'Year': str(a.student.year),
                'Faculty': str(a.student.faculty)
            } for a in assignments]
            
            df = pd.DataFrame(data)
            
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="seat_assignments_{exam.name}.xlsx"'
            
            # This logic creates a separate, sorted sheet for each room
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                room_names = sorted(df['Room Name'].unique())
                for room_name in room_names:
                    room_df = df[df['Room Name'] == room_name].copy()
                    room_df.sort_values(by='Seat Number', inplace=True)
                    room_df.to_excel(writer, index=False, sheet_name=room_name)
            
            return response
        
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing and managing Rooms.
    """
    # This queryset ensures the API only returns rooms that are marked as available for use.
    queryset = Room.objects.filter(is_available=True)
    serializer_class = RoomSerializer