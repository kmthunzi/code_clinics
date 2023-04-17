import firebase_setup as fb
from simple_term_menu import TerminalMenu
import requests
import cal_setup, pickle

def book_event(slot_id):
    '''
        books event
        param:
        - slot_id --> (str)
    '''

    slot_info = fb.get_chosen_slot(slot_id)
    print(slot_info)
    slot = slot_info[0].split(',')
    
    guest_email = f"{slot[0]}@student.wethinkcode.co.za"
    topic = slot[4]
    
    start = f"{slot[3]}T{slot[2]}:00"
    end_time_list = slot[2].split(":")
    # print(end_time_list)

    if end_time_list[1] == '00':
        end_time = f"{end_time_list[0]}:30:00"
    else :
        etime = int(end_time_list[0])
        etime += 1
        end_time = f"{etime}:00:00"
    end = f"{slot[3]}T{end_time}"

    print(f"You are about to make a booking with :{slot[0]}\n\
    On the topic :{slot[4]}\n\
    On the date :{slot[3]} between {slot[2]} - {end_time}\n")

    print('are you sure?\n')

    confim = TerminalMenu(['yes','no'])
    con = confim.show()

    if con == 0:
        main(guest_email,topic,start,end,slot_id)

def main(guest_email,topic,start,end,doc_id):
    '''

    '''

    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

    details_url = f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={creds.token}'
    response = requests.get(details_url)

    user_details = response.json()

    
    userid = user_details["email"].split("@")[0]



    service = cal_setup.get_calendar_service()

    event_result = service.events().insert(calendarId='primary',
        body={
            "summary": topic,
            "description": 'this is a test',
            "start": {"dateTime": start, "timeZone": 'Africa/Johannesburg'},
            "end": {"dateTime": end, "timeZone": 'Africa/Johannesburg'},
            "attendees": [
                {"email": guest_email},
                {"email": 'codeclinicsteam18@gmail.com'}
            ],
        }
    ).execute()
    fb.change_status(doc_id,event_result['id'],userid)
    print("created event")
    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start']['dateTime'])
    print("ends at: ", event_result['end']['dateTime'])