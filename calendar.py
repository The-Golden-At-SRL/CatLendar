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
def bookDate(date, hour, context, name, email, phoneNumber):
    toSave = []
    with open(csvPath, "r") as csvFile:
        csvCalendar = csv.DictReader(csvFile)
        
        for row in csvCalendar:
            if row["date"] == date and row["hour"] == hour:
                row["name"] = name
                row["email"] = email
                row["tel"] = phoneNumber
                row["context"] = context
                row["booked"] = "True"
            toSave.append(row)

    # And now save it
    with open(csvPath, "w") as csvFile:
        log.debug(toSave)
        fieldnames = ["date", "hour", "name", "email", "tel", "context", "booked"]
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in toSave:
            writer.writerow(row)
    
    
