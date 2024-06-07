# Classes Diagram
```mermaid
classDiagram
    Field <|-- Name
    Field <|-- Phone
    Field <|-- Birthday
    Record --> Name
    Record --> Phone
    Record --> Birthday
    AddressBook --> Record
    UserDict <|-- AddressBook

    class Record{
        + name
        + phone
        + birthday
        add_phone()
        add_birthday()
        edit_phone()
        delete()
    }
    class Name{
        pass
    }
    class Phone{
        validate()
    }
    class Birthday{
        validate_date()
        string_to_date()
    }
    class AddressBook{
        add_record()
        find()
    }
    class UserDict
