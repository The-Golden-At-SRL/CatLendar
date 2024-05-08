import os
import csv

from cat.log import log

csvPath = os.path.join(
    os.path.dirname(__file__), "calendar.csv"
)

# Returns available dates
def getAvailableDates():
    allDates = []
    
    with open(csvPath, "r") as csvFile:
        csvCalendar = csv.DictReader(csvFile)
        
        for row in csvCalendar:
            if row["booked"] == "False":
                allDates.append(row)

    
    return allDates 

# Books an appointment
def bookDate(date, hour, context, fields):
    toSave = []
    with open(csvPath, "r") as csvFile:
        csvCalendar = csv.DictReader(csvFile)
        
        for row in csvCalendar:
            if row["date"] == date and row["hour"] == hour:
                for key in fields:
                    row[key] = fields[key]
                row["context"] = context
                row["booked"] = "True"
            toSave.append(row)
    log.debug(toSave)
    # And now save it
    with open(csvPath, "w") as csvFile:
        log.debug(toSave)
        fieldnames = ["date", "hour"]
        
        for key in fields:
            fieldnames.append(key)
                      
        fieldnames.append("context")
        fieldnames.append("booked")
        
        log.debug(fields)
        log.debug(fieldnames)
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in toSave:
            writer.writerow(row)
    
    
