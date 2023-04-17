import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
import os
import requests
import json
import datetime
import webbrowser
from simple_term_menu import TerminalMenu


cred = credentials.Certificate("cc-firebase.json")
firebase_admin.initialize_app(cred)

FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")

db = firestore.client()


def validate_id(id):
    '''
        validates id
        param:
        - id --> (str)
    '''

    document = db.collection('slots').document(id).get()

    if document.exists:
        return True

    print("Invalid ID. Please run the command" \
            " --> python3 cc.py my-calendar" \
            " or --> python3 cc.py canlendar to find an existing ID.")

    return False


def join(meeting_id, user_name):
    '''
        joins event googlemeet link address
        param:
        - meeting_id --> (str)
        - usr_name --> (str)
    '''
    doc = db.collection('slots').document(meeting_id).get()

    data = doc.to_dict()
    if data["status"] == "accepted" and data["host"] == user_name or \
    data["patient"] == user_name:
        webbrowser.open(data['link'])
    elif data["status"] == "pending":
        print("Unable to join:  This is an open slot, the meeting link hasn't been created.")
    else:
        print("Unable to join:  You aren't part of the meeting.")


def book_slot_by_id(user, id, calendar):
    '''
        books slot using event id
        param:
        - user --> (str)
        - id --> (str)
    '''

    desc = input("Please describe the problem you have: ")
    doc_ref = db.collection(u'slots').document(id)

    slot_data = doc_ref.get().to_dict()

    start_time = calendar.to_date(f"{slot_data['slot_date']} {slot_data['slot_time']}")
    end_time = start_time + datetime.timedelta(minutes=30)
    # print(start_time, end_time) 
    # print(str(start_time).split(' '), str(end_time).split(' '))
    # print('T'.join(str(start_time).split()))
    # print('T'.join(str(end_time).split()))
    event_id, google_meet_link = calendar.add_to_calendar(
        user, slot_data['slot_topic'], id, desc,
        'T'.join(str(start_time).split()),
        'T'.join(str(end_time).split()), slot_data['host'],
    )
    slot_ref = db.collection(u'slots').document(id)
    slot_ref.update({u'status': 'accepted'})
    slot_ref.update({u'description': desc})
    slot_ref.update({u'patient': user})
    slot_ref.update({u'event_id': event_id})
    slot_ref.update({u'link': google_meet_link})


def book_slot_by_date_time(slot_date, slot_time, user, calendar):
    '''
        books slot by date & time
        param:
        - slot_date -->(str)
        - slot_time -->(str)
        - user -->(str)

    '''

    if not is_multiple_slots(slot_date, slot_time):
        return

    doc_ref = db.collection(
        u'slots'
    ).where(
        u'status', u'==', u'pending'
    ).where(
        u'slot_date', u'==', ''+slot_date
    ).where(
        u'slot_time', u'==', ''+slot_time
    )
    
    desc = input("Please describe the problem you have: ")

    doc = doc_ref.stream()
    for slot in doc:
        slot_data = slot.to_dict()
        if slot_data['host'] != user:
            start_time = calendar.to_date(f"{str(slot_date)} {str(slot_time)}")
            end_time = start_time + datetime.timedelta(minutes=30)
            # print(start_time, end_time)
            # print(str(start_time).split(' '), str(end_time).split(' '))
            # print('T'.join(str(start_time).split()))
            # print('T'.join(str(end_time).split()))
            event_id, google_meet_link = calendar.add_to_calendar(
                user, slot_data['slot_topic'], slot.id, desc,
                'T'.join(str(start_time).split()),
                'T'.join(str(end_time).split()), slot_data['host'],
            )
            slot_ref = db.collection(u'slots').document(slot.id)
            slot_ref.update({u'status': 'accepted'})
            slot_ref.update({u'description': desc})
            slot_ref.update({u'patient': user})
            slot_ref.update({u'event_id': event_id})
            slot_ref.update({u'link': google_meet_link})
    return event_id


def check_your_availability(user_date, user_time, user):

    volunteer_ref = db.collection(
        u'slots'
    ).where(
        u'slot_date', u'==', u''+user_date
    ).where(
        u'slot_time', '==', u''+user_time
    ).where(
        u'host', '==', u''+user
    ).get()

    if len(volunteer_ref) == 1: # or len(patient_ref) == 1
        return True
    
    return False


def create_slot(slot_date, slot_time, user):
    topic = input("Which topic are you going to help with..? ")
    doc_ref = db.collection(u'slots')
    doc_ref.add({
        "host": user,
        "slot_date": slot_date,
        "slot_time": slot_time,
        "slot_topic": "Code Clinics - " + topic,
        "status": "pending",
        "host": user,
    })

    print(f"A slot on {slot_date} at {slot_time} was created for {topic}")
    

def check_slot(user_date, user_time, user):

    doc = db.collection(u'slots').where(u'slot_date', '==', u''+user_date).where(u'slot_time', '==', u''+user_time).where(u'host', '==', u''+user).get()

    if len(doc) == 1:
        return True
    
    return False


def is_multiple_slots(user_date, user_time):

    doc = db.collection(
        u'slots'
    ).where(
        u'status', u'==', u'pending'
    ).where(
        u'slot_date', '==', u''+user_date
    ).where(
        u'slot_time', '==', u''+user_time
    ).get()

    if len(doc) == 1:
        return True
    elif len(doc) > 1:
        print(f"There are multiple open slots on the \033[1;31;40m{user_date}" \
            f"\033[0;37;40m at \033[1;31;40m{user_time}\033[0;37;40m." \
            " Please use --> \033[1;31;40mpython3 cc.py <command> <id>\033[0;37;40m")
    else:
        print(f"There are no open slots on the \033[1;31;40m{user_date}" \
            f"\033[0;37;40m at \033[1;31;40m{user_time}\033[0;37;40m.")
    
    return False


def get_slot_info_by_id(id):

    doc = db.collection(u'slots').document(u''+id).get()

    return doc.to_dict()


def get_user_slots(user_name):#for cc
    slots = {}
    user_slots_ref = db.collection(u'slots').where(u'host', u'==', user_name).stream()

    for slot in user_slots_ref:
        slots[slot.id] = slot.to_dict()
    
    return slots


def get_slots():#for cc
    slots = {}
    slots_ref = db.collection(u'slots').stream()

    for slot in slots_ref:
        slots[slot.id] = slot.to_dict()

    return slots


def get_chosen_slot(slot_id):
    slot_info = []
    slot_ref = db.collection(u'slots').stream()

    for slot in slot_ref:
        data = slot.to_dict()
        doc_id = slot.id
        if doc_id == slot_id:
            slot_info.append(f"{data['host']},{doc_id},{data['slot_time']},{data['slot_date']},\
                {data['slot_topic']}")
    
    return slot_info


def validate_password(user_name, password):#for cc_auth

    rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    
    data = json.dumps({
        "email": user_name + "@student.wethinkcode.co.za",
        "password": password,
        "returnSecureToken": True
    })

    response = requests.post(rest_api_url,
        params={"key": FIREBASE_WEB_API_KEY},
        data=data
    )

    if response.status_code == 200:
        return True

    return False


def gen_dr_list(user_id):#for create event
    doctor_ref = db.collection(u'slots').where(u'status',u'==',u'pending').stream()
    
    doc_list = []

    for doc in doctor_ref:
        doc_id = doc.id
        data = doc.to_dict()
        if data['host'] != user_id:
            # doc_list.append(f"id : '{doc_id}'username :'{data['host']}' on the '{data['slot_date']}' at '{data['slot_time']}' topic:'{data['slot_topic']}' ")
            doc_list.append(f"{data['slot_date']}, {data['slot_time']}, {data['slot_topic']}, {doc_id}")

    return(doc_list) 


def change_status(doc_id,event_id,pat_id):#for create event

    doctor_ref = db.collection(u'slots').document(u''+doc_id)
    doctor_ref.update({u'status' : 'accepted'})
    doctor_ref.update({u'event_id' : u''+event_id})
    doctor_ref.update({u'patient' : u''+pat_id}) 


def get_pending_existing_slots(userid):#for create slot

    slots = []

    doctor_ref = db.collection(u'slots').where('host', '==', userid).where('status', '==', 'pending').stream()
    
    for doc in doctor_ref:
        data = doc.to_dict()
        doc_id = doc.id
        slots.append(f"{data['slot_date']}, {data['slot_time']}, {data['slot_topic']}, {doc_id}")

    return slots


def get_existing_slots(userid):#for create slot

    slots = []

    doctor_ref = db.collection(u'slots').where('host', '==', userid).stream()
    patient_ref = db.collection(u'slots').where('patient', '==', userid).stream()
    
    for doc in doctor_ref:
        data = doc.to_dict()
        slots.append([data["slot_date"], data["slot_time"], data["status"]])
        
    for doc in patient_ref:
        data = doc.to_dict()
        slots.append([data["slot_date"], data["slot_time"], data["status"]])

    return slots


def confirm_slot(slot_info, client_id):#for create slot

    print(f"You're about to create a slot on '{slot_info['slot_date']}', at '{slot_info['slot_time']}' about '{slot_info['slot_topic']}'.")
    print("Are you sure?")
    confirm_menu = TerminalMenu(["Yes", "No"])
    confirmation = confirm_menu.show()

    if confirmation == 0:
        doc_ref = db.collection(u'slots')
        doc_ref.add(slot_info)

    print(f"A slot on {slot_info['slot_date']} at {slot_info['slot_time']} was created for {slot_info['slot_topic']}")


def get_slot_details(userid):

    slots = []
    slot_ref = db.collection(u'slots').where(u'patient',u'==', userid).stream()

    for slot in slot_ref:
        data = slot.to_dict()
        doc_id = slot.id
        # if data['host'] == userid:
        slots.append(f"{data['slot_date']}, {data['slot_time']}, {data['slot_topic']}, {doc_id}")

    return slots


def delete_slot_by_date_time(slot_date, slot_time, user_name):
    '''
    Function checks if the slot_or_event_id (uuid of event) is your event by 
    checking if you are the host of the slot

    If True, slot will be deleted
    '''

    if not is_multiple_slots(slot_date, slot_time):
        return

    slot_ref = db.collection(u'slots').where(
        u'status', u'==', u'pending'
    ).where(
        u'slot_date', u'==', ''+slot_date
    ).where(
        u'slot_time', u'==', ''+slot_time
    ).stream()

    # slot = slot_ref
    for slot in slot_ref:
        data = slot.to_dict()
        if data['host'] == user_name and data['status'] == 'pending':
            db.collection(u'slots').document(u''+slot.id).delete()
            print("Successfully deleted a slot.")
        
        elif data['host'] == user_name and data['status'] == 'accepted':
            print("\nUnable to delete slot. Use delete-event for events.")

        elif data['host'] != user_name:
            print('\nThis slot doesn\'t belong to you.')


def delete_slot_by_id(id, user_name):
    '''
    Function checks if the slot_or_event_id (uuid of event) is your event by 
    checking if you are the host of the slot

    If True, slot will be deleted
    '''
    slot_ref = db.collection(u'slots').document(u''+id)

    slot = slot_ref.get()
    if slot.exists:
        data = slot.to_dict()
        if data['host'] == user_name and data['status'] == 'pending':
            db.collection(u'slots').document(u''+id).delete()
            print("\nSuccessfully deleted the slot.")
        
        elif data['host'] == user_name and data['status'] == 'accepted':
            print("\nUnable to delete slot. Use delete-event for events.")

        elif data['host'] != user_name:
            print('\nThis slot doesn\'t belong to you.')


def delete_event_by_date_time(slot_date, slot_time, user_name, calendar):
    '''
    Function checks if the slot_or_event_id (uuid of event) has you as the 
    Attendee of the event, and that you marked down as the patient(one who needs help)
    in the database

    If True, slot will be deleted
    '''

    # if not is_multiple_slots(slot_date, slot_time):
    #     return

    slot_ref = db.collection(u'slots').where(
        u'status', u'==', u'accepted'
    ).where(
        u'slot_date', u'==', ''+slot_date
    ).where(
        u'slot_time', u'==', ''+slot_time
    )

    slots = slot_ref.get()
    # print(slots)
    if slots == []:
        print(f"Unable to delete event: You don\'t have an event on {slot_date} at {slot_time}.")
        return

    for slot in slots:
        data = slot.to_dict()
        if data['patient'] == user_name:
            data['status'] = 'pending'
            calendar.delete_event(data['event_id'], user_name)
            data.pop('patient')
            data.pop('event_id')
            db.collection('slots').document(slot.id).set(data)
            print("Successfully deleted an event")
            break
        elif data['patient'] != user_name:
            print("Unable to delete event: Only the patient can cancel a event.")
        else:
            print('Unable to delete event: Event doesn\'t exits.')


def delete_event_by_id(id, user_name, calendar):
    '''
    Function checks if the slot_or_event_id (uuid of event) has you as the 
    Attendee of the event, and that you marked down as the patient(one who needs help)
    in the database

    If True, slot will be deleted
    '''
    slot_ref = db.collection(u'slots').document(u''+id)

    slot = slot_ref.get()
    if slot.exists:
        data = slot.to_dict()
        if data['status'] == 'pending':
            print('\nUnable to delete event: This is not an event.')
        elif data['patient'] == user_name:
            data['status'] = 'pending'
            if calendar.delete_event(data['event_id'], user_name):
                data.pop('patient')
                data.pop('event_id')
                slot_ref.set(data)
                print("Successfully canceled the booking.")
        else:
            print('Unable to delete event: Event doesn\'t exits.')