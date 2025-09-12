from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet,SeatViewSet

router = DefaultRouter()
router.register(r'rooms',RoomViewSet)
router.register(r'seats',SeatViewSet)

urlpatterns = [
    path('',include(router.urls)),
    
]