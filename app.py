from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50 import SQL
import random, string #for event ID generation
from datetime import datetime, timezone, timedelta 
from dateutil import parser
import iso8601
import pytz

db = SQL("sqlite:///commontime.db")

# HELPERS

def merge_times(times):
    times = iter(times)
    try:
        merged = next(times).copy()
        for entry in times:
            start, end = entry['start'], entry['end']
            if start <= merged['end']:
                # overlapping, merge
                merged['end'] = max(merged['end'], end)
            else:
                # distinct; yield merged and start a new copy
                yield merged
                merged = entry.copy()
        yield merged
    except StopIteration:
        return

def format(time):
    if type(time) == datetime:
        output = time.strftime("%m/%d/%y, %H:%M")
        return output
    elif type(time) == str:
        input = parser.parse(time)
        output = input.strftime("%m/%d/%y, %H:%M")
        return output
    else:
        return

# END HELPERS


app = Flask(__name__)

# Pass time formatting function
app.jinja_env.globals.update(format=format)

@app.route("/")
def home():
    return redirect(url_for('newevent'))

@app.route("/joinevent", methods=["GET", "POST"])
def joinevent():    
    if request.method == "GET":
        return render_template("joinevent.html")

    if request.method == "POST":
        eventid = request.form.get("eventidform")
        check = db.execute("SELECT eventid FROM events WHERE eventid = ?", eventid)
        if check:
            return redirect(url_for('event', **{"eventid": eventid}))
        else:
            return render_template("joinevent.html", apology = "Invalid ID")


@app.route("/newevent", methods=["GET", "POST"])
def newevent():
    if request.method == "GET":
        return render_template("newevent.html")

    if request.method == "POST":

        # Create a new event
        eventid = ''.join(random.choices(string.ascii_letters + string.digits, k=7)) #7 character random event ID
        eventname = request.form.get("eventname")
        starttime = request.form.get("starttime")
        endtime = request.form.get("endtime")

        # Check for validity of time
        now = datetime.now().replace(microsecond=0)
        if starttime:
            timetest_start = datetime.strptime(starttime, '%Y-%m-%dT%H:%M').replace(microsecond=0)
        else:
            timetest_start = now
        
        if endtime:
            timetest_end = datetime.strptime(endtime, '%Y-%m-%dT%H:%M').replace(microsecond=0)
        else:
            timetest_end = timetest_start + timedelta(hours=336)

        tolerance = 5 #so selecting 'now' from the form does not immediately return an invalid time

        if timetest_end < timetest_start: #If end time is earlier than start time
            return render_template("newevent.html", apology = 'End time cannot be earlier than start time!')
        if timetest_start + timedelta(minutes=tolerance) < now or timetest_end < now:
            return render_template("newevent.html", apology = 'Search time cannot start or end earlier than now!')

        # Get timezone of event creator to insert
        timezone = str(now.astimezone())[-6:] #relative to UTC; EST is -05:00
        
        # Insert all event details into database
        db.execute("INSERT INTO events (eventid, eventname, starttime, endtime, timezone) VALUES (?, ?, ?, ?, ?)",
        eventid, eventname, timetest_start.isoformat(sep = 'T'), timetest_end.isoformat(sep = 'T'), timezone)

        return redirect(url_for('event', **{"eventid": eventid})) #redirects to event page with eventid in URL


@app.route("/event/<eventid>", methods=["GET", "POST"])
def event(eventid):
    if eventid:
        check = db.execute("SELECT eventid, eventname FROM events WHERE eventid = ?", eventid)
        eventname = check[0]['eventname']
        if check:
            if request.method == "POST": #obtain gcal events whenever API is called
                if request.form.get("delete"): #Update temp table
                    db.execute("DELETE FROM temp WHERE caleventid LIKE ?", request.form.get("delete"))

                elif request.form.get("confirm"): #Push temp table to main times, then delete temp table
                    tempall = db.execute("SELECT * FROM temp WHERE eventid = ?", eventid)

                    for tempitem in tempall:
                        db.execute("INSERT INTO times (eventid, caleventname, caleventstarttime, caleventendtime, datesorter) VALUES (?, ?, ?, ?, ?)", eventid, tempitem['caleventname'], tempitem['caleventstarttime'], tempitem['caleventendtime'], tempitem['datesorter'])

                    db.execute("DELETE FROM temp WHERE eventid = ?", eventid)
                    print("temp cleared")

                else: #Populate temp table
                    raweventsdict = request.get_json()
                    rawevents = raweventsdict['value']
                    
                    #insert each array value into database along with this event ID
                    for event in rawevents:
                        #Insert start of event as a sqlite-readable date string for correct ordering when I compare two or more calendars.
                        eventstart_obj=iso8601.parse_date(event['start'])
                        eventstart_utc=eventstart_obj.astimezone(pytz.utc)
                        eventstart_utc_zformat=eventstart_utc.strftime('%Y-%m-%d %H:%M:%S')

                        # add timezones to full day events
                        timezone = datetime.now(pytz.timezone(raweventsdict['timezone'])).strftime('%z')

                        if len(event["start"]) == 10:
                            event["start"] = event["start"] + "T00:00:00" + timezone

                        if len(event["end"]) == 10: 
                            event["end"] = event["end"] + "T00:00:00" + timezone

                        db.execute("INSERT INTO temp (eventid, caleventname, caleventstarttime, caleventendtime, datesorter, caleventid) VALUES (?, ?, ?, ?, ?, ?)",
                        eventid, event['name'], event['start'], event['end'], eventstart_utc_zformat, event['id'])
                    
                    print("temp populated")

            # Find common times!
            starttime = db.execute("SELECT starttime FROM events WHERE eventid = ?", eventid)[0]['starttime']
            endtime = db.execute("SELECT endtime FROM events WHERE eventid = ?", eventid)[0]['endtime']
            tz = db.execute("SELECT timezone FROM events WHERE eventid = ?", eventid)[0]['timezone']
            temptable = db.execute("SELECT caleventname, caleventstarttime, caleventendtime, caleventid FROM temp WHERE eventid = ?", eventid)

            allevents = db.execute("SELECT caleventstarttime, caleventendtime FROM times WHERE eventid = ? ORDER BY datesorter", eventid)

            #parse all events into datetime objects
            alleventsParsed = []
            for event in allevents:
                parsedStart = parser.parse(event["caleventstarttime"])
                parsedEnd = parser.parse(event["caleventendtime"])

                alleventsParsed.append({'start': parsedStart, 'end': parsedEnd})

            #boundaries of common time search
            lowerbound = parser.parse(starttime + tz)
            upperbound = parser.parse(endtime + tz)
            commontimes = [] 

            #merge all calendar events to create blocks of uncommon times
            if alleventsParsed:
                alleventsMerged = list(merge_times(alleventsParsed))

                #convert uncommon times to blocks of common times
                for i, event in enumerate(alleventsMerged):
                    try: 
                        commontimes.append({'start': event['end'], 'end': alleventsMerged[i + 1]['start']})
                    except:
                        commontimes.append({'start': event['end'], 'end': upperbound})

                #make sure the first and last time blocks make sense
                #first time block:
                if alleventsMerged[0]['start'] > lowerbound:
                    commontimes.insert(0, {'start': lowerbound, 'end': alleventsMerged[0]['start']})

                #last time block:
                if commontimes[-1]['start'] > upperbound:
                    commontimes.pop()
                    
            else: #if there are no calendar events, the entire thing is a common time
                commontimes.append({'start': lowerbound, 'end': upperbound})

            return render_template("event.html",  **{"starttime": starttime, "endtime": endtime, "eventid": eventid, "commontimes": commontimes, "temptable": temptable, "eventname": eventname})
        else:
            return redirect(url_for("newevent.html", **{"apology": "You entered an invalid URL. Create a new event here."}))
    else:
        return redirect(url_for('joinevent')) #if no event id, redirect to join event page