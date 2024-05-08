# CatLendar - Books your appointments
![CatLendar](logo.png)

This plugin uses an experimental feature of Cheshire Cat AI frameworks.

Now the agent can book appointments for the user in a given calendar. It can be used inside a chatbot. When the user asks for an appointment, the cat will automatically ask the required fields

## Features
1. Detect when user wants to book an appointment
2. Multilingual
3. Recognize chat context to give the appointment a title

## Calendar
All the available slots are in the `calendar.csv` file. The mandatory columns of this file are:
- date
- hour
- context
- booked

This is an example with also additional fields:
```csv
date,hour,name,email,tel,context,booked
10/05/2024,14:30,,,,,False
10/05/2024,15:30,,,,,False
10/05/2024,16:30,,,,,False
10/05/2024,17:30,,,,,False
11/05/2024,08:30,,,,,False
11/05/2024,09:30,,,,,False
11/05/2024,10:30,,,,,False
11/05/2024,11:30,,,,,False
```

## Settings
1. Language - set the used language
2. Generate Context - set the context usage. If active, a title for the appointment will be generated.

## Custom Fields
If you want to ask for custom fields, just modify the `fields.json` file inside the plugin folder like in the next example.
```json
{
    "name": "str",
    "email": "str",
    "phoneNumber": "str"
}
```
Notice: also the `calendar.csv` file needs to be modified (ant the fields should be in the same order as above). For example:
```csv
date,hour,name,email,tel,context,booked
10/05/2024,14:30,,,,,False
10/05/2024,15:30,,,,,False
10/05/2024,16:30,,,,,False
10/05/2024,17:30,,,,,False
11/05/2024,08:30,,,,,False
11/05/2024,09:30,,,,,False
11/05/2024,10:30,,,,,False
11/05/2024,11:30,,,,,False
```
The added fields are always inserted between `date,hour` and `context,booked`.

## Future Roadmap
- Expand the availability proposal to make it more "intelligent"
- Add an integration with external service
- Integration with WordPress
