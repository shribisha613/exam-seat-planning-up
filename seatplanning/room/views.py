from django.shortcuts import render
from rest_framework import viewsets
from .models import Room, Seat
from .serializers import RoomSerializer, SeatSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    

class RoomInfo(APIView):
    
    def get(self):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)