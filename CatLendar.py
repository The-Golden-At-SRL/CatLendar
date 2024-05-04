from pydantic import BaseModel

import json
from cat.experimental.form import form, CatForm, CatFormState
from cat.log import log
from .calendar import getAvailableDates, bookDate


lang = "italian"

class CalendarBooking(BaseModel):
    name: str
    email: str
    phoneNumber: str
    bookingDate: str
    
@form
class CalendarBookingForm(CatForm):
    description = "Book an appointment from those available"
    model_class = CalendarBooking
    start_examples = [
        "I want to book an appointment",
    ]
    stop_examples = [
        "Cancel reservation"
    ]
    
    # It gives some problems with the current version
    ask_confirm = False    
        
    # Override because current version is experimental and provides a dev output
    def message(self):
        
        if self._state == CatFormState.CLOSED:
            return {
                "output": f"Form {type(self).__name__} closed"
            }

        separator = "\n - "
        missing_fields = ""
        
        out = ""
        
        next_request = ""
        missing_fields_list = []
        
        if self._missing_fields:
            missing_fields = "\nMissing fields:"
            missing_fields += separator + separator.join(self._missing_fields)
            
            # missing_fields is a str, we want a list
            for missing in self._missing_fields:
                log.debug(f"MISSING: {missing}")
                missing_fields_list.append(missing)
                
            # A little bit hardcoded, but it's the fastest way
            if missing_fields_list[0] == "bookingDate":
                # Get available dates
                availableDates = getAvailableDates()
                log.debug(availableDates)

                availablePrompt = f"""Your task is to propose to the Human the availble dates for booking an appointment. You should ask the question in {lang}.
                The available dates are the following:
                ```json
                {json.dumps(availableDates)}
                ```
                Write a list to the user that summerise the available dates.
                """
                availablePromptEscaped = availablePrompt.replace("{", "{{").replace("}", "}}")
                
                response = self.cat.llm(availablePromptEscaped)
                
                log.debug(response)
                
                out = response
            else:    
                # Here we want to generate a request phrase
                prompt = f"""Your task is to ask the Human for an information. The information that you must ask is '{missing_fields_list[0]}'. You should ask the question in {lang}."""
                response = self.cat.llm(prompt)
                log.debug(f"RESPONSE: {response}")
                out = response
            
            log.debug(missing_fields_list)
            log.debug(f"Output: {missing_fields_list[0]}")
                
        invalid_fields = ""
        
        if self._errors:
            invalid_fields = "\nInvalid fields:"
            invalid_fields += separator + separator.join(self._errors)
            
    
        if self._state == CatFormState.WAIT_CONFIRM:
            # Generate confirm phrase
            prompt = f"""Your task is to ask the Human to confirm the choosen date for the appointment. The Human shoul answer with yes or no.
            The choosen date is '{self._model["bookingDate"]}'. You should ask the question in {lang}."""
            out = self.cat.llm(prompt)

        return {
            "output": out
        }
    
    def submit(self, form_data):        
        # Separate date and hour from user result
        datePrompt = f"""Your task is to print only the date in the format dd/mm/yyyy from the following string: '{form_data["bookingDate"]}'"""
        choosendDate = self.cat.llm(datePrompt)
        hourPrompt = f"""Your task is to print only the time in the format hh:mm from the following string: '{form_data["bookingDate"]}'"""
        choosenHour = self.cat.llm(hourPrompt)
        
        # Book it
        bookDate(choosendDate, choosenHour, form_data["name"], form_data["email"], form_data["phoneNumber"])
        
        # Generate final phrase
        prompt = f"""Your task is to tell the Human that his appointment has been booked. You should write the phrase in {lang}."""
        out = self.cat.llm(prompt)
        
        return {
            "output": out
        }

