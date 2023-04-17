import stdiomask
import os.path
import json
import datetime


def sign_in(fb, calendar):
    user = get_user(fb)

    config = None
    home = os.path.expanduser("~")

    data = {}

    if os.path.exists(f'{home}/.code clinics.config'):
        with open(f'{home}/.code clinics.config', 'r') as config:
            config = json.load(config)
            data = config
            data["user"] = user.uid
            data["time"] = str(datetime.datetime.today())
    else:
        data = {
            "user": user.uid,
            "time": str(datetime.datetime.today()),
        }

    with open(f'{home}/.code clinics.config', 'w') as new_config:
        json.dump(data, new_config, indent=4)

    calendar.get_calendar_permissions(user.uid)

    print(f"Welcome to code clinics {user.uid}. You can access Code Clinics features for the next 15 mins.")


def get_user(fb):
    """Method to sign into Code Clinics
    """

    user_name = input("\033[1;31;40mWTC Login username\033[0;37;40m: ")

    try:
        user = fb.auth.get_user(user_name)
        password = stdiomask.getpass("\033[1;31;40mWTC login password\033[0;37;40m: ")
        is_valid = fb.validate_password(user_name, password)

        while not is_valid:
            print("incorrect password. Please try again!")
            password = stdiomask.getpass("\033[1;31;40mWTC login password\033[0;37;40m: ")
            is_valid = fb.validate_password(user_name, password)

    except Exception as err:
        if "No user record found" in str(err):
            print(err)
            user, is_registered = register_user(fb, user_name)
            while not is_registered:
                user, is_registered = register_user(fb, user_name)
    finally:

        return user


def register_user(fb, user_name):
    '''
        registers user
        param:
        - user_name --> (str)
    '''
    print(f"Please create a password for user ID: {user_name}")
    password = stdiomask.getpass("\033[1;31;40mPassword\033[0;37;40m: ")
    password2 = stdiomask.getpass("\033[1;31;40mConfirm Password\033[0;37;40m: ")
    while password != password2:
        print(f"Passwords don't match! Please create a password for user ID: {user_name}")
        password = stdiomask.getpass("\033[1;31;40mPassword\033[0;37;40m: ")
        password2 = stdiomask.getpass("\033[1;31;40mConfirm Password\033[0;37;40m: ")

    try:
        user = fb.auth.create_user(
            uid=user_name,
            email=f'{user_name}@student.wethinkcode.co.za',
            email_verified=True ,
            password=password,
            disabled=False
        )

    except Exception as err:
        print(err)
        return None, False
    return user, True


def is_session_expired():
    '''
        checks if the session after login is expired

        returns:
        - boolean, dict or None
    '''
    config = None
    home = os.path.expanduser("~")

    today = datetime.datetime.today()

    data = {}

    if os.path.exists(f'{home}/.code clinics.config'):
        with open(f'{home}/.code clinics.config', 'r') as config:
            config = json.load(config)
            data = config

        if (
            datetime.datetime(
                int(data["time"][:4]), int(data["time"][5:7]),
                int(data["time"][8:10]), int(data["time"][11:13]),
                int(data["time"][14:16]),
            ) <= today - datetime.timedelta(minutes=15)
        ):
            print("Previous session expired, please sign-in to access the Code Clinics features")
            return True, None
    else:
        print("No previous login detected, please sign-in")
        return True, None

    return False, data
