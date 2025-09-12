from django.test import TestCase
from .models import Room, Seat
import pandas as pd
import json



"""
Excel template reading, 
Json conversion, 
randomize, 
assign each seat with a student, 
use the json file for creatign a new Excel file, 
create a sand box, 
response the sand box link, 

"""

class ExcelTesting():
    def readExcel(self):
        # Providing a clear path to the excel file 
        file_path = r'D:\RTE_API\rte_api\media\Seat Plan.xlsx'
        # parcing the exce file 
        excel_data = pd.ExcelFile(file_path)
        # Creating a dict 
        seat_data = {}
        
        
        # Now looping the sheet pages 
        for sheet_name in excel_data.sheet_names:
            
            # Converting the excel file in dataframe 
            df = pd.read_excel(file_path,sheet_name=sheet_name)
            
            # Stripping the name of sheet 
            sheet_name = sheet_name.strip()
            
            # cerating a format for storing the data of the sheets 
            seat_data[sheet_name] = {
                
                # contains the location of the entrance 
                "entrance":[],
                "max_row":0,
                "max_col":0,
                # Info of steats 
                "seats":{}
            }
            
            # This will store the value in seats
            seat = seat_data[sheet_name]["seats"]
            x_val = 0
            students = []
            
            # This end shows that the loop is not complete yet
            end = False
            
            # Now looping the rows of the excel file 
            for _,row in df.iterrows():
                new_row_start = False
                # This will store the y value 
                y_val = e_val = 0 
                
                # looping through the column of the excel file now
                for col in df.columns:
                    # For each col couny +1 
                    e_val += 1 
                    
                    # If that shell ever have a string value, room col will store
                    cell_value = str(row[col])
                    
                    # Here the cell value represents the value inside the cell 
                    if cell_value :
                        
                        # This step is not really necessary but is used to assign the stripped value inside the cell 
                        cell_value  == cell_value.strip()
                        
                        # There are lot on empty cells, this represents the empty value
                        if cell_value == "nan":continue 
                        # Now if there is a cell with value entrance 
                        if cell_value.lower() == "entrance": 
                            
                            # the x and y of entrance is saved
                            seat_data[sheet_name]["entrance"] = [x_val,e_val]
                            
                            # ending the loop 
                            end = True
                            
                            # Breaking if the entrance is found. 
                            break 
                        
                        # Now the column are being read 
                        if y_val == 0: print()
                        
                        # For checking the value in terminal 
                        print(cell_value,end= " -- ")
                        
                        """
                        There is a distinction between the students name and seat name
                        desk name contains "-"
                        Students name does not contains "-"
                        
                        But in our case we dont need students because we are going to add students after randomizing
                        so this line of code can be ignoered RN 
                    
                    
                        
                        """
                        if not '-' in cell_value: 
                            students.append(cell_value)
                        else:
                            new_row_start = True
                            if not students : student = ""
                            else: student = students[0]
                            seat[cell_value] = {"x":x_val , "y":y_val, "student":student} 
                            students =  students[1:]
                        
                        if end: break 
                        y_val += 1 
                    
                    if end: break 
                    if new_row_start : 
                        x_val += 1 
                        print (x_val)


        for sheet_name  in seat_data:
            for key in seat_data[sheet_name]["seats"]:
                max_row = seat_data[sheet_name]["max_row"]
                max_col = seat_data[sheet_name]["max_col"]
                x = seat_data [sheet_name]["seats"][key]["x"]+1
                y = seat_data [sheet_name]["seats"][key]["y"]+1
                if x > max_row : seat_data[sheet_name]["max_row"] = x 
                if y > max_col : seat_data[sheet_name]["max_col"] = y 
            y = seat_data[sheet_name]["entrance"][1]
            if y > max_col: seat_data[sheet_name]["entrance"][1] = max_col
            else: seat_data[sheet_name]["entrance"][1] = 0
        with open("seat_plan.json", "w") as json_file:
            json.dump(seat_data, json_file, indent=4)

print("\nSeat plan saved as seat_plan.json")
                

test1 = ExcelTesting()
test1.readExcel()
