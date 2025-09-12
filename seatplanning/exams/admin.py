from django.contrib import admin

# Register your models here.

from .models import Faculty
from .models import Year
from .models import Class
from .models import Section
from .models import Exam
from .models import SeatAssignment
from .models import Student


 # Make sure to import your Faculty model
admin.site.register(Faculty)
admin.site.register(Year)
admin.site.register(Class)
admin.site.register(Section)
admin.site.register(Student)
admin.site.register(Exam)
admin.site.register(SeatAssignment)

# This line registers the Faculty model with the admin site
