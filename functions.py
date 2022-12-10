from queue import PriorityQueue
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import tkinter as tk
import csv
from datetime import datetime


def call_counter():
    with open('Assets/counters.txt', 'r') as file:
        counters = file.readlines()
        file.close()
    new_num = int(counters[1]) + 1
    counters[1] = str(new_num)+'\n'

    with open('Assets/counters.txt', 'w') as file:
        file.writelines(counters)
        file.close()
    return new_num


def customer_counter():
    with open('Assets/counters.txt', 'r') as file:
        counters = file.readlines()
        file.close()
    new_num = int(counters[4]) + 1
    counters[4] = str(new_num)+'\n'

    with open('Assets/counters.txt', 'w') as file:
        file.writelines(counters)
        file.close()
    return new_num


def save_customer_csv(name, company, street, city, state, add_zip, phone, email):
    customer = [customer_counter(), name, company, street, city, state, add_zip, phone, email]
    with open('Data/customers.csv', 'a', newline='') as customers_file:
        writer = csv.writer(customers_file)
        writer.writerow(customer)
    customers_file.close

def save_call_csv(customer,issue,category,priority):
    dt = datetime.now()
    timestamp = dt.replace(microsecond=0)
    call = [call_counter(),customer,timestamp,'','',issue,category,priority,'Queued','']
    with open('Data/calls.csv', 'a', newline='') as calls_file:
        writer = csv.writer(calls_file)
        writer.writerow(call)
    calls_file.close
