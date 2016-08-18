#!/usr/bin/env python3

#   Author:Derek
#   17 August 2016
#   Raspbian Jessie / Python 3.4.2
#   Raspberry Pi 2B

import RPi.GPIO as GPIO         # GPIO Functions
import os                       # Underlying OS functions
import time                     # Time functions - sleep
from matrixKeyboard import keypad   # Adeept Keypad
import csv                      # CSV file fucntions
import sys                      # Python specific functions

global array_list       # Name of the item list
array_list = []     
global database_file
database_file = 'ws_product_database.csv'   # item database file
global working_path     # Will be set by path handler as remote or local paths to database file.

GREEN_LED_PIN = 40
RED_LED_PIN = 38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(RED_LED_PIN, GPIO.OUT)

def main_menu():    # Main function providing menu of program features, stocktake, write files, exit.
    menu_loop = True
    valid_menu_options = [1, 2, 3]  # Define valid keypad options
    instance_keypad = keypad()     # Create instance of keypad from matrixKeyboard to detect selection of menu options
    menu_options()                  # Call menu_options to list user menu options
    while menu_loop:            # Main loop. All activities except exit return here.
        try:
            menu_selection = instance_keypad.getKey()       # Detect keypad entry
            if menu_selection is not None and menu_selection not in valid_menu_options:     # Validate keypad entry as 1,2,3
                print(menu_selection)
                time.sleep(2)
                print("Your entry was invalid. Please select a number option 1 - 3.")
                time.sleep(2)
                menu_options()
            elif menu_selection is None:
                pass
            elif menu_selection == 1:   # If selection 1 call stocktake()
                stocktake()
            elif menu_selection == 2:   # If selection 2 call write_list()
                write_list(working_path, database_file)     # Write list of records to database file.
                os.system('clear')
                menu_options()
            elif menu_selection == 3:   # If selection 3 exit
                exit_program()      # Exit the program cleanly.
        except KeyboardInterrupt:
            print('Your entry was invalid. Please select a number option 1 - 3.')   # Trap keyboard interupt as error. Continue loop
            time.sleep(2)


def read_list(working_path, database_file):        # Read all the records of the dtabase file onto a python list - array.
    try:
        with open(working_path + database_file, 'r') as my_database_object:     # Open the CSV database file
            list_reader = csv.reader(my_database_object)
            if os.stat(working_path + database_file).st_size == 0:      # Trap database file exists but file length is 0, no records.
                my_database_object.close()
                sys.exit('The database file contains no records. Can not continue!')    # If there are no records, Exit .
            for row in list_reader:     # reading records to list array_list.
                array_list.append(row)
            my_database_object.close()
    except IOError:
        print('An file IO error has occured.')  # Trap filesystem errors.
        my_database_object.close()


def menu_options():     # Print the main menu options.
    os.system('clear')
    print('Wood Stocks product database')
    print('Please enter a number corresponding to your task requirements')
    print('1. Complete product stock adjustment.')
    print('2. Write records to file.')
    print('3. Exit without writing records to file.')


def stocktake():        # Iterate through all records of the database file, allowing new quantity entries.
    time.sleep(.25)
    for counter in range(0, len(array_list)):
        new_qty = receive_input(counter)        # Calls receive_input to receive a valid item new quantity
        array_list[counter][2] = new_qty        # Replace the existing quantity of  an item in the database with the current new quantity
        if counter == len(array_list):          # Advise user the end of the list has been reached
            print('You have reached the end of the database items. You should now save the records the database.')
            time.sleep(5)
            main_menu()

def receive_input(counter):     # Receives valid user input for stocktake. Integer ! <0 and returns as item new_quantity.
    item_code = array_list[counter][0]
    global item_description
    item_description = array_list[counter][1]    # Assigns the currently select stocktake item descirption for display.
    valid_quantity = False
    while valid_quantity is False:      # Loops until the user enters a valid keyboard entry for the currently selected item.
        try:
            change_message(item_description)    # Displays the current item description to be changed.
            new_quantity = int(keypad_input())  # Calls Keypad input to detect a valid new quantity
            if new_quantity < 0:                # Validates new quantity ! < 0
                print('You have entered an invalid quantity!')
                time.sleep(1.5)
            else:
                valid_quantity = True
                print('Thank You!')     # Valid entry feedback.
                time.sleep(1)
        except ValueError:  # # Traps non integer keypad entry.
            print('You have made an invalid entry. Please enter an integer quantity!')
            time.sleep(2)
            os.system('clear')
    return new_quantity


def change_message(item_description):   # Menu for stocktake function.
    os.system('clear')
    print('You are currently at stock adjustment.\n')
    print('Press the * symbol on the keypad at any time to return to the main menu.')
    print('Press the # symbol after entering the correct quantity for your product.')
    print('Please enter the new quantity for item:\t ' + item_description + ' :')   # Display item presented for change.


def keypad_input():     # Receive keypad input during stocktake. # Enter, * main menu D delete character
    keypad_string = ''
    instance_keypad = keypad()  # Create a keypad object for user input via matrixKeyboard
    while True:
        time.sleep(.15)
        append_character = instance_keypad.getKey() # Check for a keypad entry
        if append_character is not None:    # Only accept keypad value if something has been entered
            if append_character == '#':     # Use hash key as 'Enter'
                return keypad_string        # Return value of keypad_string to stocktake
            elif append_character == 'D' and len(keypad_string) > 0:    # Delete keypad string length if > 0 chars.
                keypad_string = keypad_string[:-1]
                change_message(item_description)
                print(keypad_string)
            elif append_character == '*':   # Asterisk entered, return to main menu
                time.sleep(.5)
                main_menu()
            elif append_character != 'D':   # Append keypad string with keypad character selected.
                keypad_string = keypad_string + str(append_character)
                change_message(item_description)
                print(keypad_string)        # Display the keypad string for new quantity.


def path_handler():     # Determines if the remote / wireless storage path is mounted or if local database file is to be used.
    remote_path = '/home/pi/nas1/'
    local_path = './'
    remote_path_status = path_check(remote_path)    # Check if remote / wireless path is mounted.
    remote_file_check = file_check(remote_path, database_file)  # Check if remote database file is found.
    local_file_check = file_check(local_path, database_file)    # Check if local database file is found.
    os.system('clear')
    print('Checking filesystem...')
    if remote_path_status is True:      # User path feedback.
        print('The remote storage location is available.')
        if remote_file_check is True:   # User remote file feedback.
            print('The database file stored on the remote location has been found.')
            time.sleep(5)
            return remote_path      # sets the remote path as the working path
        else:
            print('The database file stored on the remote location has not been found.')
            print('The database file on the device will be checked...')
    else:
        print('The remote / wireless path for the database file is not available....')
        print('The database file on the device file will be checked...')
        if local_file_check is True:    # Check if there is a copy of the database file on the device.
            print('The database file on the device has been found.')
            time.sleep(5)
            return local_path       # Sets the local path as the working path
        else:       # If no database file is found. Exit.
            print('The database file can not be found remotely or locally.')
            print('Can not continue!')
            sys.exit()


def path_check(remote_path):    # Check if remote path is mounted.
    return os.path.ismount(remote_path)


def file_check(working_path, database_file):    # Check if remote / local file exists.
    return os.path.isfile(working_path + database_file)


def write_list(working_path, database_file):    # Write the list/array to file. Signal success / failure via LED.
    try:
        with open(working_path + database_file, 'w', encoding='UTF-8') as database_object:  # Open file write list as CSV.
            record_writer = csv.writer(database_object)
            for line in array_list:
                record_writer.writerow(line)
            print('Your records have successfully been written to file.')
            database_object.close()
            led_signal('green')     # Write success = green LED
            time.sleep(2)
    except Exception as err:
        print(err)
        print('An error writing records to ' + working_path + ' file has occurred.')
        led_signal('red')   # Write failure = red LED
        print('Returning to the main menu.')
        time.sleep(5)
        main_menu()


def led_signal(chosen_led):     # Configure GPIO & LEDS for output, Light LED as required.
    on_duration = 5
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    if chosen_led == 'green':
        chosen_led = GREEN_LED_PIN
    else:
        chosen_led = RED_LED_PIN
    GPIO.output(chosen_led, GPIO.HIGH)
    time.sleep(on_duration)
    GPIO.output(chosen_led, GPIO.LOW)


def exit_program():     # Clean exit
    os.system('clear')
    sys.exit('You have chosen to leave the program. Goodbye.')

#   start program

try:
    working_path = path_handler()   # Call to determine local or remote path
    read_list(working_path, database_file)  # Read database CSV to list array
    main_menu()                     # Call menu - 
except Exception as err:            # display unforeseen errors for debug
    print(err)

#   End

