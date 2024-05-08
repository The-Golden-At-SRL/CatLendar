from pydantic import BaseModel, create_model

import json

from cat.experimental.form import form, CatForm, CatFormState
from cat.log import log
from .calendar import getAvailableDates, bookDate

@form
class CalendarBookingForm(CatForm):
    description = "Book an appointment from those available"
    
    initJsonStr = '{"name": "str", "email": "str", "phoneNumber": "str", "bookingDate": "str"}'
    initJson = json.loads(initJsonStr)  

    # Create a dictionary of field names and types from initJson
    fields_dict = {key: (value, ...) for key, value in initJson.items()}
    
    # Dynamically create a Pydantic model
    CalendarBooking = create_model('CalendarBooking', **fields_dict)
    
    log.debug(CalendarBooking.schema_json(indent=2))
    
    
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
        # Get settings
        settings = self.cat.mad_hatter.get_plugin().load_settings()
        lang = settings["language"]
        
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

                availablePrompt = f"""Your task is to propose to the user the availble dates for booking an appointment. You should ask the question in {lang}.
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
                prompt = f"""Your task is to ask the user for an information. The information that you must ask is '{missing_fields_list[0]}'. You should ask the question in {lang}."""
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
            prompt = f"""Your task is to ask the user to confirm the choosen date for the appointment. The user shoul answer with yes or no.
            The choosen date is '{self._model["bookingDate"]}'. You should ask the question in {lang}."""
            out = self.cat.llm(prompt)

        return {
            "output": out
        }
    
    def submit(self, form_data):
        # Get settings
        settings = self.cat.mad_hatter.get_plugin().load_settings()
        lang = settings["language"]
        generate_context = settings["generate_context"]
                
        # Separate date and hour from user result
        availableDates = getAvailableDates()
        datePrompt = f"""Your task is to produce a JSON representing the informations that the user has given to you.
        JSON must be in this format:
        ```json
        {{
            "date": // type string or null, must contain a date in the format dd/mm/yyyy
            "time" // type string or null, must contain a time in the format hh:mm
        }}
        ```
        The date and the time choosen by the user must be in the following JSON:
        ```json
        {json.dumps(availableDates)}
        ```
        
        User said: "{form_data["bookingDate"]}"
        """
        response = self.cat.llm(datePrompt)
        log.debug(response)
                
        datePrompt = f"""Your task is to print only the date in the format dd/mm/yyyy from the following json: 
        {response}
        """
        choosendDate = self.cat.llm(datePrompt)
        
        hourPrompt = f"""Your task is to print only the time in the format hh:mm from the following json:
        {response}
        """
        choosenHour = self.cat.llm(hourPrompt)
        
        log.debug(choosendDate)
        log.debug(choosenHour)
        
        # Generate chat context
        context = ""
        if generate_context: 
            history = getattr(self.cat, "working_memory").history[:(-len(form_data) * 2)]
            
            history_string = ""
            for turn in history:
                history_string += f"\n - {turn['who']}: {turn['message']}"
            
            log.debug(history_string)
            contextPrompt = f"""The user has booked an appointment. Your task is to give a title to the appointment based on the chat that you had before the booking with the user.
            The title should be in {lang}.
            The history of your chat with the user is:
            \"{history_string}\""""
            
            context = self.cat.llm(contextPrompt)
            
        # Book it
        bookDate(choosendDate, choosenHour, context, form_data["name"], form_data["email"], form_data["phoneNumber"])
        
        # Generate final phrase
        prompt = f"""Your task is to tell the user that his appointment has been booked. You should write the phrase in {lang}."""
        out = self.cat.llm(prompt)
        
        return {
            "output": out
        }

