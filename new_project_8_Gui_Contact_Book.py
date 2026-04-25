# gui_contact_list.py

# Import tools needed for the graphical interface, JSON files, and file handling
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# Default file used when no file is passed in
DEFAULT_FILE_NAME = "contacts.json"


class ContactBookGUI:
    """
    This class creates a friendly GUI contact book.
    It allows the user to add, update, delete, search,
    load, and save contacts in a JSON file.
    """

    def __init__(self, root, startup_file=None):
        """
        Set up the main window, program data, styles,
        and all graphical widgets.
        """
        self.root = root
        self.root.title("Friendly Contact Book")
        self.root.geometry("1100x650")
        self.root.minsize(950, 580)
        self.root.configure(bg="#eef3f7")

        # Store the current file name
        self.file_name = startup_file if startup_file else DEFAULT_FILE_NAME

        # Store all contacts currently loaded
        self.contacts = []

        # Store the selected contact index
        self.selected_index = None

        # Create styles and widgets
        self.setup_styles()
        self.create_widgets()

        # Load file data and show it
        self.load_contacts()
        self.refresh_treeview()

    def setup_styles(self):
        """
        Create nicer styles for the treeview and buttons.
        """
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "Treeview",
            font=("Arial", 11),
            rowheight=28,
            background="white",
            fieldbackground="white"
        )

        self.style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold")
        )

        self.style.map(
            "Treeview",
            background=[("selected", "#b9d9ff")]
        )

    def create_widgets(self):
        """
        Create the full user interface.
        """
        # -------------------------------
        # Top title section
        # -------------------------------
        title_frame = tk.Frame(self.root, bg="#eef3f7")
        title_frame.pack(fill="x", padx=15, pady=(12, 6))

        title_label = tk.Label(
            title_frame,
            text="Friendly Contact Book",
            font=("Arial", 22, "bold"),
            bg="#eef3f7",
            fg="#1f3b5b"
        )
        title_label.pack(side="left")

        subtitle_label = tk.Label(
            title_frame,
            text="Add, search, update, and manage contacts easily",
            font=("Arial", 10),
            bg="#eef3f7",
            fg="#4e647a"
        )
        subtitle_label.pack(side="left", padx=15, pady=(8, 0))

        # -------------------------------
        # File section
        # -------------------------------
        file_frame = tk.Frame(self.root, bg="#dce8f2", bd=1, relief="solid")
        file_frame.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(
            file_frame,
            text="Current File:",
            font=("Arial", 10, "bold"),
            bg="#dce8f2"
        ).pack(side="left", padx=(10, 5), pady=8)

        self.file_label = tk.Label(
            file_frame,
            text=self.file_name,
            font=("Arial", 10),
            bg="#dce8f2",
            anchor="w"
        )
        self.file_label.pack(side="left", fill="x", expand=True, pady=8)

        tk.Button(
            file_frame,
            text="Open JSON File",
            font=("Arial", 10, "bold"),
            bg="#4f8cc9",
            fg="white",
            activebackground="#3e78b1",
            activeforeground="white",
            padx=10,
            command=self.open_file_dialog
        ).pack(side="right", padx=10, pady=6)

        # -------------------------------
        # Main area
        # -------------------------------
        main_frame = tk.Frame(self.root, bg="#eef3f7")
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left panel for form
        left_panel = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        # Right panel for search + table
        right_panel = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        right_panel.pack(side="right", fill="both", expand=True)

        # -------------------------------
        # Left panel content
        # -------------------------------
        form_header = tk.Label(
            left_panel,
            text="Contact Details",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#1f3b5b"
        )
        form_header.pack(anchor="w", padx=15, pady=(15, 10))

        form_frame = tk.Frame(left_panel, bg="white")
        form_frame.pack(fill="both", padx=15, pady=(0, 10))

        # Name
        tk.Label(form_frame, text="Name", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.name_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, bd=2, relief="groove")
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Phone
        tk.Label(form_frame, text="Phone Number", font=("Arial", 10, "bold"), bg="white").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.phone_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, bd=2, relief="groove")
        self.phone_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Address
        tk.Label(form_frame, text="Address", font=("Arial", 10, "bold"), bg="white").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.address_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, bd=2, relief="groove")
        self.address_entry.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        # Email
        tk.Label(form_frame, text="Email", font=("Arial", 10, "bold"), bg="white").grid(row=6, column=0, sticky="w", pady=(0, 4))
        self.email_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, bd=2, relief="groove")
        self.email_entry.grid(row=7, column=0, sticky="ew", pady=(0, 12))

        # Helpful note
        note_label = tk.Label(
            form_frame,
            text="Tip: Double-click a contact on the right to load it here for editing.",
            font=("Arial", 9),
            bg="white",
            fg="#5a6d7f",
            wraplength=280,
            justify="left"
        )
        note_label.grid(row=8, column=0, sticky="w", pady=(0, 14))

        # Button section
        button_frame = tk.Frame(left_panel, bg="white")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        tk.Button(
            button_frame,
            text="Add Contact",
            font=("Arial", 10, "bold"),
            bg="#42b883",
            fg="white",
            activebackground="#36956b",
            activeforeground="white",
            width=16,
            pady=8,
            command=self.add_contact
        ).grid(row=0, column=0, padx=4, pady=4)

        tk.Button(
            button_frame,
            text="Update Contact",
            font=("Arial", 10, "bold"),
            bg="#f0a53b",
            fg="white",
            activebackground="#d88d23",
            activeforeground="white",
            width=16,
            pady=8,
            command=self.update_contact
        ).grid(row=0, column=1, padx=4, pady=4)

        tk.Button(
            button_frame,
            text="Delete Contact",
            font=("Arial", 10, "bold"),
            bg="#e05a5a",
            fg="white",
            activebackground="#c94747",
            activeforeground="white",
            width=16,
            pady=8,
            command=self.delete_contact
        ).grid(row=1, column=0, padx=4, pady=4)

        tk.Button(
            button_frame,
            text="Clear Fields",
            font=("Arial", 10, "bold"),
            bg="#7a8ca5",
            fg="white",
            activebackground="#66778e",
            activeforeground="white",
            width=16,
            pady=8,
            command=self.clear_fields
        ).grid(row=1, column=1, padx=4, pady=4)

        tk.Button(
            button_frame,
            text="Save Contacts",
            font=("Arial", 10, "bold"),
            bg="#4f8cc9",
            fg="white",
            activebackground="#3e78b1",
            activeforeground="white",
            width=34,
            pady=8,
            command=self.save_contacts
        ).grid(row=2, column=0, columnspan=2, padx=4, pady=(8, 4))

        # -------------------------------
        # Right panel content
        # -------------------------------
        top_right_frame = tk.Frame(right_panel, bg="white")
        top_right_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(
            top_right_frame,
            text="Search Contacts",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#1f3b5b"
        ).pack(anchor="w", pady=(0, 8))

        search_row = tk.Frame(top_right_frame, bg="white")
        search_row.pack(fill="x")

        self.search_entry = tk.Entry(search_row, font=("Arial", 11), bd=2, relief="groove")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)

        tk.Button(
            search_row,
            text="Search",
            font=("Arial", 10, "bold"),
            bg="#4f8cc9",
            fg="white",
            activebackground="#3e78b1",
            activeforeground="white",
            width=12,
            command=self.search_contacts
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            search_row,
            text="Show All",
            font=("Arial", 10, "bold"),
            bg="#7a8ca5",
            fg="white",
            activebackground="#66778e",
            activeforeground="white",
            width=12,
            command=self.refresh_treeview
        ).pack(side="left")

        # Table frame
        table_frame = tk.Frame(right_panel, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("name", "phone", "address", "email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("name", text="Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("address", text="Address")
        self.tree.heading("email", text="Email")

        self.tree.column("name", width=170, anchor="w")
        self.tree.column("phone", width=120, anchor="w")
        self.tree.column("address", width=260, anchor="w")
        self.tree.column("email", width=240, anchor="w")

        y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")

        # Double-clicking a contact loads it into the entry fields
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # -------------------------------
        # Bottom status bar
        # -------------------------------
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 10),
            bg="#dce8f2",
            fg="#1f3b5b",
            anchor="w",
            padx=12
        )
        self.status_label.pack(fill="x", side="bottom")

    def set_status(self, message):
        """
        Show a helpful status message at the bottom of the window.
        """
        self.status_label.config(text=message)

    def update_file_label(self):
        """
        Update the label that shows the current file name.
        """
        self.file_label.config(text=self.file_name)

    def load_contacts(self):
        """
        Load contacts from the current JSON file.
        If the file is missing or invalid, use an empty list.
        """
        if not os.path.exists(self.file_name):
            self.contacts = []
            self.update_file_label()
            self.set_status("No file found yet. Starting with an empty contact list.")
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    self.contacts = data
                    self.set_status(f"Loaded {len(self.contacts)} contact(s).")
                else:
                    self.contacts = []
                    messagebox.showwarning("Invalid File", "The JSON file does not contain a valid contact list.")
                    self.set_status("Invalid file format. Loaded empty contact list.")
        except (json.JSONDecodeError, IOError):
            self.contacts = []
            messagebox.showwarning("File Error", "The file could not be read.")
            self.set_status("Could not read file. Loaded empty contact list.")

        self.update_file_label()

    def save_contacts(self):
        """
        Save the contacts list to the current JSON file.
        """
        try:
            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(self.contacts, file, indent=4)
            self.set_status(f"Saved {len(self.contacts)} contact(s) to file.")
            messagebox.showinfo("Saved", "Contacts saved successfully.")
        except IOError:
            messagebox.showerror("Save Error", "Could not save the contacts file.")
            self.set_status("Error: Could not save contacts.")

    def is_valid_name(self, name):
        """
        Check that the name is not blank and contains only letters and spaces.
        """
        if not name.strip():
            return False

        for part in name.split():
            if not part.isalpha():
                return False
        return True

    def is_valid_phone(self, phone):
        """
        Check that the phone number contains digits only.
        """
        return phone.isdigit()

    def is_valid_email(self, email):
        """
        Check for a simple valid email format.
        """
        return "@" in email and "." in email and len(email) >= 5

    def get_form_data(self):
        """
        Read the data currently typed into the entry fields.
        """
        return {
            "name": self.name_entry.get().strip(),
            "phone": self.phone_entry.get().strip(),
            "address": self.address_entry.get().strip(),
            "email": self.email_entry.get().strip()
        }

    def validate_contact(self, contact):
        """
        Validate one contact dictionary before it is added or updated.
        """
        if not self.is_valid_name(contact["name"]):
            messagebox.showerror("Invalid Name", "Name must contain letters and spaces only.")
            return False

        if not self.is_valid_phone(contact["phone"]):
            messagebox.showerror("Invalid Phone", "Phone number must contain digits only.")
            return False

        if not self.is_valid_email(contact["email"]):
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
            return False

        return True

    def add_contact(self):
        """
        Add a new contact using the form data.
        """
        contact = self.get_form_data()

        if not self.validate_contact(contact):
            return

        self.contacts.append(contact)
        self.save_contacts()
        self.refresh_treeview()
        self.clear_fields()
        self.set_status(f"Added contact: {contact['name']}")

    def update_contact(self):
        """
        Update the selected contact with the form data.
        """
        if self.selected_index is None:
            messagebox.showwarning("No Contact Selected", "Please double-click a contact first to load it for editing.")
            return

        updated_contact = self.get_form_data()

        if not self.validate_contact(updated_contact):
            return

        self.contacts[self.selected_index] = updated_contact
        self.save_contacts()
        self.refresh_treeview()
        self.clear_fields()
        self.set_status(f"Updated contact: {updated_contact['name']}")

    def delete_contact(self):
        """
        Delete the selected contact after asking for confirmation.
        """
        if self.selected_index is None:
            messagebox.showwarning("No Contact Selected", "Please double-click a contact first to select it.")
            return

        contact_name = self.contacts[self.selected_index]["name"]

        confirm = messagebox.askyesno(
            "Delete Contact",
            f"Are you sure you want to delete '{contact_name}'?"
        )

        if confirm:
            del self.contacts[self.selected_index]
            self.save_contacts()
            self.refresh_treeview()
            self.clear_fields()
            self.set_status(f"Deleted contact: {contact_name}")

    def search_contacts(self):
        """
        Search the contact list by name and show matching results.
        """
        search_text = self.search_entry.get().strip().lower()

        if not search_text:
            self.refresh_treeview()
            self.set_status("Showing all contacts.")
            return

        matches = []
        for contact in self.contacts:
            if search_text in contact.get("name", "").lower():
                matches.append(contact)

        self.refresh_treeview(matches)
        self.set_status(f"Found {len(matches)} matching contact(s).")

    def refresh_treeview(self, contact_list=None):
        """
        Clear the table and fill it with all contacts
        or a filtered set of contacts.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        if contact_list is None:
            contact_list = self.contacts

        for row_number, contact in enumerate(contact_list):
            self.tree.insert(
                "",
                "end",
                iid=str(row_number),
                values=(
                    contact.get("name", ""),
                    contact.get("phone", ""),
                    contact.get("address", ""),
                    contact.get("email", "")
                )
            )

        self.selected_index = None

    def on_tree_double_click(self, event):
        """
        Load the double-clicked contact into the input fields.
        """
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item_id = selected_items[0]
        values = self.tree.item(item_id, "values")

        # Find matching contact in the full contact list
        for index, contact in enumerate(self.contacts):
            if (
                contact.get("name", "") == values[0]
                and contact.get("phone", "") == values[1]
                and contact.get("address", "") == values[2]
                and contact.get("email", "") == values[3]
            ):
                self.selected_index = index
                break

        self.clear_fields(keep_selection=True)

        self.name_entry.insert(0, values[0])
        self.phone_entry.insert(0, values[1])
        self.address_entry.insert(0, values[2])
        self.email_entry.insert(0, values[3])

        self.set_status(f"Loaded contact for editing: {values[0]}")

    def clear_fields(self, keep_selection=False):
        """
        Clear all form fields.
        If keep_selection is False, also clear the selected contact.
        """
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

        if not keep_selection:
            self.tree.selection_remove(self.tree.selection())
            self.selected_index = None
            self.set_status("Input fields cleared.")

    def open_file_dialog(self):
        """
        Open a file dialog so the user can choose a different JSON file.
        """
        file_path = filedialog.askopenfilename(
            title="Open Contact List JSON File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if file_path:
            self.file_name = file_path
            self.load_contacts()
            self.refresh_treeview()
            self.clear_fields()
            self.set_status(f"Opened file: {file_path}")


def main():
    """
    Start the contact book GUI.
    If a file is passed on the command line, use it.
    Otherwise use the default file name.
    """
    startup_file = None

    if len(sys.argv) > 1:
        startup_file = sys.argv[1]

    root = tk.Tk()
    app = ContactBookGUI(root, startup_file)
    root.mainloop()


# Run the program only when executed directly
if __name__ == "__main__":
    main()