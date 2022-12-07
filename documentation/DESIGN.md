# Overview

This is a web app called commonti.me. Its purpose is to automatically find common meeting times between two or more Google Calendars. As far as I'm aware, none of the existing solutions for scheduling group meetings does this:
- When2Meet requires you to manually check your calendar and fill in your blocks of free time.
- Doodle requires you to manually check your calendar and vote on preferred times.
- Calendly is only used to schedule 1-on-1 meetings.
I thus believe my app will make it more convenient to schedule group meetings by automating the search process for common times.

# Setup

To run this app locally, you will first have to download the root directory and all the files therein. Then, you need to get your Client ID and API Key to enable the Google sign-in function:

1. Go to [this tutorial by Google](https://developers.google.com/calendar/api/quickstart/js#set_up_your_environment) and follow the instructions under 'Set up your environment'. Copy down your Client ID and API Key.
2. From the project root directory, open templates/event.html in your desired text editor.
3. Replace the CLIENT_ID and API_KEY's default values ('YOUR_ID' and 'YOUR_KEY') with your Client ID and API Key.
4. You can use my API Key that I've commented out, but you will still need a Client ID since it's a unique identifier for each browser/device.

After that, navigate to the project's root directory, and create a Python virtual environment and install flask if you haven't:

`python3 -m venv venv`
`. venv/bin/activate`
`npm install flask`

After that, input `flask run` . The project should then run on `127.0.0.1:5000` or `localhost:5000` . 

# Creating an Event

When you first load up the app, you will be on the New Event page. Here, you can create a new event for which you want to find common times. 

Optionally specify the event name, as well as a start and end time to designate the boundaries of your search for common times. If not, the app will search for common times within the next two weeks, or two weeks from your start time if you didn't specify an end time, or from now until your end time if you didn't specify a start time.

# Joining an Event

If you instead want to join an existing event, simply paste the event's unique URL into your browser or navigate to the 'Join Event' page and submit a valid event ID.

# Searching for Common Times

Once you're on an event page, you will see a table of common times between the event's participants (if at least one calendar has already been connected for this event), else you will see one commontime spanning the event's start and end times.

Click the "Connect New Calendar" button to connect a calendar associated with a Google account you own. After doing this, the page will refresh with an events table listing your calendar's items that fall within the range of this event. (You may have to manually refresh the page once for this table to show up.)

At this point, you may choose to delete any calendar events that you don't want to include in the common time calculation. For example, you may have a whole-day event on your calendar that doesn't actually occupy your entire day (maybe it might be a reminder, or a placeholder). 

After you're happy with the events you're submitting, click the "submit" button at the bottom of this table of events. The table of common times will then update accordingly.

If you have more than one calendar that you want to factor into the common time calculation, you can click the "Connect New Calendar" button more than once, and the events table will populate with items from all the calendar's you've connected. Alternatively, you can connect and submit calendars one at a time.

# Sharing an Event

To share the event you've created with other people you're inviting, just send them the event link or unique code.

Obviously, this won't work if you're hosting the app locally. I will deploy this app soon - probably at the domain commonti.me - to allow it to be used for its intended purpose.