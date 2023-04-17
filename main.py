<<<<<<< HEAD
#!/usr/local/bin/python3

import argparse
import sys
import doctor as d
import patient as p
import create_config


def do():
    pass


def login_commands(parser):
    group1 = parser.add_argument_group('Setup and Login')
    group1.add_argument('-I','--init', action='store_true', help="Creates the config file that will be used", default=False)
    group1.add_argument('-T','--token', action='store_true', help="View your token.", default=False)
    group1.add_argument('-LD','--login_doctor', action='store_true', help="Login as a doctor.", default=False)
    group1.add_argument('-LP','--login_patient', action='store_true', help="Login as a patient.", default=False)


def doctor_commands(parser): 
    group2 = parser.add_argument_group('Functionality for doctors')
    group2.add_argument('-CS','--create_slot', action = 'store_true', help = "Create a slot, volunteering to help others.", default=False)
    group2.add_argument('-DS','--del_slot', action = 'store_true', help = "Delete a slot.", default=False)
    # group2.add_argument('-US','--upd_slot', action = 'store_true', help = "Update a slot you create.", default=False)
    group2.add_argument('-LMS','--ls_my_slot', action = 'store_true', help = "List all slots you've made.", default=False)


def patient_commands(parser):
    group3 = parser.add_argument_group('Functionality for patients')
    group3.add_argument('-BS','--book_slot', action = 'store_true', help = "Book an avalaible slot.", default=False)
    group3.add_argument('-LAS','--ls_slots', action = 'store_true', help = "List available slots.", default=False)
    group3.add_argument('-DB','--del_booking', action = 'store_true', help = "Free a booking you made", default=False)
    # group3.add_argument('-UB','--upd_booking', action = 'store_true', help = "Update booking.", default=False)
    group3.add_argument('-LB','--ls_bookings', action = 'store_true', help = "List all your bookings.", default=False)


def handle_commands(parser):

    #login and setup commands
    parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    if parser.parse_args().init:
        print("Initializing...")
        create_config.main()
    if parser.parse_args().token:
        print("Display Token")
    if parser.parse_args().login_doctor:
        doc = d.Doctor(parser)
    if parser.parse_args().login_patient:
        doc = p.Patient(parser)


    #doctor commands 
    if parser.parse_args().create_slot:
        print("Creating a slot")
    if parser.parse_args().del_slot:
        print("Deleting a slot")
    # if parser.parse_args().upd_slot:
    #     print("Updating slot")
    if parser.parse_args().ls_my_slot:
        print("Listing your slots")


    #patient commands
    if parser.parse_args().book_slot:
        print("Book a slot")
    if parser.parse_args().ls_slots:
        print("List available slots")
    if parser.parse_args().del_booking:
        print("Delete your booking")
    if parser.parse_args().upd_booking:
        print("Update your bookings")
    if parser.parse_args().ls_bookings:
        print("List bookings")
=======
# import os.path
import cal_setup
from simple_term_menu import TerminalMenu
import list_events, create_event, delete_event, create_slot, list_slot

role = "patient"

# service = 
# import list_events

# valid_commands = {'patient-login',
#                  'doctor-login',
#                  'list-calendars', 
#                  'list-slots',
#                  'create-slot',
#                  'book-slot',
#                  'edit-slot',
#                  'delete-slot',
#                  'delete-booking'
#                  }

# def valid_login_command(command):
#     if command == 'patient-login' or command == 'doctor-login':
#         return True
#     return False


# def authorization():
#     try:
#         execfile('cal_setup.py')
#         return True
#     except Exception as e:
#         print(e)
#         return False


# def login(command):
#     if valid_login_command(command):
#         auth_completed = authorization()
#     else:
#         print("You need to login with 'patient-login' or 'doctor-login'")
#         command = input("Please login:")
#         login(command)


def logged_in():
    if os.path.exists("token.pickle"):
        return True
    return False
>>>>>>> 9d7994991d828ecd8261617b480d35311e1a1351


def run():
    parser = argparse.ArgumentParser(description = "********************** This is code clinic. **********************")
    parser.add_argument('-V','--version', action = 'store_true', help = "Get the app version", default=False)

    login_commands(parser)
    doctor_commands(parser)
    patient_commands(parser)

    handle_commands(parser)


if __name__ == '__main__':
    run()


<<<<<<< HEAD
=======
    global role

    print("Welcome to Code Clinics")
    service = None

    # while not logged_in():
    print("Please login with your student email to access the Code Clinics")
    service = cal_setup.get_calendar_service()

    roles = ["doctor", "patient"]

    role_menu = TerminalMenu(roles)
    selected_role_index = role_menu.show()
    role = roles[selected_role_index]


    main_functions = [
        'list-events', 
        'list-slots',
        'create-slot',
        'book-slot',
        'edit-slot',
        'delete-slot',
        'delete-booking',
        'exit'
    ]

    if role == "doctor":
        main_functions.pop(3)
        main_functions.pop(5)
    else:
        main_functions.pop(2)
        main_functions.pop(4)
        main_functions.pop(5)

    print("please wait while we load your calendar...")
    print()
    print("<Shows user events or Code Clinics Events>")

    while True:

        print("How can we help you.?")
        

        main_menu = TerminalMenu(main_functions)
        user_choice = main_menu.show()
        print(main_functions[user_choice])
        
        if main_functions[user_choice] == "list-events":
            list_events.main(service)
        elif main_functions[user_choice] == "list-slots":
            # create_event.main()
            list_slot.get_available_slots()
            main_functions.remove("list-slots")
        elif main_functions[user_choice] == "create-slot":
            # create_event.main()
            create_slot.create_slot(role)
        # elif main_functions[user_choice] == "delete-booking" :
            # delete_event.main()
        elif main_functions[user_choice] == "book-slot":
            create_event.choose_slot()
        elif main_functions[user_choice] == "exit":
            print("Thank you for visiting our code clinic. Bye!")
            break
        

if __name__ == "__main__":
    run()
>>>>>>> 9d7994991d828ecd8261617b480d35311e1a1351
