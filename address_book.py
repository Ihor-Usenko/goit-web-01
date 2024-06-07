import pickle
from collections import UserDict
from datetime import datetime, date, timedelta
from abc import ABC, abstractmethod


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate(value):
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    def __init__(self, value):
        if not self.validate_date(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    @staticmethod
    def validate_date(value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def string_to_date(date_string):
        return datetime.strptime(date_string, "%d.%m.%Y").date()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phone = None
        self.birthday = None

    def add_phone(self, phone):
        self.phone = Phone(phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def edit_phone(self, new_phone):
        self.phone = Phone(new_phone)

    def __str__(self):
        birthday_str = self.birthday.value if self.birthday else 'N/A'
        return f"Contact name: {self.name.value}, phone {self.phone}, birthday: {birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)


    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        for record in self.data.values():
            if record.birthday:
                bday_date = Birthday.string_to_date(record.birthday.value)
                this_year_bday = bday_date.replace(year=today.year)
                if today <= this_year_bday <= today + timedelta(days=days):
                    upcoming_birthdays.append(record)
        return upcoming_birthdays
    
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "You haven't entered a contact name or phone!"
        except KeyError:
            return "Contact is not found!"
        except ValueError as e:
            return str(e)

    return inner


class Command:
    def execute(self, args, book: AddressBook):
        pass


class AddContact(Command):
    @input_error
    def execute(self, args, book: AddressBook):
        if len(args) < 2:
            raise ValueError("Maybe you forgot enter name or phone?")
        name, phone, *_ = args
        record = book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        save_address_book(book)
        return message


class ChangePhone(Command):
    @input_error
    def execute(self, args, book: AddressBook):
        if len(args) < 1:
            raise ValueError("You did not enter the subscriber's name!")
        if len(args) < 2:
            raise ValueError("You did not enter a new phone number!")
        name, new_phone = args
        record = book.find(name)
        if not record:
            raise KeyError
        if not Phone.validate(new_phone):
            raise ValueError("Phone number must be 10 digits.")
        record.edit_phone(new_phone)
        save_address_book(book)
        return "Phone number updated."


class GetPhone(Command):
    @input_error
    def execute(self, args, book: AddressBook):
        name = args[0]
        record = book.find(name)
        if record is None:
            raise KeyError
        return f"{name}: {record.phone}"


class ShowAll(Command):
    @input_error
    def execute(self, _args, book: AddressBook):
        return '\n'.join(str(record) for record in book.data.values())


class AddBirthday(Command):
    @input_error
    def execute(self, args, book: AddressBook):
        name, birthday = args
        record = book.find(name)
        if record is None:
            raise KeyError
        record.add_birthday(birthday)
        save_address_book(book)
        return "Birthday added."


class ShowBirthday(Command):
    @input_error
    def execute(self, args, book: AddressBook):
        name = args[0]
        record = book.find(name)
        if record is None:
            raise KeyError
        return f"{name}: {record.birthday.value if record.birthday else 'N/A'}"


class ShowBirthdays(Command):
    @input_error
    def execute(self, _args, book: AddressBook):
        upcoming_birthdays = book.get_upcoming_birthdays()
        if not upcoming_birthdays:
            raise ValueError("No birthdays in the next week!")
        return '\n'.join(str(record) for record in upcoming_birthdays)
    

class UserInterface(ABC):
    
    @abstractmethod
    def display_message(self, message):
        pass
    
    @abstractmethod
    def get_input(self, prompt):
        pass


class ConsoleUserInterface(UserInterface):
    
    def display_message(self, message):
        print(message)
    
    def get_input(self, prompt):
        return input(prompt)



def load_address_book(filename="address_book.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def save_address_book(address_book, filename="address_book.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(address_book, f)


def main():
    book = load_address_book()
    cui = ConsoleUserInterface()
    
    cui.display_message("Welcome to the assistant bot!")
    
    commands = {
        "add": AddContact(),
        "change": ChangePhone(),
        "phone": GetPhone(),
        "all": ShowAll(),
        "add-birthday": AddBirthday(),
        "show-birthday": ShowBirthday(),
        "birthdays": ShowBirthdays(),
    }

    while True:
        user_input = cui.get_input("Enter a command: ")
        if user_input == '':
            cui.display_message("You have not entered anything")
            continue
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_address_book(book)
            cui.display_message("Good bye!")
            break

        elif command == "hello":
            cui.display_message("How can I help you?")

        elif command in commands:
            outcome = commands[command].execute(args, book)
            cui.display_message(outcome)

        else:
            cui.display_message("Invalid command.")


if __name__ == "__main__":
    main()
