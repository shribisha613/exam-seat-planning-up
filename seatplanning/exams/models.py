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

class SeatAssignment(models.Model):
    """Seat assignment for students during exams"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20)
    seat_number = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ('exam', 'room_number', 'seat_number')
    
    def __str__(self):
        return f"{self.student} in {self.room_number}-{self.seat_number} for {self.exam}"
# Create your models here.
