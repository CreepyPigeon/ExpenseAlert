import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import time

class InvoiceEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and (event.src_path.endswith('.xml')):
            print(f"New invoice detected: {event.src_path}")

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
    
if __name__ == "__main__":

    invoices_directory = read_dir_path()

    monitor_directory(invoices_directory)