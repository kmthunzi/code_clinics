import argparse
import sys
import re
import datetime

import cc_auth as auth
import cc_firebase as fb
import cc_calendar as calendar
import automate as cc_auto


def validate_date_and_time():
    '''
        Validates date and time format in sys.args in index 2 and 3
    '''

    if not re.search("\d{4}-\d{2}-\d{2}", sys.argv[2]):
        print("The date parameter is invalid. Please use the following" \
            " format --> python3 cc.py volunteer 2020-01-02 12:00")

        return False

    if not re.search("\d{2}:\d{2}", sys.argv[3]):
        print("The time parameter is invalid. Please use the following format --> python3 cc.py volunteer 2020-01-02 12:00")

        return False

    today = datetime.datetime.today()

    date_time_data = sys.argv[2].split("-") + sys.argv[3].split(":")

    try:
        slot_date = datetime.datetime(
            int(date_time_data[0]),
            int(date_time_data[1]),
            int(date_time_data[2]),
            int(date_time_data[3]),
            int(date_time_data[4])
        )

        if slot_date < today:
            print("This date has passed, please use another date and time")
            return False
        
        if slot_date > today + datetime.timedelta(days=90):
            print("Cannot create a slot for a date which is more than 90 days from today.")
            return False

        if date_time_data[4] != '00' and date_time_data[4] != '30':
            print("Slots are only available in 30 min intervals, e.g (12:00, 12:30)")
            return False

    except Exception as err:
        if "day" in str(err):
            print("Invalid day")
            return False
        elif "month" in str(err):
            print("Invalid month")
            return False
        elif "hour" in str(err):
            print("Invalid hour")
            return False
        elif "minute" in str(err):
            print("Invalid minute")
            return False

    return True


def run_command(args, data, run_type):
    '''
        Checks which commands are being called and executes them accordingly.

        Parameters:
            sys.args(args) -->(str)
            data --> (dict)
            run-type --> (str)
    '''

    if "automate" in args:
        service = calendar.get_calendar_permissions(data['user'])
        cc_auto.run(data,service)
    
    if "my-calendar" in args:
        if len(args) == 3:
            calendar.my_calendar(fb, data, args[2])
        elif len(args) == 2:
            calendar.my_calendar(fb, data)
        else:
            print("Unable to view your calendar: Too many arguments. Please use the format below" \
            " --> python3 cc.py calendar <int>" \
            " . int allows values from 1-10")
    
    if "calendar" in args:

        if len(args) == 3:
            calendar.view_main_calendar(fb, data["user"], args[2])
        elif len(args) == 2:
            calendar.view_main_calendar(fb, data["user"])
        else:
            print("Unable to view your calendar: Too many arguments. Please use the format below" \
            " --> python3 cc.py calendar <int>" \
            " . int allows values from 1-10")

        # calendar.view_main_calendar(fb, data["user"])

    if  "volunteer" in args and (len(args) == 2):
        print("Unable to volunteer: There are some missing parameters. Please use the format "\
            "below --> python3 cc.py volunteer YYYY-MM-DD HH:MM")

        return
    
    elif "volunteer" in args:

        if fb.check_your_availability(args[2], args[3], data["user"]):
            print("Unable to volunteer: You already have a slot at that time!")
        elif calendar.check_your_availability(args[2], args[3], data["user"]):
            print("Unable to volunteer: You have an event at that time!")
        else:
            fb.create_slot(args[2], args[3], data["user"])

    if "cancel-slot" in args and run_type == 'date_n_time':

        fb.delete_slot_by_date_time(args[2], args[3], data["user"])

    elif "cancel-slot" in args and run_type == 'id':
        fb.delete_slot_by_id(args[2] , data["user"])

    elif "cancel-slot" in args:
        print("Unable to cancel slot: There are some missing parameters. Please use the format below" \
            " --> python3 cc.py cancel-slot <date> <time>" \
            " or --> python3 cc.py cancel-slot <id>")

        return

    if "book-slot" in args and run_type == 'date_n_time':

        if fb.check_your_availability(args[2], args[3], data["user"]):
            print("Unable to book slot: You are unavailable at that time!")
        elif calendar.check_your_availability(args[2], args[3], data["user"]):
            print("Unable to book slot: You have an event at that time!")
        else:
            fb.book_slot_by_date_time(args[2], args[3], data["user"], calendar)
    
    elif "book-slot" in args and run_type == 'id':

        slot = fb.get_slot_info_by_id(args[2])

        if slot["status"] == "accepted":
            print("slot already taken")
            return

        if fb.check_your_availability(slot["slot_date"], slot["slot_time"], data["user"]):
            print("Unable to book slot: You are unavailable at that time!")
        elif calendar.check_your_availability(slot["slot_date"], slot["slot_time"], data["user"]):
            print("Unable to book slot: You have an event at that time!")
        else:
            print("available")
            fb.book_slot_by_id(data['user'], args[2], calendar)
    
    elif "book-slot" in args:
        print("Unable to book slot: There are some missing parameters. Please use the format below" \
            " --> python3 cc.py book-slot <date> <time>" \
            " or --> python3 cc.py book-slot <id>")

        return

    if "cancel-booking" in args and run_type == 'date_n_time':

        fb.delete_event_by_date_time(args[2], args[3], data["user"], calendar)

    elif "cancel-booking" in args and run_type == 'id':

        fb.delete_event_by_id(args[2], data["user"], calendar)

    elif "cancel-booking" in args:
        print("UNable to cancel booking: There are some missing parameters. Please use the format below" \
            " --> python3 cc.py delete-event <date> <time>" \
            " or --> python3 cc.py cancel-booking <id>")

        return

    if "join" in args and len(args) == 3:
        fb.join(args[2], data["user"])
    
    elif "join" in args:
        print("Unable to join meeting: You are missing a parameters. Please use the format below --> python3 cc.py join <id>")

        return


def run():
    '''
        checks if session after sign-in is expired
        checks sys.args for valid commands
    '''


    args = sys.argv
    run_type = None
    

    if "sign-in" in args:

        auth.sign_in(fb, calendar)
        sys.exit()
    elif len(args) == 1 or "--help" in args or "-h" in args or "help" in args:
        print("""
usage:  cc  [-h | --help]
            <command> [<args>]

These are the cc commands that can be used in various situations:

all Code Clinic commands
    sign-in                 Signs you into the Code Clinic system.

    automate                Runs the system in terminal menu

    my-calendar             View your personal schedule.
        - optional args:    <int>  numbers of days to view (1-10)

    calendar                View the Code Clinic schedule.
        - optional args:    <int>  numbers of days to view (1-10)

    volunteer               Create a slot, volunteering to help others.
        - required args:     <YYYY-MM-DD> <HH:MM> Date and Time

    cancel-slot             Remove slot you volunteered for.
        - accepted args:    <YYYY-MM-DD> <HH:MM> Date and Time
        - accepted args:    <slot_id>  ID of slot. you can view slot_id by running cc calendar.

    book-slot               Book an avalaible slot.
        - accepted args:    <YYYY-MM-DD> <HH:MM> Date and Time
        - accepted args:    <slot_id>  ID of slot. you can view slot_id by running cc calendar.

    cancel-booking          Cancel a booking you made.
        - accepted args:    <YYYY-MM-DD> <HH:MM> Date and Time
        - accepted args:    <slot_id>  ID of slot. you can view slot_id by running cc calendar.

    join                    Join the google meets for your booking.
        - required args:    <slot_id>  ID of slot. you can view slot_id by running cc calendar.
""")
        sys.exit()

    is_session_expired, data = auth.is_session_expired()
    if is_session_expired:
        sys.exit()

    if len(args) == 4:
        if not validate_date_and_time():
            sys.exit()

        run_type = "date_n_time"

    elif len(args) == 3:

        if args[1] == "my-calendar" and args[1] == "calendar" and not args[2].isdigit():
            print("invalid number")
            sys.exit()

        elif args[1] != "my-calendar" and args[1] != "calendar" and not fb.validate_id(args[2]):
            sys.exit()

        if args[1] != "my-calendar" and args[1] != "calendar":
            run_type = 'id'
    
    run_command(args, data, run_type)


if __name__ == "__main__":

    run()


