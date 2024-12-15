import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import time
from bs4 import BeautifulSoup
import json

class InvoiceEventHandler(FileSystemEventHandler):
    """This function handles the invoice events"""
    def on_created(self, event):
        if not event.is_directory and (event.src_path.endswith('.xml')):
            print(f"New invoice detected: {event.src_path}")
            invoice_data = parse_invoice(event.src_path)
            print(f"Data from the invoice {event.src_path}: {invoice_data}")


def read_dir_path():
    """This function prompts the user to give the directory path. If path doesn`t exist, it creates the directory"""
    print("Please write the path of the directory to be monitored")
    while True:
        path = input()
        if os.path.isdir(path):
            print(f"Monitoring directory: {path}")
            return path
        elif not path:
            print("Path cannot be empty. Please try again.")
        else:
            try:
                os.makedirs(path)
                print(f"Directory created: {path}")
                return path
            except Exception as e:
                print(f"Failed to create directory: {e}")
                continue

def monitor_directory(directory_path):
    """This function monitors the given directory"""
    event_handler = InvoiceEventHandler()
    observer = Observer()
    observer.schedule(event_handler, directory_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
    
def parse_invoice(invoice_path):
    """This function gets a file path and returns important data from the xml file"""
    try:
        with open(invoice_path, 'r') as file:
            content = file.read()

        parsed_invoice = BeautifulSoup(content, 'xml')

        invoice_id = parsed_invoice.find("id").text if parsed_invoice.find("id") else None
        date = parsed_invoice.find("date").text if parsed_invoice.find("date") else None
        amount = float(parsed_invoice.find("amount").text) if parsed_invoice.find("amount") else 0.0
        category = parsed_invoice.find("category").text if parsed_invoice.find("category") else "Miscellaneous"

        return {
            "id": invoice_id,
            "date": date,
            "amount": amount,
            "category": category,
        }

    except Exception as e:
        print(f"Error parsing the XML file: {invoice_path} {e}")

def load_budget_limits():
    budget_limits_file_path = 'ExpenseAlert/budget_limits.json'
    try:
        with open(budget_limits_file_path) as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error reading the errors from: {budget_limits_file_path} {e}")

if __name__ == "__main__":

    #invoices_directory = read_dir_path()

    #monitor_directory(invoices_directory)

    budget_limits = load_budget_limits()
    print(budget_limits)