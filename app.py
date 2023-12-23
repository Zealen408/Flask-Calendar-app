from flask import Flask, render_template, request, redirect, url_for
from datetime import date, time, datetime
from calendar import Calendar
import csv
from external_variables import conductors, locations

app = Flask(__name__)

# A list to store the events
events = []


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        meeting_date = request.form.get('date')
        meeting_time = request.form.get('time')
        location = request.form.get('location')
        conductor = request.form.get('conductor')

        # convert date and time fields to date and time objects
        year, month, day = meeting_date.split('-')
        hour, minute, second = meeting_time.split(':')

        event = {
            # convert date field to date object
            'date': date(int(year), int(month), int(day)),
            'time': time(int(hour), int(minute), int(second)),
            'location': location,
            'conductor': conductor
        }

        if event not in events:
            events.append(event)
        events.sort(key=lambda x: (x['date'], x['time']))

    # Pass the events list to the template
    return render_template('index.html', events=events, conductors=conductors, locations=locations)


# a function to edit events
@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the form data from the request
        meeting_date = request.form.get('date')
        meeting_time = request.form.get('time')
        location = request.form.get('location')
        conductor = request.form.get('conductor')

        # Convert the meeting date and time to datetime objects
        # using the specified format
        date_obj = datetime.strptime(meeting_date, '%Y-%m-%d').date()
        time_obj = datetime.strptime(meeting_time, '%H:%M:%S').time()

        # Create an event dictionary with the parsed data
        event = {
            'date': date_obj,
            'time': time_obj,
            'location': location,
            'conductor': conductor
        }

        # Append the event to the events list and sort the list by date and time
        events.append(event)
        events.sort(key=lambda x: (x['date'], x['time']))

        # Redirect back to the previous page
        referrer = request.form.get('referrer')
        print(referrer)
        if referrer is None:
            print("Referrer is None")
        return redirect(referrer or '/')

    # Check if there are any events in the list
    if events:
        # Remove the event at the specified index from the events list
        event = events.pop(index)
        referrer = request.referrer
        # Render the edit.html template with the event and index as parameters
        return render_template('edit.html', event=event, index=index, locations=locations, conductors=conductors, referrer=referrer)

    # If there are no events in the list
    else:
        # Redirect to the homepage
        return redirect('/')


@app.route('/delete/<int:index>')
def delete(index):
    events.pop(index)
    return redirect(request.referrer or url_for('calendar'))


@app.route('/cal/<int:month>/<int:year>')
@app.route('/cal/<int:month>')
@app.route('/cal')
def calendar(month=None, year=None):
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month + 1

    if month > 12:
        month = 1
        year += 1
    
    if month < 1:
        month = 12
        year -= 1

    # Create a calendar object
    cal = Calendar()
    # Set Monday as the first day of the week
    cal.setfirstweekday(0)

    # set cal to selected year and month
    dates = cal.monthdatescalendar(year, month)

    # Pass the events list to the template
    return render_template('calendar.html', events=events, dates=dates, month=month, year=year)


@app.route('/backup')
def backup():
    with open('events.csv', 'w') as f:
        for event in events:
            f.write(f"{event['date']},{event['time']},{event['location']},{event['conductor']}\n")
    return redirect('/')
    

@app.route('/restore')
def restore():
    with open('events.csv', 'r') as f:
        for line in f:
            # Split the line into date, time, location, and conductor
            meeting_date, meeting_time, location, conductor = line.strip().split(',')
            year, month, day = meeting_date.split('-')
            hour, minute, second = meeting_time.split(':')
            event = {
                'date': date(int(year), int(month), int(day)),
                'time': time(int(hour), int(minute), int(second)),
                'location': location,
                'conductor': conductor
            }
            if event not in events:
                events.append(event)

        # sort the events by date
        events.sort(key=lambda x: (x['date'], x['time']))
    return redirect('/')


if __name__ == '__main__':
    if not events:
        _ = restore()

    app.run(debug=True)
