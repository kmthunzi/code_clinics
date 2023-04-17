import datetime, sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from prettytable import PrettyTable
from prettytable import ALL as ALL
from simple_term_menu import TerminalMenu

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]

CREDENTIALS_FILE = 'credentials.json'

time_slots = [
    "07:00",
    "07:30",
    "08:00",
    "08:30",
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30",
    "17:00",
    "17:30",
]

def get_calendar_permissions(user_name):
    '''
        sets user perissions on calendar
    '''
    global service

    creds = None
    home = os.path.expanduser("~")
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(f'{home}/.{user_name}_token.pickle'):
        with open(f'{home}/.{user_name}_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            try:
                creds = flow.run_local_server(port=0)
            except Exception as exception:
                print("Not logged in", exception)
                exit()


    # Save the credentials for the next run
    with open(f'{home}/.{user_name}_token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_all_events(user_name, days):
    '''
        gets all code clinics and user events
        parameters:
        - user_name --> (str)
        - days --> (int)
        returns
        - list
    '''

    calendar_events = []
    service = get_calendar_permissions(user_name)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    last_day = (datetime.datetime.utcnow() + datetime.timedelta(days=int(days)-1)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='c_nbne6mmfbrl20dqvec8gm33flo@group.calendar.google.com',
        timeMin=now,
        timeMax=last_day, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = event['start'].get('dateTime', event['start'].get('time'))

        event_date = datetime.datetime(
            int(start[:4]), int(start[5:7]),
            int(start[8:10]), int(start[11:13]),
            int(start[14:16]),
        )

    return events


def get_calendar_events(user_name, days):
    '''
        gets all code clinics and user events
        parameters:
        - user_name --> (str)
        - days --> (int)
        returns
        - list
    '''

    calendar_events = []
    service = get_calendar_permissions(user_name)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    last_day = (datetime.datetime.utcnow() + datetime.timedelta(days=int(days)-1)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='c_nbne6mmfbrl20dqvec8gm33flo@group.calendar.google.com', timeMin=now,
        timeMax=last_day, singleEvents=True,
        orderBy='startTime', q='Code Clinics').execute()
    events = events_result.get('items', [])
 
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = event['start'].get('dateTime', event['start'].get('time'))

        event_date = datetime.datetime(
            int(start[:4]), int(start[5:7]),
            int(start[8:10]), int(start[11:13]),
            int(start[14:16]),
        )

    return events


def add_to_calendar(user_name, topic, doc_id, desc, start, end, host):
    '''
        adds event to code clinics calendar
        param:
        - user_name --> (str)
        - topic --> (str)
        - doc_id --> (str)
        - desc --> (str)
        - start --> (str)
        - end --> (str)
        - host --> (str)
    '''
    service = get_calendar_permissions(user_name)

    event_result = service.events().insert(
        calendarId='c_nbne6mmfbrl20dqvec8gm33flo@group.calendar.google.com',
        conferenceDataVersion=1,
        body={
            "summary": f"{topic} - {doc_id}",
            "description": f'{desc}',
            "start": {"dateTime": f"{start}+02:00"},
            "end": {"dateTime": f"{end}+02:00"},
            "attendees": [
                {
                    "email": f"{host}@student.wethinkcode.co.za",
                    "responseStatus": "accepted",
                    "comment": "host"
                },
                {
                    "email": f"{user_name}@student.wethinkcode.co.za",
                    "responseStatus": "accepted",
                    "comment": "patient"
                }
            ],
            "sendUpdates": "all",
            "conferenceData": {
                "createRequest": {
                    "requestId": "hangoutsMeet"
                }
            },
        }
    ).execute()
    # fb.change_status(doc_id,event_result['id'],userid)
    print("Succesfully booked the slot.")
    # print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start']['dateTime'])
    print("ends at: ", event_result['end']['dateTime'])
    return (event_result['id'], event_result['hangoutLink'])


def cc_get_days_events(user_name, day, current_day_events, current_day_slots, user_slots):
    '''
        gets todays events and slots
        param:
        - user_name --> (str)
        - day --> (int)
        - current_day_events --> (list)
        - current_day_slots --> (list)
        - user_slots --> (list)
        returns
        - list
    '''
    slots = []
    times = []

    for slot in time_slots:

        is_event = False
        test_str = ''

        for event in current_day_events:
            # print(event)

            if event["start"]["dateTime"][11:16] == slot:
                slot_id = str(event['summary']).split(' - ')[-1]
                txt = str(event['summary']).split(' - ')[:-1]
                txt = ' - '.join(txt)
                host, patient = get_roles(event["attendees"])
                color = ""
                if host == user_name or patient == user_name:
                    color = "\033[1;32;40m"
                else:
                    color = "\033[1;31;40m"
                
                test_str += f"{txt}\n\n" \
                    f"{color}[Booked]\033[0;37;40m \n\n" \
                    f"\033[1;30;37m{slot_id}\033[0;37;40m\n\n" \
                    f"host: {host}\n" \
                    f"patient: {patient}\n\n-----\n\n"

                is_event = True
                # break
            
        for data in current_day_slots:
            if (
                (user_slots[data]["slot_date"] == str(day) and
                user_slots[data]["slot_time"] == slot) and
                user_slots[data]["host"] == user_name and
                user_slots[data]["status"] == "pending"
            ):
                test_str += f"{user_slots[data]['slot_topic']}\n\n" \
                f"\033[1;36;40m[Pending]\033[0;37;40m \n\n" \
                f"\033[1;37;40m{data}\033[0;37;40m\n\n" \
                f"host: {user_slots[data]['host']}\n\n-----\n\n"
                is_event = True

            elif (
                user_slots[data]["slot_date"] == str(day) and
                user_slots[data]["slot_time"] == slot and
                user_slots[data]["status"] == "pending"
            ):
                test_str += f"{user_slots[data]['slot_topic']}\n\n" \
                f"\033[1;33;40m[Open]\033[0;37;40m \n\n" \
                f"\033[1;37;40m{data}\033[0;37;40m\n\n" \
                f"host: {user_slots[data]['host']}\n\n-----\n\n"
                is_event = True

        if is_event:
            slots.append(test_str.strip('\n\n-----\n\n'))
            # times.append(slot)
        
        elif not is_event:
            slots.append("")
            # times.append("")
    
    return slots


def get_days_events(user_name, day, current_day_events, current_day_slots, user_slots):
    '''
        gets todays events and slots
        param:
        - user_name --> (str)
        - day --> (int)
        - current_day_events --> (list)
        - current_day_slots --> (list)
        - user_slots --> (list)
        returns
        - list
    '''

    slots = []
    times = []
    # print(current_day_events)

    for slot in time_slots:

        is_event = False
        test_str = ''

        for event in current_day_events:
            if event["start"]["dateTime"][11:16] == slot:
                slot_id = str(event['summary']).split(' - ')[-1]
                txt = str(event['summary']).split(' - ')[:-1]
                txt = ' - '.join(txt)
                host, patient = get_roles(event["attendees"])

                color = ""
                if host == user_name or patient == user_name:
                    color = "\033[1;32;40m"
                    test_str += f"{txt}\n\n" \
                        f"{color}[Booked]\033[0;37;40m \n\n" \
                        f"\033[1;37;40m{slot_id}\033[0;37;40m\n\n" \
                        f"host: {host}\n" \
                        f"patient: {patient}\n\n-----\n\n"
                    is_event = True

        for data in current_day_slots:
            if (
                (user_slots[data]["slot_date"] == str(day) and
                user_slots[data]["slot_time"] == slot) and
                user_slots[data]["host"] == user_name  and
                user_slots[data]["status"] == "pending"
            ):
                # test_str = f"\033[1;36;40mYour Slot\033[0;37;40m\nid: {data}"
                test_str += f"{user_slots[data]['slot_topic']}\n\n" \
                f"\033[1;36;40m[Pending]\033[0;37;40m \n\n" \
                f"\033[1;37;40m{data}\033[0;37;40m\n\n" \
                f"host: {user_slots[data]['host']}\n\n-----\n\n"
                is_event = True
                # break
                # if user_slots[data]["host"] == user_name:
                #     test_str += f"\033[1;36;40mYour Slot\033[0;37;40m\nid: {data}\n-----\n"
                #     # slots.append(f"\033[1;36;40mYour Slot\033[0;37;40m\nid: {data}")
                # elif user_slots[data]["host"] != user_name:
                #     test_str += f"\033[1;33;40mOpen Slot\033[0;37;40m\nid: {data}\n-----\n"
                #     # slots.append(f"\033[1;33;40mOpen Slot\033[0;37;40m\nid: {data}")

            # elif (
            #     user_slots[data]["slot_date"] == str(day) and
            #     user_slots[data]["slot_time"] == slot and
            #     user_slots[data]["status"] == "pending"
            # ):
            #     test_str += f"{user_slots[data]['slot_topic']}\n\n" \
            #     f"\033[1;33;40m[Open]\033[0;37;40m \n\n" \
            #     f"\033[1;37;40m{data}\033[0;37;40m\n\n" \
            #     f"host: {user_slots[data]['host']}\n\n-----\n\n"
            #     is_event = True
                # slots.append(test_str.strip('\n\n-----\n\n'))

        if is_event:
            slots.append(test_str.strip('\n\n-----\n\n'))
            # times.append(slot)
        
        elif not is_event:
            slots.append("")
            # times.append("")
    
    return slots


def show_user_calendar(user_name, user_slots):
    '''
        shows users schedule
        param:
        - user_name --> (str)
        - user_slots --> (str)

    '''
    global service

    number_of_days = 7

    today = datetime.datetime.today()
    days_later = today + datetime.timedelta(days=number_of_days)
    min_date = today.isoformat() + 'Z' # 'Z' indicates UTC time
    max_date = days_later.isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=min_date, timeMax=max_date, singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    event_table = PrettyTable(hrules=ALL)
    event_table.align = "c"

    event_table.add_column("", time_slots)


    for i in range(number_of_days):
        day = today.date() + datetime.timedelta(days=i)
        current_day_events = [event for event in events if event["start"]["dateTime"][:10] == str(day)]
        current_day_slots = [
            data for data in user_slots
            if user_slots[data]["slot_date"] == str(today.date()) and user_slots[data]["host"] == user_name
        ]
        day_list = get_days_events(user_name, day, current_day_events, current_day_slots, user_slots)
        event_table.add_column(str(day), day_list)

    
    print(event_table)


def to_date(date):
    '''

    '''
    return datetime.datetime(
        int(date[:4]), int(date[5:7]),
        int(date[8:10]), int(date[11:13]),
        int(date[14:16]),
    )


def get_roles(attendees):
    '''
        gets host and patient of event
        return
        - str, str
    '''
    # print(attendees)
    host = [attendee['email'].split('@')[0] for attendee in attendees if attendee['comment'] == 'host']
    patient = [attendee['email'].split('@')[0] for attendee in attendees if attendee['comment'] == 'patient']
    return host[0], patient[0]


def my_calendar(fb, data, day=None):
    '''
        gets users events based on no. days
        params:
        - data -->(str)
        - day -->(int)
    '''

    today = datetime.datetime.today()
    user_name = data["user"]

    if day != None:

        if int(day) < 0 or int(day) > 11:
            print("You can specify up to 10 days.\nDefaulting to 7 days.")
            number_of_days = 7
        else:
            number_of_days = int(day)
    else:
        number_of_days = 7

    slots = fb.get_slots()
    events = get_calendar_events(user_name, number_of_days)
    # print(events)
    max_width = dict()
    
    days_later = today + datetime.timedelta(days=number_of_days)

    slots_table = PrettyTable(hrules=ALL)

    # slots_table.field_names = ["Date", "Time", "Event"]
    slots_table.add_column('', time_slots)

    for i in range(number_of_days):
        day = today.date() + datetime.timedelta(days=i)
        current_day_slots = [
            data for data in slots
            if slots[data]["slot_date"] == str(day)
        ]
        
        if not events:
            day_list = get_days_events(user_name, day, [], current_day_slots, slots)
            # print(day_list)
            slots_table.add_column(str(day), day_list)
        else:
            current_day_events = [
                event for event in events
                if to_date(event["start"]["dateTime"]).date() == day
            ]
            day_list = get_days_events(user_name, day, current_day_events, current_day_slots, slots)
            slots_table.add_column(str(day), day_list)

        max_width[str(day)] = 200 // number_of_days

    slots_table.align = "l"
    slots_table._max_width = max_width
    slots_table.left_padding_width = 0
    print(slots_table)


def check_your_availability(date, time, user_name):
    '''
        checks user avialability 
        param:
        - date --> (str)
        - time --> (str)
        - user_name --> (str) 

        returns:
        - boolean
    '''
    service = get_calendar_permissions(user_name)
    start_time = to_date(f"{date} {time}")
    end_time = start_time + datetime.timedelta(minutes=29)

    events_result = service.events().list(
        calendarId='primary', timeMin=f"{date}T{time}:00+02:00",
        timeMax=f"{date}T{str(end_time)[11:16]}:00+02:00", singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if len(events) == 0:
        return False

    return True


def delete_event(event_id, user_name):
    # Delete the event
    '''
        deletes event on calendar
        param:
        - event_id --> (str)
        - user_name --> (str)

    '''
    service = get_calendar_permissions(user_name)
    try:
       service.events().delete(
           calendarId='c_nbne6mmfbrl20dqvec8gm33flo@group.calendar.google.com',
           eventId= event_id,
           ).execute()
    except Exception as err:
        print("Failed to cancel event", err)

        return False

    return True


def view_main_calendar(fb, user_name, day=None):
    '''
        displays events for specified amount of days
        if day is not specified or < 10 and > 1, defualt is 7
        param:
         - user_name -->(str)
         - day --> (int) 
    '''

    if day != None:

        if int(day) < 0 or int(day) > 11:
            print("You can specify up to 10 days.\nDefaulting to 7 days.")
            number_of_days = 7
        else:
            number_of_days = int(day)
    else:
        number_of_days = 7

    slots = fb.get_slots()
    events = get_all_events(user_name, number_of_days)
    max_width = dict()

    today = datetime.datetime.today()
    days_later = today + datetime.timedelta(days=number_of_days)

    slots_table = PrettyTable(hrules=ALL)

    # slots_table.field_names = ["Date", "Time", "Event"]
    slots_table.add_column('time', time_slots)

    for i in range(number_of_days):
        day = today.date() + datetime.timedelta(days=i)
        current_day_slots = [
            data for data in slots
            if slots[data]["slot_date"] == str(day)
        ]
        
        if not events:
            day_list = cc_get_days_events(user_name, day, [], current_day_slots, slots)
            # print(day_list)
            slots_table.add_column(str(day), day_list)
        else:
            current_day_events = [
                event for event in events
                if to_date(event["start"]["dateTime"]).date() == day
            ]
            day_list = cc_get_days_events(user_name, day, current_day_events, current_day_slots, slots)
            slots_table.add_column(str(day), day_list)

        max_width[str(day)] = 200 // number_of_days
    # for i in range(number_of_days):

    #     day = today.date() + datetime.timedelta(days=i)
    #     current_day_slots = [
    #         data for data in slots
    #         if slots[data]["slot_date"] == str(day)
    #     ]
    #     if not events:
    #         day_list, times = cc_get_days_events(user_name, day, [], current_day_slots, slots)
    #         for i in range(len(day_list)):
    #             if day_list[i] != '':
    #                 slots_table.add_row([str(day), times[i], day_list[i]])
    #     else:
    #         current_day_events = [
    #             event for event in events
    #             if to_date(event["start"]["dateTime"]).date() == day
    #         ]
    #         day_list, times = cc_get_days_events(user_name, day, current_day_events, current_day_slots, slots)
    #         for i in range(len(day_list)):
    #             if day_list[i] != '':
    #                 slots_table.add_row([str(day), times[i], day_list[i]])

    slots_table.align = "l"
    # max_width["time"] = 5 // number_of_days
    slots_table._max_width = max_width
    slots_table.left_padding_width = 0
    # print(max_width)
    print(slots_table)
