import csv
import matplotlib.pyplot as plt
from utils import log_action, get_date

FILE_NAME = "expenses.csv"

@log_action
def add_expense(category, amount, description):
    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([get_date(), category, amount, description])
    print(f"✅ Added: {description} (₹{amount}) under '{category}'")

@log_action
def view_expenses():
    try:
        with open(FILE_NAME, "r") as file:
            reader = csv.reader(file)
            print("\n📒 Expense List:")
            for row in reader:
                print(f"Date: {row[0]} | Category: {row[1]} | Amount: ₹{row[2]} | Note: {row[3]}")
    except FileNotFoundError:
        print("⚠️ No expenses found yet.")

@log_action
def total_by_category():
    try:
        with open(FILE_NAME, "r") as file:
            reader = csv.reader(file)
            totals = {}
            for row in reader:
                category = row[1]
                amount = float(row[2])
                totals[category] = totals.get(category, 0) + amount

            if not totals:
                print("⚠️ No data found. Add some expenses first!")
                return

            print("\n💡 Total Spending by Category:")
            for cat, total in totals.items():
                print(f"{cat}: ₹{total}")

            # Visualization Option
            show_chart = input("\n📊 Do you want to see a chart? (y/n): ").lower()
            if show_chart == "y":
                plot_chart(totals)

    except FileNotFoundError:
        print("⚠️ No data found. Add some expenses first!")

def plot_chart(totals):
    categories = list(totals.keys())
    amounts = list(totals.values())

    print("\n1. Pie Chart")
    print("2. Bar Chart")
    choice = input("Choose chart type (1/2): ")

    if choice == "1":
        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title("Expense Distribution by Category")
        plt.show()

    elif choice == "2":
        plt.figure(figsize=(8, 5))
        plt.bar(categories, amounts)
        plt.xlabel("Category")
        plt.ylabel("Total (₹)")
        plt.title("Expense Summary by Category")
        plt.show()

    else:
        print("❌ Invalid choice. No chart displayed.")
