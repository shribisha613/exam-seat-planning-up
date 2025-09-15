from rest_framework import serializers
from .models import Room,Seat

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        field = ['seat_id','row','column']
        
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        field = ['room_id','room_name','max_rows','max_columns','capacity','seats']
        
         