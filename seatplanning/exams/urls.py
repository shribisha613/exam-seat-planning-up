from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    FacultyViewSet, YearViewSet, ClassViewSet, SectionViewSet,
    StudentViewSet, ExamViewSet, SeatAssignmentViewSet,
    ExcelUploadView, SeatAssignmentGenerator, ExportSeatAssignments
)

router = DefaultRouter()
router.register(r'faculties', FacultyViewSet)
router.register(r'years', YearViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'students', StudentViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'seat-assignments', SeatAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload-excel/', ExcelUploadView.as_view(), name='excel-upload'),
    path('exams/<int:exam_id>/generate-seats/', SeatAssignmentGenerator.as_view(), name='generate-seats'),
    path('exams/<int:exam_id>/export-seats/', ExportSeatAssignments.as_view(), name='export-seats'),  
]