#Import functions.
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

#File name for created .csv file.
FILE_NAME = "monthly_expenses.csv"

#Creates an empty file if the .csv file has not already been created, otherwise it uses the existing .csv file.
def load_expenses():
    
    if Path(FILE_NAME).exists():
        df = pd.read_csv(FILE_NAME)
    else:
        df = pd.DataFrame(columns=[
            "Date",
            "Month",
            "Category",
            "Description",
            "Amount",
            "Last Edited"
        ])
    return df

#Sorts expenses by amount before saving to file.
def save_expenses(df):
  
    df = df.sort_values(by="Amount")
    df.to_csv(FILE_NAME, index=False)

#Adds a new expense with the current date and month.
def add_expense(df):
    
    print("\n--- Add Expense ---")
    category = input("Enter category: ").strip()
    description = input("Enter description: ").strip()

    try:
        amount = float(input("Enter amount: ").strip())
    except ValueError:
        print("Invalid amount. Expense not added.")
        return df

    now = datetime.now()
    date_now = now.strftime("%Y-%m-%d %H:%M:%S")
    month_now = now.strftime("%Y-%m")

    new_expense = pd.DataFrame([{
        "Date": date_now,
        "Month": month_now,
        "Category": category,
        "Description": description,
        "Amount": amount,
        "Last Edited": date_now
    }])

    df = pd.concat([df, new_expense], ignore_index=True)
    save_expenses(df)
    print("Expense added successfully.")
    return df

#Displays all expenses with index numbers.
def view_expenses(df):
   
    print("\n--- All Expenses ---")
    if df.empty:
        print("No expenses found.")
    else:
        print(df.reset_index(drop=True))

#Displays expenses for a selected month, otherwise displays there are none.
def view_monthly_expenses(df):
    print("\n--- View Monthly Expenses ---")
    if df.empty:
        print("No expenses found.")
        return

    month = input("Enter month (YYYY-MM): ").strip()
    monthly_df = df[df["Month"] == month]

    if monthly_df.empty:
        print("No expenses found for that month.")
    else:
        print(monthly_df.reset_index(drop=True))

#Edits an existing expense by index. Month stays the same unless the user changes it manually. Last edited is automatically updated.
def edit_expense(df):
    print("\n--- Edit Expense ---")
    if df.empty:
        print("No expenses to edit.")
        return df

    print(df.reset_index(drop=True))

    try:
        index = int(input("Enter the index of the expense to edit: ").strip())
        if index < 0 or index >= len(df):
            print("Invalid index.")
            return df
    except ValueError:
        print("Invalid input.")
        return df

    print("Press Enter to keep the current value.")

    current_month = df.at[index, "Month"]
    current_category = df.at[index, "Category"]
    current_description = df.at[index, "Description"]
    current_amount = df.at[index, "Amount"]

    new_month = input(f"New month [{current_month}] (YYYY-MM): ").strip()
    new_category = input(f"New category [{current_category}]: ").strip()
    new_description = input(f"New description [{current_description}]: ").strip()
    new_amount = input(f"New amount [{current_amount}]: ").strip()

    if new_month:
        df.at[index, "Month"] = new_month
    if new_category:
        df.at[index, "Category"] = new_category
    if new_description:
        df.at[index, "Description"] = new_description
    if new_amount:
        try:
            df.at[index, "Amount"] = float(new_amount)
        except ValueError:
            print("Invalid amount. Amount not changed.")

    df.at[index, "Last Edited"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_expenses(df)
    print("Expense updated successfully.")
    return df

#Deletes expense by index 0 to how many there are, otherwise prints there are none.
def delete_expense(df):
    print("\n--- Delete Expense ---")
    if df.empty:
        print("No expenses to delete.")
        return df

    print(df.reset_index(drop=True))

    try:
        index = int(input("Enter the index of the expense to delete: ").strip())
        if index < 0 or index >= len(df):
            print("Invalid index.")
            return df
    except ValueError:
        print("Invalid input.")
        return df

    df = df.drop(index).reset_index(drop=True)
    save_expenses(df)
    print("Expense deleted successfully.")
    return df

#Shows total and average expenses for one selected month, otherwise prints there are none.
def show_monthly_summary(df):
    print("\n--- Monthly Summary ---")
    if df.empty:
        print("No expenses found.")
        return

    month = input("Enter month (YYYY-MM): ").strip()
    monthly_df = df[df["Month"] == month]

    if monthly_df.empty:
        print("No expenses found for that month.")
        return

    total = monthly_df["Amount"].sum()
    average = monthly_df["Amount"].mean()

    print(f"\nSummary for {month}")
    print(f"Total Expense: ${total:.2f}")
    print(f"Average Expense: ${average:.2f}")

    print("\nBy Category:")
    category_totals = monthly_df.groupby("Category")["Amount"].sum()
    print(category_totals)

#Shows totals for each month, otherwise prints statement saying there are none.
def show_all_months_summary(df):
    """
    Show totals for each month.
    """
    print("\n--- All Months Summary ---")
    if df.empty:
        print("No expenses found.")
        return

    monthly_totals = df.groupby("Month")["Amount"].sum().sort_index()
    print(monthly_totals)

#Shows the total expenses for a selected year, otherwise prints statement saying there is none.
def show_yearly_total(df):
    print("\n--- Yearly Total ---")
    if df.empty:
        print("No expenses found.")
        return

    year = input("Enter year (YYYY): ").strip()
    yearly_df = df[df["Month"].str.startswith(year)]

    if yearly_df.empty:
        print("No expenses found for that year.")
        return

    total = yearly_df["Amount"].sum()
    print(f"Total expenses for {year}: ${total:.2f}")

#Shows the running total month by month for a selected year, otherwise prints there are none.
def show_running_year_total(df):
    print("\n--- Running Yearly Total ---")
    if df.empty:
        print("No expenses found.")
        return

    year = input("Enter year (YYYY): ").strip()
    yearly_df = df[df["Month"].str.startswith(year)]

    if yearly_df.empty:
        print("No expenses found for that year.")
        return

    monthly_totals = yearly_df.groupby("Month")["Amount"].sum().sort_index()
    running_total = monthly_totals.cumsum()

    print(f"\nRunning total for {year}:")
    for month, total in running_total.items():
        print(f"{month}: ${total:.2f}")

#Generates a pie chart for a selected month, otherwise prints there are none and doesn't bring up a pie chart.
def show_pie_chart(df):
    print("\n--- Monthly Expense Pie Chart ---")
    if df.empty:
        print("No expenses available for chart.")
        return

    month = input("Enter month (YYYY-MM): ").strip()
    monthly_df = df[df["Month"] == month]

    if monthly_df.empty:
        print("No expenses found for that month.")
        return

    category_totals = monthly_df.groupby("Category")["Amount"].sum()

    plt.figure(figsize=(8, 8))
    plt.pie(category_totals, labels=category_totals.index, autopct="%1.1f%%", startangle=90)
    plt.title(f"Expenses by Category for {month}")
    plt.axis("equal")
    plt.show()

#Displays menu with options.
def display_menu():
    print("\n=== Monthly Expense Tracker ===")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. View Expenses for One Month")
    print("4. Edit Expense")
    print("5. Delete Expense")
    print("6. Show Monthly Summary")
    print("7. Show All Months Summary")
    print("8. Show Yearly Total")
    print("9. Show Running Yearly Total")
    print("10. Show Monthly Pie Chart")
    print("11. Exit")

#While loop for the main program. If numbers 1-11 are not chosen, a message comes up to say input needs to be 1-11.
def main():
    df = load_expenses()

    while True:
        display_menu()
        choice = input("Choose an option (1-11): ").strip()

        if choice == "1":
            df = add_expense(df)
        elif choice == "2":
            view_expenses(df)
        elif choice == "3":
            view_monthly_expenses(df)
        elif choice == "4":
            df = edit_expense(df)
        elif choice == "5":
            df = delete_expense(df)
        elif choice == "6":
            show_monthly_summary(df)
        elif choice == "7":
            show_all_months_summary(df)
        elif choice == "8":
            show_yearly_total(df)
        elif choice == "9":
            show_running_year_total(df)
        elif choice == "10":
            show_pie_chart(df)
        elif choice == "11":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 11.")


if __name__ == "__main__":
    main()