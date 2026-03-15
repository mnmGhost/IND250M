#Imports needed functions to allow for reading, writing, and conversion of json files and to allow python code to interact with file system.
import json
import os

# Name of the file used to store contacts permanently.
FILE_NAME = "contacts.json"

#Defines loaded_contacts code, allows for reading and loading of contacts. Ensures code does not crash by inserting an empty list when invalid responses are detected.
def load_contacts():
    """
    Load contacts from the JSON file.
    If the file does not exist or is invalid, return an empty list.
    """
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r") as file:
            data = json.load(file)

            # Make sure the JSON file contains a list
            if isinstance(data, list):
                return data
            else:
                return []
    except (json.JSONDecodeError, IOError):
        # If the file is empty, corrupted, or unreadable, start with an empty list
        return []

#Defines save_contact code, saves the curent list of contacts to json file.
def save_contacts(contacts):
    """
    Save the contact list to the JSON file.
    The indent makes the file easier to read.
    """
    with open(FILE_NAME, "w") as file:
        json.dump(contacts, file, indent=4)

#Defines is_valid_name, checks for valid input for name.
def is_valid_name(name):
    """
    Check that the name contains only letters and spaces.
    Reject names with numbers or special characters.
    """
    if not name.strip():
        return False

    for part in name.split():
        if not part.isalpha():
            return False
    return True

#Defines is_valid_phone, checks for valid input for phone number.
def is_valid_phone(phone):
    """
    Check that the phone number contains digits only.
    """
    return phone.isdigit()

#Defines is_valid_email, checks for valid input for email address.
def is_valid_email(email):
    """
    Basic email validation.
    This checks for the presence of '@' and '.'.
    """
    return "@" in email and "." in email and len(email) >= 5

#Defines add_contact, prompts input contact name, phone number, address, and email address, checks if inputs are valid, provides error message, prompts user to start over.
def add_contact(contacts):
    """
    Ask the user for contact information, validate it,
    and add it to the contact list if valid.
    """
    print("\n--- Add Contact ---")

    name = input("Enter name: ").strip()
    if not is_valid_name(name):
        print("Error: Name must contain letters and spaces only.")
        return

    phone = input("Enter phone number: ").strip()
    if not is_valid_phone(phone):
        print("Error: Phone number must contain digits only.")
        return

    address = input("Enter address: ").strip()

    email = input("Enter email: ").strip()
    if not is_valid_email(email):
        print("Error: Please enter a valid email address.")
        return

    # Create a dictionary for the new contact
    contact = {
        "name": name,
        "phone": phone,
        "address": address,
        "email": email
    }

    contacts.append(contact)
    save_contacts(contacts)
    print(f"Contact '{name}' added successfully.")

#Defines view_contacts, displays contacts in list if contacts present, shows message if not present.
def view_contacts(contacts):
    """
    Display all contacts in the list.
    """
    print("\n--- Contact List ---")

    if not contacts:
        print("No contacts found.")
        return

    for index, contact in enumerate(contacts, start=1):
        print(f"\nContact #{index}")
        print(f"Name: {contact['name']}")
        print(f"Phone: {contact['phone']}")
        print(f"Address: {contact['address']}")
        print(f"Email: {contact['email']}")

#Defines delete_contact, prompts input for contact to be deleted, deletes contact if it is present, shows message to let user know contact was deleted, if not then message showing contact not found appears.
def delete_contact(contacts):
    """
    Delete a contact by name.
    Removes the first matching contact found.
    """
    print("\n--- Delete Contact ---")
    name_to_delete = input("Enter the name of the contact to delete: ").strip()

    for contact in contacts:
        if contact["name"].lower() == name_to_delete.lower():
            contacts.remove(contact)
            save_contacts(contacts)
            print(f"Contact '{contact['name']}' deleted successfully.")
            return

    print("Contact not found.")

#Defines search_contact, prompts input to search name, if name not found message letting user know nothing came up appears.
def search_contact(contacts):
    """
    Search for contacts by name.
    Matches partial names as well.
    """
    print("\n--- Search Contact ---")
    search_name = input("Enter the name to search for: ").strip().lower()

    matches = []
    for contact in contacts:
        if search_name in contact["name"].lower():
            matches.append(contact)

    if not matches:
        print("No matching contacts found.")
        return

    print("\nMatching Contacts:")
    for index, contact in enumerate(matches, start=1):
        print(f"\nMatch #{index}")
        print(f"Name: {contact['name']}")
        print(f"Phone: {contact['phone']}")
        print(f"Address: {contact['address']}")
        print(f"Email: {contact['email']}")

#Deines dispaly_menu, prompts input of five options to choose from.
def display_menu():
    """
    Show the main menu options.
    """
    print("\n=== Contact Book Menu ===")
    print("1. Add Contact")
    print("2. View Contacts")
    print("3. Delete Contact")
    print("4. Search Contact")
    print("5. Exit")

#Defines main, provides basic while loop until program is exited.
def main():
    """
    Main program loop.
    Loads contacts, shows the menu, and performs the chosen action.
    """
    contacts = load_contacts()

    while True:
        display_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_contact(contacts)
        elif choice == "2":
            view_contacts(contacts)
        elif choice == "3":
            delete_contact(contacts)
        elif choice == "4":
            search_contact(contacts)
        elif choice == "5":
            print("Exiting Contact Book. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


# This makes sure the program runs only when the file is executed directly.
if __name__ == "__main__":
    main()