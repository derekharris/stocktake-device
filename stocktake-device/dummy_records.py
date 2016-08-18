#!/usr/bin/env python3

# Create dummy records for the Wood Stocks product database.
import random   # Random num genertaor
import time     # Time functions
import os       # Underlying OS functions
import csv      # Handle csv r/w

list_length = 10     # Number of records to be created for database csv
                     # Modify as required for dummy database.

def create_list():      # Create dummy Python list as an item array.
    for record in range(1, list_length + 1):
        uid = str(record).zfill(4)  # Zero fill records to maintain data format
        item_code = ('A' + uid)     # Prepend item code with A
        item_description = ('<Description of product item ' + item_code + '>')  # Generate dummy description
        current_count = random.randint(0, 99)    # Generate randon item start quantity
        on_order = 'No'     # Set 'On order status' to no
        record_string = [item_code, item_description, current_count, on_order]  # create appendable string
        record_list.append(record_string)   # create list


def print_list():   # Visual feedback after completion
    for item in record_list:
        print(item)


def write_list():   # Write list to database file in CSV format
    with open(database_file, 'w', encoding='UTF-8') as database_object:
        record_writer = csv.writer(database_object)
        for line in record_list:
            record_writer.writerow(line)


def read_list():    # Read list to prove valid write
    array_list = []
    with open(database_file, 'r') as database_object:
        record_reader = csv.reader(database_object)
        for line in record_reader:
            print(line)
            array_list.append(line)


# prgram start
global record_list
record_list = []
global database_file
database_file = 'ws_product_database.csv'

# call functions
print('Creating initial list:')
create_list()
print('Displaying initial list:')
print_list()
print('Writing initial list:')
write_list()
print('List written')
print('Read and display written list per line:')
read_list()
print('Display written list as array:')
print(record_list)
# end
