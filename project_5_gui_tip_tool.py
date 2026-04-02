import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar


class TipCalculatorApp:
    """
    A modern tip calculator GUI using ttkbootstrap.

    Features:
    - Enter bill amount
    - Select tip percentage
    - Select number of diners
    - Automatically updates calculations when values change
    - Handles invalid input safely
    """

    def __init__(self, root):
        self.root = root
        self.root.title("GUI Tip Tool")
        self.root.geometry("520x430")
        self.root.resizable(False, False)

        # ----------------------------
        # Variables
        # ----------------------------
        self.bill_var = StringVar()
        self.tip_var = StringVar(value="15")
        self.diners_var = StringVar(value="1")

        self.tip_amount_var = StringVar(value="$0.00")
        self.total_var = StringVar(value="$0.00")
        self.per_person_var = StringVar(value="$0.00")
        self.status_var = StringVar(value="Enter the bill amount to begin.")

        # ----------------------------
        # Build interface
        # ----------------------------
        self.create_widgets()

        # ----------------------------
        # Automatically update on change
        # ----------------------------
        self.bill_var.trace_add("write", self.update_calculations)
        self.tip_var.trace_add("write", self.update_calculations)
        self.diners_var.trace_add("write", self.update_calculations)

    def create_widgets(self):
        """Create and place all GUI widgets."""

        # Main container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Tip Calculator",
            font=("Segoe UI", 22, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = ttk.Label(
            main_frame,
            text="Calculate tip, total, and split the bill automatically",
            font=("Segoe UI", 10)
        )
        subtitle_label.pack(pady=(0, 20))

        # Input card
        input_frame = ttk.Labelframe(main_frame, text="Meal Details", padding=15)
        input_frame.pack(fill=X, pady=(0, 15))

        # Bill amount
        ttk.Label(input_frame, text="Bill Amount ($):", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky=W, padx=5, pady=10
        )
        bill_entry = ttk.Entry(
            input_frame,
            textvariable=self.bill_var,
            width=25,
            font=("Segoe UI", 11)
        )
        bill_entry.grid(row=0, column=1, padx=5, pady=10, sticky=EW)
        bill_entry.focus()

        # Tip percentage
        ttk.Label(input_frame, text="Tip Percentage:", font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, sticky=W, padx=5, pady=10
        )
        tip_combo = ttk.Combobox(
            input_frame,
            textvariable=self.tip_var,
            values=["10", "15", "20"],
            state="readonly",
            width=22
        )
        tip_combo.grid(row=1, column=1, padx=5, pady=10, sticky=EW)

        # Diners
        ttk.Label(input_frame, text="Number of Diners:", font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, sticky=W, padx=5, pady=10
        )
        diners_combo = ttk.Combobox(
            input_frame,
            textvariable=self.diners_var,
            values=["1", "2", "3", "4", "5", "6"],
            state="readonly",
            width=22
        )
        diners_combo.grid(row=2, column=1, padx=5, pady=10, sticky=EW)

        input_frame.columnconfigure(1, weight=1)

        # Results card
        results_frame = ttk.Labelframe(main_frame, text="Results", padding=15)
        results_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(results_frame, text="Tip Amount:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=W, padx=5, pady=8
        )
        ttk.Label(
            results_frame,
            textvariable=self.tip_amount_var,
            font=("Segoe UI", 11, "bold"),
            bootstyle="success"
        ).grid(row=0, column=1, sticky=E, padx=5, pady=8)

        ttk.Label(results_frame, text="Total with Tip:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=W, padx=5, pady=8
        )
        ttk.Label(
            results_frame,
            textvariable=self.total_var,
            font=("Segoe UI", 11, "bold"),
            bootstyle="info"
        ).grid(row=1, column=1, sticky=E, padx=5, pady=8)

        ttk.Label(results_frame, text="Per Person:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=W, padx=5, pady=8
        )
        ttk.Label(
            results_frame,
            textvariable=self.per_person_var,
            font=("Segoe UI", 11, "bold"),
            bootstyle="warning"
        ).grid(row=2, column=1, sticky=E, padx=5, pady=8)

        results_frame.columnconfigure(1, weight=1)

        # Status message
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            bootstyle="danger",
            font=("Segoe UI", 9)
        )
        status_label.pack(anchor=W, pady=(0, 15))

        # Exit button
        exit_button = ttk.Button(
            main_frame,
            text="Exit",
            command=self.root.destroy,
            bootstyle="danger"
        )
        exit_button.pack(fill=X)

    def update_calculations(self, *args):
        """
        Recalculate values whenever the bill amount,
        tip percentage, or number of diners changes.
        """

        bill_text = self.bill_var.get().strip()
        tip_text = self.tip_var.get().strip()
        diners_text = self.diners_var.get().strip()

        # If bill entry is empty, reset output
        if bill_text == "":
            self.tip_amount_var.set("$0.00")
            self.total_var.set("$0.00")
            self.per_person_var.set("$0.00")
            self.status_var.set("Enter the bill amount to begin.")
            return

        try:
            bill_amount = float(bill_text)

            if bill_amount < 0:
                raise ValueError("Negative bill amount")

            tip_percent = float(tip_text)
            diners = int(diners_text)

            if diners < 1:
                raise ValueError("Invalid number of diners")

            # Calculations
            tip_amount = bill_amount * (tip_percent / 100)
            total_with_tip = bill_amount + tip_amount
            per_person = total_with_tip / diners

            # Display formatted values
            self.tip_amount_var.set(f"${tip_amount:.2f}")
            self.total_var.set(f"${total_with_tip:.2f}")
            self.per_person_var.set(f"${per_person:.2f}")
            self.status_var.set("")

        except ValueError:
            self.tip_amount_var.set("$0.00")
            self.total_var.set("$0.00")
            self.per_person_var.set("$0.00")
            self.status_var.set("Please enter a valid numeric bill amount.")

def main():
    """
    Create the main application window and run the program.
    """
    app = ttk.Window(themename="litera")
    TipCalculatorApp(app)
    app.mainloop()


if __name__ == "__main__":
    main()