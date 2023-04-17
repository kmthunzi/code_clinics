import datetime
from prettytable import PrettyTable
from simple_term_menu import TerminalMenu
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore
import cal_setup, pickle
import requests
import sys
import cc_firebase as fb
# cred = credentials.Certificate("cc-firebase.json")
# firebase_admin.initialize_app(cred)

# db = firestore.client()

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


# def get_existing_slots(userid):

#     slots = []

#     doctor_ref = db.collection(u'slots').stream()
#     # patient_ref = db.collection(u'slots').document(u'booked').collection(u''+userid).stream()
#     for doc in doctor_ref:
#         data = doc.to_dict()
#         slots.append([data["slot_date"], data["slot_time"], data["status"]])
#     # for doc in patient_ref:
#     #     data = doc.to_dict()
#     #     slots.append([data["slot_date"], data["slot_time"], data["status"]])

#     # print(slots)
#     return slots


# def confirm_slot(slot_info, client_id):

#     print(f"You're about to create a slot on '{slot_info['slot_date']}', at '{slot_info['slot_time']}' about '{slot_info['slot_topic']}'.")
#     print("Are you sure?")
#     confirm_menu = TerminalMenu(["Yes", "No", "Back"])
#     confirmation = confirm_menu.show()

#     if confirmation == 0:
#         doc_ref = db.collection(u'slots')
#         doc_ref.add(slot_info)


def show_slots(today, time, day, existing_slots):
    slots = []

    for slot in time_slots:
        # print([str(day), slot, "pending"], [str(day), slot, "pending"] in existing_slots)
        hour, mins = slot.split(":", 2)

        slot_hour = datetime.timedelta(hours=int(hour))
        current_hour = datetime.timedelta(hours=int(time.hour))
        slot_minute = datetime.timedelta(minutes=int(mins))
        current_minute = datetime.timedelta(minutes=int(time.minute))
        thirty_minutes = datetime.timedelta(minutes=30)

        if today.date() == day:
            if slot_hour < current_hour:
                slots.append(f"\033[1;31;40m-\033[1;37;40m")
                # slots.append(f"\033[1;31;40m{slot}\033[1;37;40m")
                continue
            elif slot_hour == current_hour and slot_minute < current_minute:
                slots.append(f"\033[1;31;40m-\033[1;37;40m")
                # slots.append(f"\033[1;31;40m{slot}\033[1;37;40m")
                continue
        elif [str(day), slot, "pending"] in existing_slots:
            slots.append(f"\033[1;33;40m pending \033[1;37;40m")
            # slots.append(f"\033[1;33;40m{slot}\033[1;37;40m")
            continue
        elif [str(day), slot, "accepted"] in existing_slots:
            slots.append(f"\033[1;32;40maccepted\033[1;37;40m")
            # slots.append(f"\033[1;32;40m{slot}\033[1;37;40m")
            continue

        slots.append(slot)
    
    return slots


def select_role():

    roles = ['Doctor', 'Patient']
    role_menu = TerminalMenu(roles)
    index = role_menu.show()

    return roles[index]


def select_date_time(available_slots, days):

    date_menu = TerminalMenu([str(day) for day in days])
    print("Choose date:")
    selected_date = date_menu.show()
    slot_date = str(days[selected_date])
    print(str(days[selected_date]))
    
    available_slots[selected_date] = [
        slot for slot in available_slots[selected_date] if "\033" not in slot
    ]

    slot_menu = TerminalMenu(available_slots[selected_date])
    print("Choose slot:")
    selected_slot = slot_menu.show()
    slot_time = available_slots[selected_date][selected_slot]
    print(available_slots[selected_date][selected_slot])

    return str(days[selected_date]), available_slots[selected_date][selected_slot]


def get_available_slots(userid):

    slot_date = []
    slot_time = []
    days = []

    today = datetime.datetime.now()
    time = today.time()
    number_of_days = 7

    available_slots = []
    existing_slots = fb.get_existing_slots(userid)
    x = PrettyTable()

    for i in range(number_of_days):
        day = today.date() + datetime.timedelta(days=i)
        slots = show_slots(today, time, day, existing_slots)
        x.add_column(str(day), slots)
        available_slots.append(slots)
        if len(slots) != 0:
            days.append(day)

    print(x)

    # std_out = sys.stdout
    # sys.stdout = open("test.txt", "w")
    # print(str(x).replace("\033[1;32;40m", "").replace("\033[1;31;40m", "").replace("\033[1;33;40m", "").replace("\033[1;37;40m", ""))
    # sys.stdout.close()
    # sys.stdout = std_out

    # test = open("test.txt", "r")
    # txt = test.read()
    # txt = txt.replace("\033[1;32;40m", "").replace("\033[1;31;40m", "").replace("\033[1;33;40m", "").replace("\033[1;37;40m", "")
    # print(txt)
    # test.close

    return available_slots, days


def create_slot(role):

    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

    details_url = f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={creds.token}'
    response = requests.get(details_url)

    user_details = response.json()
    userid = user_details["email"].split("@")[0]

    available_slots, days = get_available_slots(userid)

    slot_date, slot_time = select_date_time(available_slots, days)

    slot_topic = input("Whats the topic?")
    

    slot_info = {
        "slot_date": slot_date,
        "slot_time": slot_time,
        "slot_topic": "Code Clinics - "+slot_topic,
        "host_role": role,
        "status": 'pending',
        "host": userid,
    }

    fb.confirm_slot(slot_info, creds.client_id)

    return