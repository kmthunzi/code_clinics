
from simple_term_menu import TerminalMenu
from prettytable import PrettyTable
import os.path
import cc_firebase as fb
import datetime
import json
import cc_auth as auth
import cc_calendar as calendar

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

def run(data,service):
    '''

    '''

    print("Welcome to Code Clinics automation system")

    user_name = data['user']


    main_functions = [
        'calendar', 
        'create-slot',
        'book-slot',
        'cancel-slot',
        'cancel-booking',
        'exit'
    ]


    while not check_token_expiry() :

        print("How can we help you.?")
        

        main_menu = TerminalMenu(main_functions)
        user_choice = main_menu.show()
        print(main_functions[user_choice])
        
        if main_functions[user_choice] == "calendar":

            cal_menu = TerminalMenu(['Code Clinics', 'Personal'])
            num_days = [str(i) for i in range(1, 11)]
            days_menu = TerminalMenu(num_days)

            print("which calendar would you like to view?")
            
            # cal = input("1 = Code Clinics\n2 = Personal\n:")
            cal = cal_menu.show()
            # while True:

            if cal == 0:
                
                print("How many days would you like to view?")
                days = days_menu.show()
                calendar.view_main_calendar(fb, user_name, days + 1)
            
            elif cal == 1:
                
                print("How many days would you like to view?")
                days = days_menu.show()
                calendar.my_calendar(fb,data, days + 1)

        elif main_functions[user_choice] == "create-slot":
            
            print("You are about to volunteer for a slot.")
            while True:
                ans = input("Are you sure? Y/N: ")
                if ans.lower() == 'y':
                    create_slot(data)
                    break
                
                elif ans.lower() == 'n':
                    break
                else:
                    print("Please choose a valid command.")
                    continue

        elif main_functions[user_choice] == "cancel-booking" :

            while True:
                ans = input("You are about to delete a booking you made with a volunteer.\nAre you sure? Y/N: ")
                if ans.lower() == 'y':
                    delete_event(data)
                    break
                elif ans.lower() == 'n':
                    break
                else:
                    print("Please choose a valid command.")
                    continue

        elif main_functions[user_choice] == "book-slot":
            
            while True:
                ans = input("You are about to make a booking with a volunteer.\nAre you sure? Y/N : ")
                if ans.lower() == 'y':
                    book_slot(data)
                    break
                elif ans.lower() == 'n':
                    break
                else:
                    print("Please choose a valid command.")
                    continue

        elif main_functions[user_choice] == "cancel-slot":
            
            while True:
                ans = input("You are about to delete a slot you made as a volunteer.\nAre you sure? Y/N : ")
                if ans.lower() == 'y':
                    delete_slot(data)
                    break 
                elif ans.lower() == 'n':
                    break
                else:
                    print("Please choose a valid command.")
                    continue

        elif main_functions[user_choice] == "exit":
            print("Thank you for visiting our code clinic. Bye!")
            break
    

def check_token_expiry():
    '''
        checks if session after sign-in is expired
        -Returns --> Boolean
    '''
    
    is_session_expired,data = auth.is_session_expired()

    if is_session_expired:
        return True
    else:
        return False


def book_slot(data):
    '''
        checks for available slots and displays them in terminal menu

        Parameters:
        - Data --> (dict)
    '''
    user_id = data['user']
    slots = fb.gen_dr_list(user_id)
    print('Here is the list of open slots:')

    # confirm_menu = TerminalMenu(doc_list)
    # confirmation = confirm_menu.show()

    if len(slots) != 0:
        confirm_menu = TerminalMenu(slots)
        con = confirm_menu.show()
        chosen_slot = slots[con].split(', ')[3]
        fb.book_slot_by_id(user_id, chosen_slot, calendar)
    else:
        print("Sorry there are no slots available to book")
        chosen_slot = ""

    # get_details(confirmation,doc_list,data)


def get_details(confirmation,doc_list,data):
    '''
        Gets details of event and asks for confirmation if 'yes' is chosen 
        for booking slot
        
        Parameters:
        - confirmation --> (str)
        - doc_list -->  (dict)
        - data --> (dict)
    '''
    split_doc = doc_list[confirmation].split("'")    

    doc_id = split_doc[1]

    print('are you sure?')

    confim = TerminalMenu(['yes','no'])
    con = confim.show()

    if con == 0:
        print('creating event on code clinics calendar')

        fb.book_slot_by_id(data['user'], doc_id, calendar)
    elif con == 1:
        print('you have canceled the slot')

    return


#for deleting event

def delete_event(data):

    userid = data['user']

    slots = fb.get_slot_details(userid)
    if len(slots) != 0:
        confirm_menu = TerminalMenu(slots)
        con = confirm_menu.show()
        chosen_slot = slots[con].split(', ')[3]
        fb.delete_event_by_id(chosen_slot, userid, calendar)
    else:
        print("Sorry you dont have any slots available to cancel")
        chosen_slot = ""

    # print(chosen_slot)


#for deleting a slot


def delete_slot(data):
    '''
        Deletes user slot if slot belongs to user and is not booked

        Parameters:
        - data --> (dict) 
    '''


    userid = data['user']
    slots = fb.get_pending_existing_slots(userid)

    if len(slots) != 0:

        print("Here is a list of all the slots you will be able to cancel your availability\n")
        confirm_menu = TerminalMenu(slots)
        con = confirm_menu.show()
        chosen_slot = slots[con].split(', ')[3]
        fb.delete_slot_by_id(chosen_slot, userid)

        print('you have succesfully removed your slot.')

    else:
        print("Sorry you have no available slots to cancel")


#for creating a slot

def create_slot(data):
    '''
        creates slot if slot time is available

        parameters:
        - data --> (dict)
    '''
    userid = data['user']

    available_slots, days = get_available_slots(userid)

    slot_date, slot_time = select_date_time(available_slots, days)

    slot_topic = input("Which topic are you going to help with..? ")
    

    slot_info = {
        "slot_date": slot_date,
        "slot_time": slot_time,
        "slot_topic": "Code Clinics - " + slot_topic,
        "status": 'pending',
        "host": userid,
    }

    fb.confirm_slot(slot_info, userid)

    return


def get_available_slots(userid):

    '''
        checks for available slots that don't belong to the user

        parameters:
        - userid --> (str)
    '''

    days = []

    today = datetime.datetime.now()
    time = today.time()
    number_of_days = 10

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

    return available_slots, days


def show_slots(today, time, day, existing_slots):
    '''
        checks for future slots based on existing slots

        parameters:
        - today --> (str)
        - time --> (str)
        - day --> (str)
        - existing_slots --> (list)
    '''
    slots = []

    for slot in time_slots:

        hour, mins = slot.split(":", 2)

        slot_hour = datetime.timedelta(hours=int(hour))
        current_hour = datetime.timedelta(hours=int(time.hour))
        slot_minute = datetime.timedelta(minutes=int(mins))
        current_minute = datetime.timedelta(minutes=int(time.minute))

        if today.date() == day:
            if slot_hour < current_hour:
                slots.append(f"\033[1;31;40m-\033[1;37;40m")
                continue
            elif slot_hour == current_hour and slot_minute < current_minute:
                slots.append(f"\033[1;31;40m-\033[1;37;40m")
                continue
        elif [str(day), slot, "pending"] in existing_slots:
            slots.append(f"\033[1;33;40m pending \033[1;37;40m")
            continue
        elif [str(day), slot, "accepted"] in existing_slots:
            slots.append(f"\033[1;32;40maccepted\033[1;37;40m")
            continue

        slots.append(slot)
    
    return slots


def select_role():
    '''
        asks for user role

        return:
        - (str)
    '''

    roles = ['Doctor', 'Patient']
    role_menu = TerminalMenu(roles)
    index = role_menu.show()

    return roles[index]


def select_date_time(available_slots, days):
    '''
        
    '''

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




#What needs to be changed for main functionality
