# exams/management/commands/import_rooms.py

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from exams.models import Room, Seat

# --- THIS IS THE CONFIGURATION MAP ---
# This map is the single source of truth for which building a room belongs to.
# The KEY must exactly match the sheet name in your Excel file.
ROOM_TO_BUILDING_MAP = {
    # Nepal Block Rooms
    "Fewa": "Nepal Block",
    "Machhapuchre": "Nepal Block",
    "Nilgiri": "Nepal Block",
    "Tilicho": "Nepal Block",
    "Gokyo": "Nepal Block",
    "Begnas": "Nepal Block",
    "Rara": "Nepal Block",
    "Annapurna": "Nepal Block",
    
    # UK Block Rooms
    "Big Ben": "UK Block",
    "Open Access": "UK Block",
    "Stonehenge": "UK Block",
    "Kingstone": "UK Block",
    "Thames": "UK Block",
}

class Command(BaseCommand):
    help = 'Imports all rooms and seat layouts from a single master Excel file.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the master Excel file (e.g., "media/Seat Plan.xlsx").')

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options['file_path']
        self.stdout.write(self.style.SUCCESS(f"--- Starting Import from: {file_path} ---"))

        try:
            xls = pd.ExcelFile(file_path)
            
            self.stdout.write(self.style.WARNING("Clearing all existing Room and Seat data..."))
            Seat.objects.all().delete()
            Room.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing data cleared."))

            for sheet_name in xls.sheet_names:
                room_name = sheet_name.strip()

                # --- THE DEFINITIVE FIX IS HERE ---
                # Look up the building name from our map for EACH sheet.
                building_name = ROOM_TO_BUILDING_MAP.get(room_name)
                
                if not building_name:
                    self.stdout.write(self.style.WARNING(f"WARNING: Room '{room_name}' was found in Excel but is not in the ROOM_TO_BUILDING_MAP. Skipping this sheet."))
                    continue
                
                self.stdout.write(f"Processing room: '{room_name}' -> Assigning to building: '{building_name}'...")
                
                # Create the Room instance with the CORRECT building name from the map.
                room_instance = Room.objects.create(name=room_name, building=building_name)
                
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                
                seats_to_create = []
                for r_idx, row_series in df.iterrows():
                    for c_idx, cell_value in enumerate(row_series):
                        if pd.notna(cell_value) and isinstance(cell_value, str) and '-' in cell_value:
                            seats_to_create.append(Seat(
                                room=room_instance, seat_number=cell_value.strip(),
                                row_num=r_idx + 1, col_num=c_idx + 1
                            ))
                
                Seat.objects.bulk_create(seats_to_create)
                
                room_instance.capacity = len(seats_to_create)
                # We only need to update the capacity, so we can use a more efficient save.
                room_instance.save(update_fields=['capacity'])

                self.stdout.write(self.style.SUCCESS(f" -> Successfully created '{room_name}' with {room_instance.capacity} seats."))

            self.stdout.write(self.style.SUCCESS("\n--- Import process completed successfully! ---"))

        except FileNotFoundError:
            raise CommandError(f"ERROR: The file at '{file_path}' was not found.")
        except Exception as e:
            raise CommandError(f"An unexpected error occurred: {e}")