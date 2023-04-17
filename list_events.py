import datetime
# from cal_setup import get_calendar_service

def main(service):
#    service = get_calendar_service() # c_ukj1ahamef3djgapes637ns5cg@group.calendar.google.com
   # Call the Calendar API
   now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
   print('Getting List of 10 events')
   events_result = service.events().list(
       calendarId='primary', timeMin=now,
       maxResults=10, singleEvents=True,
       orderBy='startTime').execute()
   events = events_result.get('items', [])
   #print("id {}".format(events[0]["id"]))

   if not events:
       print('No upcoming events found.')
   for event in events:
       start = event['start'].get('dateTime', event['start'].get('date'))
       #print(event.eventId())
       print(start, event['summary'],"[id : {}]".format(event["id"]))

# if __name__ == '__main__':
#    main()