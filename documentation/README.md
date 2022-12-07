
# Design

Watch my video [here:](https://youtu.be/F2_FjIQKgHg)
Or [here](https://www.loom.com/share/b3e1718e0bff474e80cdfa9a27d3edb4), on Loom (quality might be better).

This project is available on github under ethanctan/commontime_submission.

I created this app using Flask for the backend and HTML, (Bootstrap) CSS and Javascript for the frontend. 

The following files are key to the functioning of this app:
- The .html files in /templates and the .css files in /static for the frontend,
- and app.py and commontime.db for the backend.

I will now walk through everything that happens when a user follows the flow that I've outlined in `README.md`.

# Creating an Event

Whenever a user creates a new event, the 'events' table in commontime.db is updated with the event's unique ID, name, start time, end time, and the user's timezone.

# Joining an Event

When the user joins an event, either through the Join Event page or by pasting in an event's unique URL, the 'events' table in commontime.db is searched for the event's ID. If a valid event exists, the user is directed to that event's page.

# Searching for Common Times

Searching for common times is tricky because it requires multiple conversions between datetime objects, differing formats and data types between Google Calendar's API, SQLite, Python, and easily-readable date & time strings, as well as the consideration of multiple timezones. I have created the following flow that takes all this into consideration:

1. When a user first connects a calendar to an event, the Google Calendar API is called and returns a list of the user's calendar items falling within the start and end times of the event.
2. The name, start, and end of each calendar item is read by app.py and inserted into the 'temp' table in commontime.db.
3. app.py then reads all items in the 'temp' table that has just been inserted (using this event's unique ID), and displays this on a table. This is when the user gets to delete events that they don't want to be included in the common time calculation; these events will then be deleted from the 'temp' table accordingly.
4. Once the user clicks 'submit', the items in the 'temp' table are pushed onto the 'times' table, which permanently stores all submitted calendar items, and the 'temp' table itself is cleared of all items corresponding to this event's id. 
5. Now, the calculation of common times takes place. First, app.py gets a list of all calendar items that correspond to this event's ID, ordered by SQLite according to starting date and time, and converts them to Python datetime objects.
6. Then, all the calendar items are 'merged' into blocks of 'uncommon' times - i.e. mutually disjoint blocks of time occupied by at least one calendar item. This is stored in an array of dicts, one dict per block. This step is necessary in order to not complicate the search for common times with overlapping calendar items.
7. Then, the aforementioned array of dicts is read, and the times between each block (as well as the event's start and end times) are pushed into another array of dicts - this time, with blocks of common times.
8. This array of dicts containing common times is then displayed on the table of common times on the event page.

To prevent errors due to different timezones, all dates and times are parsed and compared as Python datetime objects or SQLite datetime strings on the backend (which are standardized according to UTC), but converted to more easily-readable strings on the frontend. The timezone of the event creator herself is also taken into account, in order to prevent errors due to wrongly-interpreted event start and end times.

Apologies are rendered accordingly when the user attempts to take an invalid path:
- By trying to access an invalid event ID, and
- By inputting invalid event start and end times.

# What Changed from my Proposal?

In my original project proposal, I pondered using React or Vue for my project's frontend. However, as it stands, I don't think this project has enough common elements shared between its pages to warrant using React or Vue as a frontend framework.

Additionally, I considered adding a function allowing users to vote on common times. I realize now that this design decision wouldn't make sense, since the common times that are available for a given event will change every time a new calendar is connected - it would be more convenient and less complicated for users to simply look through the table of common times once everyone's connected their calendars and decide on a time (since, ostensibly, every person should be available during these common times anyway).

# Future Improvements

I think this app is genuinely useful; as such I intend to polish it and eventually publish it for use. Before doing so, I aim to:

- Add the option to search for common times of a minimum duration
- Stress-test the app with multiple calendar connections from different users at once, to see if the server has trouble updating and reading the SQL database
- Add the option to select a common time and automatically create a calendar event
- Add support for other calendars (e.g. Microsoft Calendar), as well as offline calendars if possible (by allowing uploads of .ics files)
