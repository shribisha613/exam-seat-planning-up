from django.db import models

class Room(models.Model):
    room_id = models.AutoField(primary_key=True,unique=True)
    room_name = models.CharField(max_length=20)
    max_rows = models.IntegerField()
    max_columns = models.IntegerField()
    capacity = models.IntegerField()

    
    def __str__(self):
        return self.room_name

class Seat(models.Model):
    room = models.ForeignKey(Room,related_name='seats', on_delete=models.CASCADE)  #Here this will create a another table for seats and FK the Room 
    seat_id = models.CharField(primary_key=True,unique=True,max_length=10)
    row = models.IntegerField()
    column = models.IntegerField()
    
    def __str__ (self):
        return f"Seat {self.seat_number} in {self.room.room_name}"
    
    