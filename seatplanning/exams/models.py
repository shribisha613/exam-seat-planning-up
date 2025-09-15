from django.db import models

class Faculty(models.Model):
    """Represents a faculty/department in the university"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Year(models.Model):
    """Academic year (e.g., 2023, 2024)"""
    year_value = models.IntegerField(unique=True)
    
    def __str__(self):
        return str(self.year_value)

class Class(models.Model):
    """Represents a class (e.g., CS101, MATH201)"""
    name = models.CharField(max_length=100)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('name', 'year', 'faculty')
    
    def __str__(self):
        return f"{self.name} - {self.faculty} ({self.year})"

class Section(models.Model):
    """Represents a section within a class (e.g., Section A, Section B)"""
    name = models.CharField(max_length=10)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('name', 'class_name', 'year', 'faculty')
    
    def __str__(self):
        return f"{self.class_name} - {self.name}"

class Student(models.Model):
    """Student information model"""
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} ({self.roll_no})"

class Exam(models.Model):
    """Exam information model"""
    name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"{self.name} on {self.date}"
    


class Room(models.Model):
    """Represents an examination room with a layout template."""
    name = models.CharField(max_length=100, unique=True)
    building = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0, editable=False, help_text="Calculated automatically from template seats.")
    max_rows = models.IntegerField(default=0, editable=False)
    max_columns = models.IntegerField(default=0, editable=False)
    is_available = models.BooleanField(default=True)
    template_file = models.FileField(upload_to='room_templates/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.building})"

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically parse the template
        and populate the Seat table after the file is saved.
        """
        # Save the model instance first to ensure it has an ID and the file is on disk
        super().save(*args, **kwargs)
        
        # If a template file was just uploaded, parse it.
        if self.template_file:
            # Import locally to avoid circular import issues
            from .utils import parse_room_template_and_create_seats
            parse_room_template_and_create_seats(self)

class Seat(models.Model):
    """Represents a single, specific seat within a room."""
    room = models.ForeignKey(Room, related_name='seats', on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=20) # e.g., "A-01", "B-15"
    row_num = models.IntegerField()
    col_num = models.IntegerField()
    
    class Meta:
        # A seat number should be unique within a given room
        unique_together = ('room', 'seat_number')

    def __str__(self):
        return f"Seat {self.seat_number} in {self.room.name}"

class SeatAssignment(models.Model):
    """
    MODIFIED: This model now links a Student to a specific Seat for an Exam.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    # The new, correct way: a direct link to the Seat object.
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    
    # The old fields are no longer needed, as this info is in the Seat model.
    # room_number = models.CharField(max_length=20)
    # seat_number = models.CharField(max_length=20)
    
    class Meta:
        # A seat can only be assigned to one student per exam.
        unique_together = ('exam', 'seat')
    
    def __str__(self):
        # Updated to reflect the new structure
        return f"{self.student} at {self.seat} for {self.exam}"

