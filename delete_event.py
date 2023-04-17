## Script to delete events from google calendar

from cal_setup import get_calendar_service
import cc_firebase as fb

def main(event_id):
    # Delete the event
    service = get_calendar_service()
    try:
       service.events().delete(
           calendarId='primary',
           eventId= event_id,
           ).execute()
    except googleapiclient.errors.HttpError:
        print("Failed to delete event")

    print("Event deleted")