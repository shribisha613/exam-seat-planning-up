import pandas as pd
from .models import Seat

def parse_room_template_and_create_seats(room_instance):
    """
    Reads an Excel template file, parses the seat layout,
    and creates/updates the Seat objects for the given Room.
    """
    if not room_instance.template_file:
        print(f"No template file for room: {room_instance.name}")
        return

    try:
        # Clear any existing seats for this room to ensure a fresh import
        room_instance.seats.all().delete()

        # Use pandas to read the specific sheet; openpyxl is used under the hood
        # We assume the layout is on the first sheet of the Excel file
        df = pd.read_excel(room_instance.template_file.path, header=None)
        
        seats_to_create = []
        max_row, max_col = 0, 0

        # Iterate through each cell of the DataFrame
        for r_idx, row_series in df.iterrows():
            for c_idx, cell_value in enumerate(row_series):
                # Check if the cell is not empty and looks like a seat number (contains a '-')
                if pd.notna(cell_value) and isinstance(cell_value, str) and '-' in cell_value:
                    seat_number = cell_value.strip()
                    # r_idx and c_idx are 0-based, so add 1 for human-readable row/col numbers
                    row_num = r_idx + 1
                    col_num = c_idx + 1
                    
                    seats_to_create.append(
                        Seat(
                            room=room_instance,
                            seat_number=seat_number,
                            row_num=row_num,
                            col_num=col_num
                        )
                    )
                    
                    if row_num > max_row: max_row = row_num
                    if col_num > max_col: max_col = col_num

        # Create all seats in a single, efficient database query
        Seat.objects.bulk_create(seats_to_create)
        
        # Update the parent Room's calculated fields and save it
        room_instance.capacity = len(seats_to_create)
        room_instance.max_rows = max_row
        room_instance.max_columns = max_col
        # We need to save without triggering this function again to avoid a loop
        # so we use ._base_manager.update() which bypasses the save() method
        type(room_instance)._base_manager.filter(pk=room_instance.pk).update(
            capacity=room_instance.capacity,
            max_rows=room_instance.max_rows,
            max_columns=room_instance.max_columns
        )
        print(f"Successfully parsed template for '{room_instance.name}'. Found {room_instance.capacity} seats.")

    except Exception as e:
        print(f"ERROR parsing template for room '{room_instance.name}': {e}")