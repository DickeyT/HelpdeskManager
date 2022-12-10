import tkinter as tk
from tkinter import ttk, Menu
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import pandas as pd
import datetime
from queue import PriorityQueue
import functions


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Helpdesk Manager")
        self.iconbitmap("Assets/helpdesk-icon.ico")
        self.geometry("1080x720+10+10")

        self.menubar = Menu(self)
        self.config(menu=self.menubar)

        self.file_menu = Menu(self.menubar, tearoff=False)
        self.call_menu = Menu(self.menubar, tearoff=False)
        self.help_menu = Menu(self.menubar, tearoff=False)

    # File Menu
        self.menubar.add_cascade(
            label='File',
            menu=self.file_menu
        )
        self.file_menu.add_command(
            label='Exit',
            command=self.destroy
        )

    # Call Menu
        self.menubar.add_cascade(
            label='Calls',
            menu=self.call_menu
        )
        self.call_menu.add_command(
            label='New Call',
            command=lambda: self.show_frame(NewCall)
        )
        self.call_menu.add_command(
            label='Calls',
            command=lambda: self.show_frame(CallsPage)
        )
        self.call_menu.add_separator()
        self.call_menu.add_command(
            label='Call Queue',
            command=lambda: self.show_frame(CallQueue)
        )
        self.call_menu.add_separator()

        self.call_menu.add_command(
            label='Customers',
            command=lambda: self.show_frame(Customers)
        )
        self.call_menu.add_command(
            label='Add Customer',
            command=lambda: self.show_frame(NewCustomer)
        )

        self.menubar.add_cascade(
            label='Help',
            menu=self.help_menu
        )
        self.help_menu.add_command(
            label='About...',
            command=lambda: showinfo(
                title='About Helpdesk Manager',
                message='This program is an educational final project for CIS152\n'
                        'These are not real helpdesk calls or customers\n\n'
                        'Version 1.0.0\n'
                        'Released: 12/09/2022\n\n'
                        'Coded by Trevor Dickey'
            )
        )

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, NewCall, CallsPage, CallQueue, Customers, NewCustomer):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.update()
        frame.event_generate("<<ShowFrame>>")


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=720, width=1080, background="white")

        self.photo = ImageTk.PhotoImage(Image.open("Assets/splash_logo.png"))
        self.img_label = ttk.Label(self, image=self.photo)

        self.img_label.place(relx=0.5, rely=0.5, anchor="center")


class NewCall(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=720, width=1080, background="gray")
        self.categories = ['Hardware', 'Network', 'Peripherals', 'Credentials', 'Drivers', 'Software']
        self.priorities = {1: "Critical",
                           2: "High",
                           3: "Medium High",
                           4: "Medium",
                           5: "Medium Low",
                           6: "Low"}
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, minsize=150)
        self.columnconfigure(2, minsize=150)
        self.columnconfigure(10, minsize=10)
        self.columnconfigure(11, minsize=150)
        self.columnconfigure(12, minsize=150)
        self.columnconfigure(13, minsize=150)
        self.bind('<<ShowFrame>>', self.onShowFrame)
        self.load_customers()
        self.load_calls()

        # category entry
        selected_category = tk.StringVar()
        self.category_menu = ttk.Combobox(self, textvariable=selected_category, state='readonly')
        self.category_menu['values'] = self.categories
        self.category_menu.current()
        self.category_menu.config(justify='center')

        self.category_label = tk.Label(self, text="Category")
        self.category_label.config(bg='black', fg='white')
        self.category_label.grid(row=0, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))

        self.category_menu.grid(row=1, column=1, sticky='ew', padx=(2, 2))

        # Priority entry
        selected_priority = tk.StringVar()
        self.priority_menu = ttk.Combobox(self, textvariable=selected_priority, state='readonly')
        self.priority_menu['values'] = list(self.priorities.values())
        self.priority_menu.current()
        self.priority_menu.config(justify='center')

        self.priority_label = tk.Label(self, text="Priority")
        self.priority_label.config(bg='black', fg='white')
        self.priority_label.grid(row=0, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.priority_menu.grid(row=1, column=2, sticky='ew', padx=(2, 5))

        # issue entry
        self.issue_label = tk.Label(self, text="Issue")
        self.issue_label.config(bg='black', fg='white')
        self.issue_label.grid(row=2, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.issue_entry = ScrolledText(self, width=3, height=5)
        self.issue_entry.grid(row=3, column=0, columnspan=3, rowspan=5, sticky='nesw', padx=(5, 5))

        # buttons
        clear_button = ttk.Button(self, text="Clear", command=lambda: self.clear_call())
        clear_button.grid(row=8, column=0, padx=(5, 2), pady=(5, 0), sticky='ew')
        submit_button = ttk.Button(self, text="Enter Call", command=lambda: self.save_call())
        submit_button.grid(row=8, column=1, columnspan=2, padx=(2, 5), pady=(5, 0), sticky='ew')


        selected_cust = tk.StringVar()
        self.customer_menu = ttk.Combobox(self, textvariable=selected_cust, state='readonly')
        self.customer_menu['values'] = self.generate_customer_list()
        self.customer_menu.current()
        self.customer_menu.config(justify='center')

        self.select_label = tk.Label(self, text="Please Select a Customer")
        self.select_label.config(bg='black', fg='white')
        self.select_label.grid(row=0, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))

        self.customer_menu.grid(row=1, column=11, columnspan=3, sticky='ew', padx=(5, 5))
        self.customer_menu.bind('<<ComboboxSelected>>', self.customer_changed)

        # company entry
        self.company_label = tk.Label(self, text="Company")
        self.company_label.config(bg='black', fg='white')
        self.company_label.grid(row=2, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.company_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.company_entry.grid(row=3, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # street entry
        self.street_label = tk.Label(self, text="Street")
        self.street_label.config(bg='black', fg='white')
        self.street_label.grid(row=4, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.street_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.street_entry.grid(row=5, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # city entry
        self.city_label = tk.Label(self, text="City")
        self.city_label.config(bg='black', fg='white')
        self.city_label.grid(row=6, column=11, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.city_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.city_entry.grid(row=7, column=11, sticky='ew', padx=(5, 2))

        # state entry
        self.state_label = tk.Label(self, text="State")
        self.state_label.config(bg='black', fg='white')
        self.state_label.grid(row=6, column=12, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.state_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.state_entry.grid(row=7, column=12, sticky='ew', padx=(2, 2))

        # zip entry
        self.zip_label = tk.Label(self, text="Zip Code")
        self.zip_label.config(bg='black', fg='white')
        self.zip_label.grid(row=6, column=13, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.zip_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.zip_entry.grid(row=7, column=13, sticky='ew', padx=(2, 5))

        # phone entry
        self.phone_label = tk.Label(self, text="Phone")
        self.phone_label.config(bg='black', fg='white')
        self.phone_label.grid(row=8, column=11, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.phone_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.phone_entry.grid(row=9, column=11, sticky='ew', padx=(5, 2))

        # email entry
        self.email_label = tk.Label(self, text="E-mail")
        self.email_label.config(bg='black', fg='white')
        self.email_label.grid(row=8, column=12, columnspan=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.email_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.email_entry.grid(row=9, column=12, columnspan=2, sticky='ew', padx=(2, 5))

        # hidden required tag
        self.required_tag = tk.Label(self, text='Category, Priority, Issue and Customer are required!')
        self.required_tag.config(fg='red')


    def customer_changed(self, event):
        self.name_num = dict(zip(self.customer_data.cust_name, self.customer_data.index))
        self.key = self.customer_menu.get()
        self.row_index = int(self.name_num[self.key])
        self.enable_fields()
        self.clear_fields()
        self.company_entry.insert(0, self.customer_data.at[self.row_index, 'cust_company'])
        self.street_entry.insert(0, self.customer_data.at[self.row_index, 'cust_street'])
        self.city_entry.insert(0, self.customer_data.at[self.row_index, 'cust_city'])
        self.state_entry.insert(0, self.customer_data.at[self.row_index, 'cust_state'])
        self.zip_entry.insert(0, self.customer_data.at[self.row_index, 'cust_zip'])
        self.phone_entry.insert(0, self.customer_data.at[self.row_index, 'cust_phone'])
        self.email_entry.insert(0, self.customer_data.at[self.row_index, 'cust_email'])
        self.disable_fields()

    def enable_fields(self):
        self.company_entry.configure(state='normal')
        self.street_entry.configure(state='normal')
        self.city_entry.configure(state='normal')
        self.state_entry.configure(state='normal')
        self.zip_entry.configure(state='normal')
        self.phone_entry.configure(state='normal')
        self.email_entry.configure(state='normal')

    def disable_fields(self):
        # self.name_entry.configure(state='disabled')
        self.company_entry.configure(state='disabled')
        self.street_entry.configure(state='disabled')
        self.city_entry.configure(state='disabled')
        self.state_entry.configure(state='disabled')
        self.zip_entry.configure(state='disabled')
        self.phone_entry.configure(state='disabled')
        self.email_entry.configure(state='disabled')

    def clear_call(self):
        self.enable_fields()
        self.customer_menu.set('')
        self.clear_fields()
        self.disable_fields()
        self.category_menu.set('')
        self.priority_menu.set('')
        self.issue_entry.delete('1.0', 'end')
        self.required_tag.destroy()

    def save_call(self):
        category_text = self.category_menu.get()
        priority_text = self.priority_menu.get()
        issue_text = self.issue_entry.get('1.0', tk.END)
        customer_text = self.category_menu.get()
        if category_text == "" or \
                priority_text == "" or \
                issue_text == "" or\
                customer_text == "":
            self.required_missing()
        else:
            self.clear_call()
            self.required_tag.destroy()
            if priority_text == "Critical":
                priority = 1
            elif priority_text == "Critical":
                priority = 2
            elif priority_text == "High":
                priority = 3
            elif priority_text == "Medium High":
                priority = 4
            elif priority_text == "Medium":
                priority = 5
            elif priority_text == "Medium Low":
                priority = 6
            else:
                priority = 7
            functions.save_call_csv(self.row_index, issue_text, category_text, priority)

    def required_missing(self):
        # hidden required tag
        self.required_tag = tk.Label(self, text='Category, Priority, Issue and Customer are required!')
        self.required_tag.config(fg='red')
        self.required_tag.grid(row=10, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))

    def clear_fields(self):
        self.category_menu.delete(0, 'end')
        self.priority_menu.delete(0, 'end')
        self.issue_entry.delete("1.0", 'end')
        self.customer_menu.delete(0, 'end')
        self.company_entry.delete(0, 'end')
        self.street_entry.delete(0, 'end')
        self.city_entry.delete(0, 'end')
        self.state_entry.delete(0, 'end')
        self.zip_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')

    def generate_customer_list(self):
        return self.customer_data['cust_name'].to_list()

    def load_customers(self):
        data = pd.read_csv('Data/customers.csv', dtype={"cust_zip": object})
        data.fillna('', inplace=True)
        self.customer_data = pd.DataFrame(data)
        self.customer_data = self.customer_data.set_index('cust_num')

    def load_calls(self):
        data = pd.read_csv('Data/calls.csv')
        data.fillna('', inplace=True)
        self.call_data = pd.DataFrame(data)
        self.call_data = self.call_data.set_index('call_num')

    def onShowFrame(self, event):
        self.update()
        self.load_customers()
        self.customer_menu['values'] = self.generate_customer_list()


class CallsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.priority_menu = None
        self.category_menu = None
        self.customer_menu = None
        self.configure(height=720, width=1080, background="gray")
        self.categories = ['Hardware', 'Network', 'Peripherals', 'Credentials', 'Drivers', 'Software']
        self.priorities = {1: "Critical",
                           2: "High",
                           3: "Medium High",
                           4: "Medium",
                           5: "Medium Low",
                           6: "Low"}
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, minsize=150)
        self.columnconfigure(2, minsize=150)
        self.columnconfigure(10, minsize=10)
        self.columnconfigure(11, minsize=150)
        self.columnconfigure(12, minsize=150)
        self.columnconfigure(13, minsize=150)
        self.bind('<<ShowFrame>>', self.onShowFrame)
        self.load_customers()
        self.load_calls()

        # Call number
        selected_call_num = tk.StringVar()
        self.call_num_label = tk.Label(self, text="Call Number")
        self.call_num_label.config(bg='black', fg='white')
        self.call_num_label.grid(row=0, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.call_num_menu = ttk.Combobox(self, textvariable=selected_call_num, state='readonly')
        self.call_num_menu['values'] = self.generate_call_list()
        self.call_num_menu.current()
        self.call_num_menu.config(justify='center')
        self.call_num_menu.grid(row=1, column=0, sticky='ew', padx=(5, 2))
        self.call_num_menu.bind('<<ComboboxSelected>>', self.call_changed)

        # category entry
        self.category_label = tk.Label(self, text="Category")
        self.category_label.config(bg='black', fg='white')
        self.category_label.grid(row=0, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))

        self.category_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.category_entry.grid(row=1, column=1, sticky='ew', padx=(2, 2))

        # Priority entry
        self.priority_label = tk.Label(self, text="Priority")
        self.priority_label.config(bg='black', fg='white')
        self.priority_label.grid(row=0, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.priority_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.priority_entry.grid(row=1, column=2, sticky='ew', padx=(2, 5))

        # Call time
        self.call_time_label = tk.Label(self, text="Call Time")
        self.call_time_label.config(bg='black', fg='white')
        self.call_time_label.grid(row=2, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.call_time_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.call_time_entry.grid(row=3, column=0, sticky='ew', padx=(5, 2))

        # call start entry
        self.call_start_label = tk.Label(self, text="Call Start")
        self.call_start_label.config(bg='black', fg='white')
        self.call_start_label.grid(row=2, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.call_start_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.call_start_entry.grid(row=3, column=1, sticky='ew', padx=(2, 2))

        # call end entry
        self.call_end_label = tk.Label(self, text="Call End")
        self.call_end_label.config(bg='black', fg='white')
        self.call_end_label.grid(row=2, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.call_end_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.call_end_entry.grid(row=3, column=2, sticky='ew', padx=(2, 5))

        # issue entry
        self.issue_label = tk.Label(self, text="Issue")
        self.issue_label.config(bg='black', fg='white')
        self.issue_label.grid(row=4, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.issue_entry = ScrolledText(self, width=3, height=5)
        self.issue_entry.grid(row=5, column=0, columnspan=3, rowspan=5, sticky='nesw', padx=(5, 5))

        # customer entry
        self.select_label = tk.Label(self, text="Customer")
        self.select_label.config(bg='black', fg='white')
        self.select_label.grid(row=0, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.customer_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.customer_entry.grid(row=1, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # company entry
        self.company_label = tk.Label(self, text="Company")
        self.company_label.config(bg='black', fg='white')
        self.company_label.grid(row=2, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.company_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.company_entry.grid(row=3, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # street entry
        self.street_label = tk.Label(self, text="Street")
        self.street_label.config(bg='black', fg='white')
        self.street_label.grid(row=4, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.street_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.street_entry.grid(row=5, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # city entry
        self.city_label = tk.Label(self, text="City")
        self.city_label.config(bg='black', fg='white')
        self.city_label.grid(row=6, column=11, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.city_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.city_entry.grid(row=7, column=11, sticky='ew', padx=(5, 2))

        # state entry
        self.state_label = tk.Label(self, text="State")
        self.state_label.config(bg='black', fg='white')
        self.state_label.grid(row=6, column=12, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.state_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.state_entry.grid(row=7, column=12, sticky='ew', padx=(2, 2))

        # zip entry
        self.zip_label = tk.Label(self, text="Zip Code")
        self.zip_label.config(bg='black', fg='white')
        self.zip_label.grid(row=6, column=13, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.zip_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.zip_entry.grid(row=7, column=13, sticky='ew', padx=(2, 5))

        # phone entry
        self.phone_label = tk.Label(self, text="Phone")
        self.phone_label.config(bg='black', fg='white')
        self.phone_label.grid(row=8, column=11, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.phone_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.phone_entry.grid(row=9, column=11, sticky='ew', padx=(5, 2))

        # email entry
        self.email_label = tk.Label(self, text="E-mail")
        self.email_label.config(bg='black', fg='white')
        self.email_label.grid(row=8, column=12, columnspan=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.email_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.email_entry.grid(row=9, column=12, columnspan=2, sticky='ew', padx=(2, 5))

        # note entry
        self.note_label = tk.Label(self, text="Notes")
        self.note_label.config(bg='black', fg='white')
        self.note_label.grid(row=10, column=0, columnspan=14, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.note_entry = ScrolledText(self, width=14, height=5)
        self.note_entry.grid(row=11, column=0, columnspan=14, rowspan=5, sticky='nesw', padx=(5, 5))


    def customer_changed(self, event):
        self.name_num = dict(zip(self.customer_data.cust_name, self.customer_data.index))
        self.key = self.customer_menu.get()
        self.row_index = int(self.name_num[self.key])
        self.enable_fields()
        self.clear_fields()
        self.company_entry.insert(0, self.customer_data.at[self.row_index, 'cust_company'])
        self.street_entry.insert(0, self.customer_data.at[self.row_index, 'cust_street'])
        self.city_entry.insert(0, self.customer_data.at[self.row_index, 'cust_city'])
        self.state_entry.insert(0, self.customer_data.at[self.row_index, 'cust_state'])
        self.zip_entry.insert(0, self.customer_data.at[self.row_index, 'cust_zip'])
        self.phone_entry.insert(0, self.customer_data.at[self.row_index, 'cust_phone'])
        self.email_entry.insert(0, self.customer_data.at[self.row_index, 'cust_email'])
        self.disable_fields()

    def call_changed(self, event):
        self.row_index = int(self.call_num_menu.get())
        self.cust_index = self.call_data.at[self.row_index, 'customer']
        self.enable_fields()
        self.clear_fields()
        self.category_entry.insert(0, self.call_data.at[self.row_index, 'category'])
        self.priority_entry.insert(0, self.priorities[self.call_data.at[self.row_index, 'priority']])
        self.call_time_entry.insert(0, self.call_data.at[self.row_index, 'call_time'])
        self.call_start_entry.insert(0, self.call_data.at[self.row_index, 'call_start'])
        self.call_end_entry.insert(0, self.call_data.at[self.row_index, 'call_end'])
        self.issue_entry.insert("1.0", self.call_data.at[self.row_index, 'issue'])
        self.note_entry.insert("1.0", self.call_data.at[self.row_index, 'notes'])
        self.customer_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_name'])
        self.company_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_company'])
        self.street_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_street'])
        self.city_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_city'])
        self.state_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_state'])
        self.zip_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_zip'])
        self.phone_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_phone'])
        self.email_entry.insert(0, self.customer_data.at[self.cust_index, 'cust_email'])
        self.disable_fields()

    def enable_fields(self):
        self.company_entry.configure(state='normal')
        self.street_entry.configure(state='normal')
        self.city_entry.configure(state='normal')
        self.state_entry.configure(state='normal')
        self.zip_entry.configure(state='normal')
        self.phone_entry.configure(state='normal')
        self.email_entry.configure(state='normal')

    def disable_fields(self):
        # self.name_entry.configure(state='disabled')
        self.company_entry.configure(state='disabled')
        self.street_entry.configure(state='disabled')
        self.city_entry.configure(state='disabled')
        self.state_entry.configure(state='disabled')
        self.zip_entry.configure(state='disabled')
        self.phone_entry.configure(state='disabled')
        self.email_entry.configure(state='disabled')

    def clear_call(self):
        self.enable_fields()
        self.customer_menu.set('')
        self.clear_fields()
        self.disable_fields()
        self.category_menu.set('')
        self.priority_menu.set('')
        self.issue_entry.delete('1.0', 'end')
        self.required_tag.destroy()

    def save_call(self):
        category_text = self.category_menu.get()
        priority_text = self.priority_menu.get()
        issue_text = self.issue_entry.get('1.0', tk.END)
        customer_text = self.category_menu.get()
        self.cust_index = self.call_data.at[self.row_index, 'customer']
        if category_text == "" or \
                priority_text == "" or \
                issue_text == "" or\
                customer_text == "":
            self.required_missing()


    def required_missing(self):
        # hidden required tag
        self.required_tag = tk.Label(self, text='Category, Priority, Issue and Customer are required!')
        self.required_tag.config(fg='red')
        self.required_tag.grid(row=10, column=0, columnspan=3, sticky='ew', padx=(5,5), pady=(5,0))


    def clear_fields(self):
        self.category_entry.delete(0, 'end')
        self.priority_entry.delete(0, 'end')
        self.call_time_entry.delete(0, 'end')
        self.call_start_entry.delete(0, 'end')
        self.call_end_entry.delete(0, 'end')
        self.issue_entry.delete("1.0", 'end')
        self.note_entry.delete('1.0', 'end')
        self.customer_entry.delete(0, 'end')
        self.company_entry.delete(0, 'end')
        self.street_entry.delete(0, 'end')
        self.city_entry.delete(0, 'end')
        self.state_entry.delete(0, 'end')
        self.zip_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')

    def generate_call_list(self):
        return self.call_data.index.to_list()

    def load_customers(self):
        data = pd.read_csv('Data/customers.csv', dtype={"cust_zip": object})
        data.fillna('', inplace=True)
        self.customer_data = pd.DataFrame(data)
        self.customer_data = self.customer_data.set_index('cust_num')

    def load_calls(self):
        data = pd.read_csv('Data/calls.csv')
        data.fillna('', inplace=True)
        self.call_data = pd.DataFrame(data)
        self.call_data = self.call_data.set_index('call_num')
        pd.to_datetime(self.call_data['call_start'])

    def onShowFrame(self, event):
        self.update()
        self.load_customers()
        self.load_calls()
        self.call_num_menu['values'] = self.generate_call_list()

class Customers(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=720, width=1080, background="white")
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, minsize=150)
        self.columnconfigure(2, minsize=150)
        self.bind('<<ShowFrame>>', self.onShowFrame)
        self.load_customers()
        self.fields = ['cust_company','cust_street','cust_city','cust_state','cust_zip','cust_phone','cust_email']

        selected_cust = tk.StringVar()
        self.customer_menu = ttk.Combobox(self,textvariable=selected_cust, state='readonly')
        self.customer_menu['values'] = self.generate_customer_list()
        self.customer_menu.current()
        self.customer_menu.config(justify='center')

        self.select_label = tk.Label(self, text="Please Select a Customer")
        self.select_label.config(bg='black', fg='white')
        self.select_label.grid(row=0, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))

        self.customer_menu.grid(row=1, column=0, columnspan=3, sticky='ew', padx=(5, 5))
        self.customer_menu.bind('<<ComboboxSelected>>', self.customer_changed)

        # company entry
        self.company_label = tk.Label(self, text="Company")
        self.company_label.config(bg='black', fg='white')
        self.company_label.grid(row=4, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.company_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.company_entry.grid(row=5, column=0, columnspan=3, sticky='ew', padx=(5, 5))

        # street entry
        self.street_label = tk.Label(self, text="Street")
        self.street_label.config(bg='black', fg='white')
        self.street_label.grid(row=6, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.street_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.street_entry.grid(row=7, column=0, columnspan=3, sticky='ew', padx=(5, 5))

        # city entry
        self.city_label = tk.Label(self, text="City")
        self.city_label.config(bg='black', fg='white')
        self.city_label.grid(row=8, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.city_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.city_entry.grid(row=9, column=0, sticky='ew', padx=(5, 2))

        # state entry
        self.state_label = tk.Label(self, text="State")
        self.state_label.config(bg='black', fg='white')
        self.state_label.grid(row=8, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.state_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.state_entry.grid(row=9, column=1, sticky='ew', padx=(2, 2))

        # zip entry
        self.zip_label = tk.Label(self, text="Zip Code")
        self.zip_label.config(bg='black', fg='white')
        self.zip_label.grid(row=8, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.zip_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.zip_entry.grid(row=9, column=2, sticky='ew', padx=(2, 5))

        # phone entry
        self.phone_label = tk.Label(self, text="Phone")
        self.phone_label.config(bg='black', fg='white')
        self.phone_label.grid(row=10, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.phone_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.phone_entry.grid(row=11, column=0, sticky='ew', padx=(5, 2))

        # email entry
        self.email_label = tk.Label(self, text="E-mail")
        self.email_label.config(bg='black', fg='white')
        self.email_label.grid(row=10, column=1, columnspan=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.email_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.email_entry.grid(row=11, column=1, columnspan=2, sticky='ew', padx=(2, 5))

        # buttons
        self.edit_button = ttk.Button(self, text="Edit Customer", command=lambda: self.edit_customer())
        self.edit_button.grid(row=12, column=0, padx=(5, 2), pady=(5, 0), sticky='ew')
        self.submit_button = ttk.Button(self, text="Save Customer", state='disabled', command=lambda: self.save_customer())
        self.submit_button.grid(row=12, column=1, columnspan=2, padx=(2, 5), pady=(5, 0), sticky='ew')

        # hidden required tag
        self.required_tag = tk.Label(self, text='Customer name and Phone are required!')
        self.required_tag.config(fg='red')

    def edit_customer(self):
        self.enable_fields()
        self.submit_button.config(state='normal')
        self.edit_button.config(state='disabled')
        self.name_label = tk.Label(self, text="Customer Name")
        self.name_label.config(bg='black', fg='white')
        self.name_label.grid(row=2, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.name_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.name_entry.grid(row=3, column=0, columnspan=3, sticky='ew', padx=(5, 5))
        self.name_entry.insert(0, self.customer_data.at[self.row_index, 'cust_name'])

    def save_customer(self):
        name_text = self.name_entry.get()
        company_text = self.company_entry.get()
        street_text = self.street_entry.get()
        city_text = self.city_entry.get()
        state_text = self.state_entry.get()
        zip_text = self.zip_entry.get()
        phone_text = self.phone_entry.get()
        email_text = self.email_entry.get()
        if name_text == "" or phone_text == "":
            self.required_missing()
        else:
            self.required_tag.destroy()
            self.customer_data.at[self.row_index, 'cust_name'] = name_text
            self.customer_data.at[self.row_index, 'cust_company'] = company_text
            self.customer_data.at[self.row_index, 'cust_street'] = street_text
            self.customer_data.at[self.row_index, 'cust_city'] = city_text
            self.customer_data.at[self.row_index, 'cust_state'] = state_text
            self.customer_data.at[self.row_index, 'cust_zip'] = zip_text
            self.customer_data.at[self.row_index, 'cust_phone'] = phone_text
            self.customer_data.at[self.row_index, 'cust_email'] = email_text
            self.customer_data.to_csv('Data/customers.csv')
            self.load_customers()
            self.customer_menu['values'] = self.generate_customer_list()
            self.customer_menu.set(name_text)
            self.disable_fields()
            self.name_label.destroy()
            self.name_entry.destroy()
            self.submit_button.config(state='disabled')
            self.edit_button.config(state='normal')

    def required_missing(self):
        # hidden required tag
        self.required_tag = tk.Label(self, text='Customer name and Phone are required!')
        self.required_tag.config(fg='red')
        self.required_tag.grid(row=13, column=0, columnspan=3, sticky='ew', padx=(5,5), pady=(5,0))

    def customer_changed(self, event):
        self.name_num = dict(zip(self.customer_data.cust_name, self.customer_data.index))
        self.key = self.customer_menu.get()
        self.row_index = int(self.name_num[self.key])
        self.enable_fields()
        self.clear_fields()
        self.company_entry.insert(0, self.customer_data.at[self.row_index, 'cust_company'])
        self.street_entry.insert(0, self.customer_data.at[self.row_index, 'cust_street'])
        self.city_entry.insert(0, self.customer_data.at[self.row_index, 'cust_city'])
        self.state_entry.insert(0, self.customer_data.at[self.row_index, 'cust_state'])
        self.zip_entry.insert(0, self.customer_data.at[self.row_index, 'cust_zip'])
        self.phone_entry.insert(0, self.customer_data.at[self.row_index, 'cust_phone'])
        self.email_entry.insert(0, self.customer_data.at[self.row_index, 'cust_email'])
        self.disable_fields()

    def clear_fields(self):
        # self.name_entry.delete(0, 'end')
        self.company_entry.delete(0, 'end')
        self.street_entry.delete(0, 'end')
        self.city_entry.delete(0, 'end')
        self.state_entry.delete(0, 'end')
        self.zip_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')

    def enable_fields(self):
        # self.name_entry.configure(state='normal')
        self.company_entry.configure(state='normal')
        self.street_entry.configure(state='normal')
        self.city_entry.configure(state='normal')
        self.state_entry.configure(state='normal')
        self.zip_entry.configure(state='normal')
        self.phone_entry.configure(state='normal')
        self.email_entry.configure(state='normal')

    def disable_fields(self):
        # self.name_entry.configure(state='disabled')
        self.company_entry.configure(state='disabled')
        self.street_entry.configure(state='disabled')
        self.city_entry.configure(state='disabled')
        self.state_entry.configure(state='disabled')
        self.zip_entry.configure(state='disabled')
        self.phone_entry.configure(state='disabled')
        self.email_entry.configure(state='disabled')

    def generate_customer_list(self):
        return self.customer_data['cust_name'].to_list()

    def load_customers(self):
        data = pd.read_csv('Data/customers.csv', dtype={"cust_zip": object})
        data.fillna('', inplace=True)
        self.customer_data = pd.DataFrame(data)
        self.customer_data = self.customer_data.set_index('cust_num')

    def onShowFrame(self, event):
        self.update()
        self.load_customers()
        self.customer_menu['values'] = self.generate_customer_list()

class CallQueue(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=720, width=1080, background="gray")
        self.priorities = {1: "Critical",
                           2: "High",
                           3: "Medium High",
                           4: "Medium",
                           5: "Medium Low",
                           6: "Low"}
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, minsize=150)
        self.columnconfigure(2, minsize=150)
        self.columnconfigure(10, minsize=10)
        self.columnconfigure(11, minsize=150)
        self.columnconfigure(12, minsize=150)
        self.columnconfigure(13, minsize=150)
        self.columnconfigure(14, minsize=150)
        self.bind('<<ShowFrame>>', self.onShowFrame)
        self.load_customers()
        self.load_calls()

        # Call number
        selected_call_num = tk.StringVar()
        self.call_num_label = tk.Label(self, text="Call Number")
        self.call_num_label.config(bg='black', fg='white')
        self.call_num_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.call_num_label.grid(row=0, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.call_num_entry.grid(row=1, column=0, sticky='ew', padx=(5, 2))

        # category entry
        self.category_label = tk.Label(self, text="Category")
        self.category_label.config(bg='black', fg='white')
        self.category_label.grid(row=0, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))

        self.category_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.category_entry.grid(row=1, column=1, sticky='ew', padx=(2, 2))

        # Priority entry
        self.priority_label = tk.Label(self, text="Priority")
        self.priority_label.config(bg='black', fg='white')
        self.priority_label.grid(row=0, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.priority_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.priority_entry.grid(row=1, column=2, sticky='ew', padx=(2, 5))

        # Call time
        self.call_time_label = tk.Label(self, text="Call Time")
        self.call_time_label.config(bg='black', fg='white')
        self.call_time_label.grid(row=2, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.call_time_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.call_time_entry.grid(row=3, column=0, sticky='ew', padx=(5, 2))

        # call start entry
        self.call_start_label = tk.Label(self, text="Call Start")
        self.call_start_label.config(bg='black', fg='white')
        self.call_start_label.grid(row=2, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.call_start_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.call_start_entry.grid(row=3, column=1, sticky='ew', padx=(2, 2))

        # call end entry
        self.call_end_label = tk.Label(self, text="Call End")
        self.call_end_label.config(bg='black', fg='white')
        self.call_end_label.grid(row=2, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.call_end_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.call_end_entry.grid(row=3, column=2, sticky='ew', padx=(2, 5))

        # issue entry
        self.issue_label = tk.Label(self, text="Issue")
        self.issue_label.config(bg='black', fg='white')
        self.issue_label.grid(row=4, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.issue_entry = ScrolledText(self, width=3, height=5)
        self.issue_entry.grid(row=5, column=0, columnspan=3, rowspan=5, sticky='nesw', padx=(5, 5))

        # customer entry
        self.select_label = tk.Label(self, text="Customer")
        self.select_label.config(bg='black', fg='white')
        self.select_label.grid(row=0, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.customer_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.customer_entry.grid(row=1, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # company entry
        self.company_label = tk.Label(self, text="Company")
        self.company_label.config(bg='black', fg='white')
        self.company_label.grid(row=2, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.company_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.company_entry.grid(row=3, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # street entry
        self.street_label = tk.Label(self, text="Street")
        self.street_label.config(bg='black', fg='white')
        self.street_label.grid(row=4, column=11, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.street_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.street_entry.grid(row=5, column=11, columnspan=3, sticky='ew', padx=(5, 5))

        # city entry
        self.city_label = tk.Label(self, text="City")
        self.city_label.config(bg='black', fg='white')
        self.city_label.grid(row=6, column=11, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.city_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.city_entry.grid(row=7, column=11, sticky='ew', padx=(5, 2))

        # state entry
        self.state_label = tk.Label(self, text="State")
        self.state_label.config(bg='black', fg='white')
        self.state_label.grid(row=6, column=12, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.state_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.state_entry.grid(row=7, column=12, sticky='ew', padx=(2, 2))

        # zip entry
        self.zip_label = tk.Label(self, text="Zip Code")
        self.zip_label.config(bg='black', fg='white')
        self.zip_label.grid(row=6, column=13, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.zip_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.zip_entry.grid(row=7, column=13, sticky='ew', padx=(2, 5))

        # phone entry
        self.phone_label = tk.Label(self, text="Phone")
        self.phone_label.config(bg='black', fg='white')
        self.phone_label.grid(row=8, column=11, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.phone_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.phone_entry.grid(row=9, column=11, sticky='ew', padx=(5, 2))

        # email entry
        self.email_label = tk.Label(self, text="E-mail")
        self.email_label.config(bg='black', fg='white')
        self.email_label.grid(row=8, column=12, columnspan=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.email_entry = tk.Entry(self, disabledforeground='black', justify='center', state='disabled')
        self.email_entry.grid(row=9, column=12, columnspan=2, sticky='ew', padx=(2, 5))

        # note entry
        self.note_label = tk.Label(self, text="Notes")
        self.note_label.config(bg='black', fg='white')
        self.note_label.grid(row=10, column=0, columnspan=14, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.note_entry = ScrolledText(self, width=14, height=5)
        self.note_entry.grid(row=11, column=0, columnspan=14, rowspan=5, sticky='nesw', padx=(5, 5))

        # buttons
        self.call_start_button = ttk.Button(self, text="Call Start Time", command=lambda: self.timestamp_start())
        self.call_start_button.grid(row=16, column=0, padx=(5, 2), pady=(5, 0), sticky='ew')
        self.call_end_button = ttk.Button(self, text="Call End Time", command=lambda: self.timestamp_end())
        self.call_end_button.grid(row=16, column=1, padx=(2, 2), pady=(5, 0), sticky='ew')
        self.close_call_button = ttk.Button(self, text="Close Call", command=lambda: self.close_call())
        self.close_call_button.grid(row=16, column=2, columnspan=10, padx=(2,2), pady=(5,0), stick='ew')
        self.call_hold_button = ttk.Button(self, text="Hold Call", command=lambda: self.hold_call())
        self.call_hold_button.grid(row=16, column=12, padx=(2, 2), pady=(5, 0), sticky='ew')

        self.next_priority_call_button = ttk.Button(self, text="Next Priority Call",
                                                    command=lambda: self.load_priority_call())
        self.next_priority_call_button.grid(row=0, column=14, padx=(2,2), pady=(5,0), stick='ew')

    def close_call(self):
        if self.call_start_entry != "" and self.call_end_entry != "":
            row_index = self.priority_call_num[1]
            call_start = self.call_start_entry.get()
            call_end = self.call_end_entry.get()
            issue_text = self.issue_entry.get('1.0', tk.END)
            notes_text = self.note_entry.get('1.0', tk.END)
            self.call_data.at[row_index, 'call_start'] = call_start
            self.call_data.at[row_index, 'call_end'] = call_end
            self.call_data.at[row_index, 'issue'] = issue_text
            self.call_data.at[row_index, 'notes'] = notes_text
            self.call_data.to_csv('Data/calls.csv')



    def timestamp_start(self):
        dt = datetime.datetime.now()
        timestamp = dt.replace(microsecond=0)
        self.call_start_entry.insert(0, str(timestamp))

    def timestamp_end(self):
        dt = datetime.datetime.now()
        timestamp = dt.replace(microsecond=0)
        self.call_end_entry.insert(0, str(timestamp))

    def load_priority_call(self):
        self.enable_fields()
        self.clear_fields()
        self.call_num_entry.delete(0, 'end')
        self.priority_call_num = self.calls_priority_queue.get()
        self.call_num_entry.insert(0, [self.priority_call_num[1]])
        cust_index = self.call_data.at[self.priority_call_num[1], 'customer']
        self.category_entry.insert(0, self.call_data.at[self.priority_call_num[1], 'category'])
        self.priority_entry.insert(0, self.priorities[self.call_data.at[self.priority_call_num[1], 'priority']])
        self.call_time_entry.insert(0, self.call_data.at[self.priority_call_num[1], 'call_time'])
        self.call_start_entry.insert(0, self.call_data.at[self.priority_call_num[1], 'call_start'])
        self.call_end_entry.insert(0, self.call_data.at[self.priority_call_num[1], 'call_end'])
        self.issue_entry.insert("1.0", self.call_data.at[self.priority_call_num[1], 'issue'])
        self.note_entry.insert("1.0", self.call_data.at[self.priority_call_num[1], 'notes'])
        self.customer_entry.insert(0, self.customer_data.at[cust_index, 'cust_name'])
        self.company_entry.insert(0, self.customer_data.at[cust_index, 'cust_company'])
        self.street_entry.insert(0, self.customer_data.at[cust_index, 'cust_street'])
        self.city_entry.insert(0, self.customer_data.at[cust_index, 'cust_city'])
        self.state_entry.insert(0, self.customer_data.at[cust_index, 'cust_state'])
        self.zip_entry.insert(0, self.customer_data.at[cust_index, 'cust_zip'])
        self.phone_entry.insert(0, self.customer_data.at[cust_index, 'cust_phone'])
        self.email_entry.insert(0, self.customer_data.at[cust_index , 'cust_email'])
        self.disable_fields()

    def get_priority_list(self):
        self.load_calls()
        get_calls = self.call_data[self.call_data['status'] != 'Completed']
        get_calls = get_calls[get_calls['status'] != 'On Hold']
        index_list = get_calls.index.values.tolist()
        priority_list = get_calls["priority"].tolist()
        # priority_list = [ int(x) for x in priority_list]
        calls_priority_list = []
        for item in range(len(priority_list)):
            calls_priority_list.append((priority_list[item], index_list[item]))
        self.calls_priority_queue = PriorityQueue()
        for call in calls_priority_list:
            self.calls_priority_queue.put(call)

    def enable_fields(self):
        self.call_num_entry.configure(state='normal')
        self.category_entry.configure(state='normal')
        self.priority_entry.configure(state='normal')
        self.call_time_entry.configure(state='normal')
        self.customer_entry.configure(state='normal')
        self.company_entry.configure(state='normal')
        self.street_entry.configure(state='normal')
        self.city_entry.configure(state='normal')
        self.state_entry.configure(state='normal')
        self.zip_entry.configure(state='normal')
        self.phone_entry.configure(state='normal')
        self.email_entry.configure(state='normal')

    def disable_fields(self):
        self.call_num_entry.configure(state='disabled')
        self.category_entry.configure(state='disabled')
        self.priority_entry.configure(state='disabled')
        self.call_time_entry.configure(state='disabled')
        self.customer_entry.configure(state='disabled')
        self.company_entry.configure(state='disabled')
        self.street_entry.configure(state='disabled')
        self.city_entry.configure(state='disabled')
        self.state_entry.configure(state='disabled')
        self.zip_entry.configure(state='disabled')
        self.phone_entry.configure(state='disabled')
        self.email_entry.configure(state='disabled')

    def clear_call(self):
        self.enable_fields()
        self.customer_menu.set('')
        self.clear_fields()
        self.disable_fields()
        self.category_menu.set('')
        self.priority_menu.set('')
        self.issue_entry.delete('1.0', 'end')
        self.required_tag.destroy()

    def clear_fields(self):
        self.category_entry.delete(0, 'end')
        self.priority_entry.delete(0, 'end')
        self.call_time_entry.delete(0, 'end')
        self.call_start_entry.delete(0, 'end')
        self.call_end_entry.delete(0, 'end')
        self.issue_entry.delete("1.0", 'end')
        self.note_entry.delete('1.0', 'end')
        self.customer_entry.delete(0, 'end')
        self.company_entry.delete(0, 'end')
        self.street_entry.delete(0, 'end')
        self.city_entry.delete(0, 'end')
        self.state_entry.delete(0, 'end')
        self.zip_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')

    def load_customers(self):
        data = pd.read_csv('Data/customers.csv', dtype={"cust_zip": object})
        data.fillna('', inplace=True)
        self.customer_data = pd.DataFrame(data)
        self.customer_data = self.customer_data.set_index('cust_num')

    def load_calls(self):
        data = pd.read_csv('Data/calls.csv')
        data.fillna('', inplace=True)
        self.call_data = pd.DataFrame(data)
        self.call_data = self.call_data.set_index('call_num')
        pd.to_datetime(self.call_data['call_start'])

    def onShowFrame(self, event):
        self.update()
        self.load_customers()
        self.load_calls()
        self.get_priority_list()

    def hold_call(self):
        pass


class Customers(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=720, width=1080, background="white")
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, minsize=150)
        self.columnconfigure(2, minsize=150)
        self.bind('<<ShowFrame>>', self.onShowFrame)
        self.load_customers()
        self.fields = ['cust_company', 'cust_street', 'cust_city', 'cust_state', 'cust_zip', 'cust_phone',
                       'cust_email']

        selected_cust = tk.StringVar()
        self.customer_menu = ttk.Combobox(self, textvariable=selected_cust, state='readonly')
        self.customer_menu['values'] = self.generate_customer_list()
        self.customer_menu.current()
        self.customer_menu.config(justify='center')

        self.select_label = tk.Label(self, text="Please Select a Customer")
        self.select_label.config(bg='black', fg='white')
        self.select_label.grid(row=0, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))

        self.customer_menu.grid(row=1, column=0, columnspan=3, sticky='ew', padx=(5, 5))
        self.customer_menu.bind('<<ComboboxSelected>>', self.customer_changed)

        # company entry
        self.company_label = tk.Label(self, text="Company")
        self.company_label.config(bg='black', fg='white')
        self.company_label.grid(row=4, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.company_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.company_entry.grid(row=5, column=0, columnspan=3, sticky='ew', padx=(5, 5))

        # street entry
        self.street_label = tk.Label(self, text="Street")
        self.street_label.config(bg='black', fg='white')
        self.street_label.grid(row=6, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.street_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.street_entry.grid(row=7, column=0, columnspan=3, sticky='ew', padx=(5, 5))

        # city entry
        self.city_label = tk.Label(self, text="City")
        self.city_label.config(bg='black', fg='white')
        self.city_label.grid(row=8, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.city_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.city_entry.grid(row=9, column=0, sticky='ew', padx=(5, 2))

        # state entry
        self.state_label = tk.Label(self, text="State")
        self.state_label.config(bg='black', fg='white')
        self.state_label.grid(row=8, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.state_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.state_entry.grid(row=9, column=1, sticky='ew', padx=(2, 2))

        # zip entry
        self.zip_label = tk.Label(self, text="Zip Code")
        self.zip_label.config(bg='black', fg='white')
        self.zip_label.grid(row=8, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.zip_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.zip_entry.grid(row=9, column=2, sticky='ew', padx=(2, 5))

        # phone entry
        self.phone_label = tk.Label(self, text="Phone")
        self.phone_label.config(bg='black', fg='white')
        self.phone_label.grid(row=10, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.phone_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.phone_entry.grid(row=11, column=0, sticky='ew', padx=(5, 2))

        # email entry
        self.email_label = tk.Label(self, text="E-mail")
        self.email_label.config(bg='black', fg='white')
        self.email_label.grid(row=10, column=1, columnspan=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.email_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.email_entry.grid(row=11, column=1, columnspan=2, sticky='ew', padx=(2, 5))

        # buttons
        self.edit_button = ttk.Button(self, text="Edit Customer", command=lambda: self.edit_customer())
        self.edit_button.grid(row=12, column=0, padx=(5, 2), pady=(5, 0), sticky='ew')
        self.submit_button = ttk.Button(self, text="Save Customer", state='disabled',
                                        command=lambda: self.save_customer())
        self.submit_button.grid(row=12, column=1, columnspan=2, padx=(2, 5), pady=(5, 0), sticky='ew')

        # hidden required tag
        self.required_tag = tk.Label(self, text='Customer name and Phone are required!')
        self.required_tag.config(fg='red')

    def edit_customer(self):
        self.enable_fields()
        self.submit_button.config(state='normal')
        self.edit_button.config(state='disabled')
        self.name_label = tk.Label(self, text="Customer Name")
        self.name_label.config(bg='black', fg='white')
        self.name_label.grid(row=2, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.name_entry = tk.Entry(self, disabledforeground='black', justify='center')
        self.name_entry.grid(row=3, column=0, columnspan=3, sticky='ew', padx=(5, 5))
        self.name_entry.insert(0, self.customer_data.at[self.row_index, 'cust_name'])

    def save_customer(self):
        name_text = self.name_entry.get()
        company_text = self.company_entry.get()
        street_text = self.street_entry.get()
        city_text = self.city_entry.get()
        state_text = self.state_entry.get()
        zip_text = self.zip_entry.get()
        phone_text = self.phone_entry.get()
        email_text = self.email_entry.get()
        if name_text == "" or phone_text == "":
            self.required_missing()
        else:
            self.required_tag.destroy()
            self.customer_data.at[self.row_index, 'cust_name'] = name_text
            self.customer_data.at[self.row_index, 'cust_company'] = company_text
            self.customer_data.at[self.row_index, 'cust_street'] = street_text
            self.customer_data.at[self.row_index, 'cust_city'] = city_text
            self.customer_data.at[self.row_index, 'cust_state'] = state_text
            self.customer_data.at[self.row_index, 'cust_zip'] = zip_text
            self.customer_data.at[self.row_index, 'cust_phone'] = phone_text
            self.customer_data.at[self.row_index, 'cust_email'] = email_text
            self.customer_data.to_csv('Data/customers.csv')
            self.load_customers()
            self.customer_menu['values'] = self.generate_customer_list()
            self.customer_menu.set(name_text)
            self.disable_fields()
            self.name_label.destroy()
            self.name_entry.destroy()
            self.submit_button.config(state='disabled')
            self.edit_button.config(state='normal')

    def required_missing(self):
        # hidden required tag
        self.required_tag = tk.Label(self, text='Customer name and Phone are required!')
        self.required_tag.config(fg='red')
        self.required_tag.grid(row=13, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))

    def customer_changed(self, event):
        self.name_num = dict(zip(self.customer_data.cust_name, self.customer_data.index))
        self.key = self.customer_menu.get()
        self.row_index = int(self.name_num[self.key])
        self.enable_fields()
        self.clear_fields()
        self.company_entry.insert(0, self.customer_data.at[self.row_index, 'cust_company'])
        self.street_entry.insert(0, self.customer_data.at[self.row_index, 'cust_street'])
        self.city_entry.insert(0, self.customer_data.at[self.row_index, 'cust_city'])
        self.state_entry.insert(0, self.customer_data.at[self.row_index, 'cust_state'])
        self.zip_entry.insert(0, self.customer_data.at[self.row_index, 'cust_zip'])
        self.phone_entry.insert(0, self.customer_data.at[self.row_index, 'cust_phone'])
        self.email_entry.insert(0, self.customer_data.at[self.row_index, 'cust_email'])
        self.disable_fields()

    def clear_fields(self):
        # self.name_entry.delete(0, 'end')
        self.company_entry.delete(0, 'end')
        self.street_entry.delete(0, 'end')
        self.city_entry.delete(0, 'end')
        self.state_entry.delete(0, 'end')
        self.zip_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')

    def enable_fields(self):
        # self.name_entry.configure(state='normal')
        self.company_entry.configure(state='normal')
        self.street_entry.configure(state='normal')
        self.city_entry.configure(state='normal')
        self.state_entry.configure(state='normal')
        self.zip_entry.configure(state='normal')
        self.phone_entry.configure(state='normal')
        self.email_entry.configure(state='normal')

    def disable_fields(self):
        # self.name_entry.configure(state='disabled')
        self.company_entry.configure(state='disabled')
        self.street_entry.configure(state='disabled')
        self.city_entry.configure(state='disabled')
        self.state_entry.configure(state='disabled')
        self.zip_entry.configure(state='disabled')
        self.phone_entry.configure(state='disabled')
        self.email_entry.configure(state='disabled')

    def generate_customer_list(self):
        return self.customer_data['cust_name'].to_list()

    def load_customers(self):
        data = pd.read_csv('Data/customers.csv', dtype={"cust_zip": object})
        data.fillna('', inplace=True)
        self.customer_data = pd.DataFrame(data)
        self.customer_data = self.customer_data.set_index('cust_num')

    def onShowFrame(self, event):
        self.update()
        self.load_customers()
        self.customer_menu['values'] = self.generate_customer_list()


class NewCustomer(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=720, width=1080, background="white")
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, minsize=150)
        self.columnconfigure(2, minsize=150)

        # name entry
        self.name_label = tk.Label(self, text="Customer Name")
        self.name_label.config(bg='black', fg='white')
        self.name_label.grid(row=0, column=0, columnspan=3, sticky='ew', padx=(5,5), pady=(5,0))
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=1, column=0, columnspan=3, sticky='ew', padx=(5,5))

        # company entry
        self.company_label = tk.Label(self, text="Company")
        self.company_label.config(bg='black', fg='white')
        self.company_label.grid(row=2, column=0, columnspan=3, sticky='ew', padx=(5,5), pady=(5,0))
        self.company_entry = ttk.Entry(self)
        self.company_entry.grid(row=3, column=0, columnspan=3, sticky='ew', padx=(5,5))

        # street entry
        self.street_label = tk.Label(self, text="Street")
        self.street_label.config(bg='black', fg='white')
        self.street_label.grid(row=4, column=0, columnspan=3, sticky='ew', padx=(5, 5), pady=(5, 0))
        self.street_entry = ttk.Entry(self)
        self.street_entry.grid(row=5, column=0, columnspan=3, sticky='ew', padx=(5, 5))

        # city entry
        self.city_label = tk.Label(self, text="City")
        self.city_label.config(bg='black', fg='white')
        self.city_label.grid(row=6, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.city_entry = ttk.Entry(self)
        self.city_entry.grid(row=7, column=0, sticky='ew', padx=(5, 2))

        # state entry
        self.state_label = tk.Label(self, text="State")
        self.state_label.config(bg='black', fg='white')
        self.state_label.grid(row=6, column=1, sticky='ew', padx=(2, 2), pady=(5, 0))
        self.state_entry = ttk.Entry(self)
        self.state_entry.grid(row=7, column=1, sticky='ew', padx=(2, 2))

        # zip entry
        self.zip_label = tk.Label(self, text="Zip Code")
        self.zip_label.config(bg='black', fg='white')
        self.zip_label.grid(row=6, column=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.zip_entry = ttk.Entry(self)
        self.zip_entry.grid(row=7, column=2, sticky='ew', padx=(2, 5))

        # phone email
        self.phone_label = tk.Label(self, text="Phone")
        self.phone_label.config(bg='black', fg='white')
        self.phone_label.grid(row=8, column=0, sticky='ew', padx=(5, 2), pady=(5, 0))
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=9, column=0, sticky='ew', padx=(5, 2))

        # email entry
        self.email_label = tk.Label(self, text="E-mail")
        self.email_label.config(bg='black', fg='white')
        self.email_label.grid(row=8, column=1, columnspan=2, sticky='ew', padx=(2, 5), pady=(5, 0))
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=9, column=1, columnspan=2, sticky='ew', padx=(2, 5))

        # buttons
        clear_button = ttk.Button(self, text="Clear", command=lambda: self.clear_customer())
        clear_button.grid(row=10, column=0, padx=(5, 2), pady=(5, 0), sticky='ew')
        submit_button = ttk.Button(self, text="Save Customer", command=lambda: self.save_customer())
        submit_button.grid(row=10, column=1, columnspan=2, padx=(2, 5), pady=(5, 0), sticky='ew')

        # hidden required tag
        self.required_tag = tk.Label(self, text='Customer name and Phone are required!')
        self.required_tag.config(fg='red')

    def clear_customer(self):
        self.name_entry.delete(0, 'end')
        self.company_entry.delete(0, 'end')
        self.street_entry.delete(0, 'end')
        self.city_entry.delete(0, 'end')
        self.state_entry.delete(0, 'end')
        self.zip_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.required_tag.destroy()

    def save_customer(self):
        name_text = self.name_entry.get()
        company_text = self.company_entry.get()
        street_text = self.street_entry.get()
        city_text = self.city_entry.get()
        state_text = self.state_entry.get()
        zip_text = self.zip_entry.get()
        phone_text = self.phone_entry.get()
        email_text = self.email_entry.get()
        if name_text == "" or phone_text == "":
            self.required_missing()
        else:
            self.clear_customer()
            self.required_tag.destroy()
            functions.save_customer_csv(name_text, company_text, street_text,
                                        city_text, state_text, zip_text,
                                        phone_text, email_text)

    def required_missing(self):
        # hidden required tag
        self.required_tag = tk.Label(self, text='Customer name and Phone are required!')
        self.required_tag.config(fg='red')
        self.required_tag.grid(row=11, column=0, columnspan=3, sticky='ew', padx=(5,5), pady=(5,0))





app = App()
app.mainloop()
