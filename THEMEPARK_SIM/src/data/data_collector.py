import csv
from utils.helpers import format_time

class DataCollector:
    """
    Collects and manages visitor data and sales information for the theme park.

    Attributes:
        visitor_data (list): List of data for each visitor.
        journey_log (list): Log of events during the visitor's journey in the park.
        successful_sales (int): Count of successful ticket sales at the ticket office.
        failed_sales (int): Count of failed ticket sales.
        online_sales (int): Count of online ticket sales.
        online_entries_used (int): Count of online entries that have been used.
        ticket_times (list): List of wait times for ticket purchases.
    """
    
    def __init__(self):
        """Initializes the DataCollector with empty data structures and counters."""
        self.visitor_data = []  # List to store visitor data
        self.journey_log = []  # List to log events during the visitor's journey
        self.successful_sales = 0  # Counter for successful ticket sales
        self.failed_sales = 0  # Counter for failed ticket sales
        self.online_sales = 0  # Counter for online ticket sales
        self.online_entries_used = 0  # Counter for used online entries
        self.ticket_times = []  # List to store ticket purchase wait times

    def register_visitor(self, visitor_data):
        """Registers a new visitor and updates sales statistics.

        Args:
            visitor_data (dict): Data related to the visitor, including ticket type and entry status.
        """
        self.visitor_data.append(visitor_data)  # Add visitor data to the list

        # Increment successful sales if the visitor bought a ticket at the office and entered the park
        if visitor_data.get('ticket_type') == 'ticket_office' and visitor_data.get('entered_park'):
            self.successful_sales += 1

    def register_failure(self):
        """Increments the count of failed ticket sales."""
        self.failed_sales += 1  # Increment the failed sales counter

    def register_online_sale(self, used=False):
        """Registers an online ticket sale.

        Args:
            used (bool): Indicates whether the online entry was used.
        """
        self.online_sales += 1  # Increment the online sales counter
        if used:
            self.online_entries_used += 1  # Increment used online entries if applicable

    def mark_online_entry_used(self):
        """Marks an online entry as used if there are available entries."""
        if self.online_entries_used < self.online_sales:
            self.online_entries_used += 1  # Increment the count of used online entries

    def register_ticket_time(self, time):
        """Records the wait time for a ticket purchase.

        Args:
            time (float): The wait time in minutes.
        """
        self.ticket_times.append(time)  # Add the wait time to the list

    def log_event(self, event_data: dict):
        """Logs an event during the visitor's journey.

        Args:
            event_data (dict): Data related to the event to be logged.
        """
        self.journey_log.append(event_data)  # Add event data to the journey log

    def export_journey_log(self, filename="visitor_journey.csv", start_time=600):
        """Exports the journey log to a CSV file, formatting the entry time if present.

        Args:
            filename (str): The name of the file to export the journey log to.
            start_time (int): The start time used to format entry times (default 600 minutes = 10:00 AM).
        """
        if not self.journey_log:
            print("No journey data to export.")  # Check if there is journey data to export
            return

        try:
            # Create a new list with formatted entry_time if present
            formatted_log = []
            for record in self.journey_log:
                if "entry_time" in record:
                    record["entry_time"] = format_time(record["entry_time"], start_time)
                formatted_log.append(record)

            # Write journey log to a CSV file
            with open(filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=formatted_log[0].keys())
                writer.writeheader()  # Write the header row
                writer.writerows(formatted_log)  # Write the journey log rows

            print(f"\nJourney log exported to '{filename}'")  # Confirmation message
        except IOError as e:
            print(f"Error exporting journey log to CSV: {e}")  # Handle file writing errors

    def summary(self):
        """Prints a summary of the collected data and sales statistics."""
        try:
            avg_wait = sum(self.ticket_times) / len(self.ticket_times) if self.ticket_times else 0  # Calculate average wait time
            print(f"\nSummary:")
            print(f"Online sales: {self.online_sales}")
            print(f"Ticket office sales: {self.successful_sales}")
            print(f"Total sales: {self.successful_sales + self.online_sales}")
            print(f"Used online entries: {self.online_entries_used}")
            print(f"Unused online entries: {self.online_sales - self.online_entries_used}")
            print(f"Visitors who did not enter: {self.failed_sales}")
            print(f"Average wait time at ticket office: {avg_wait:.2f} minutes")
        except Exception as e:
            print(f"Error generating summary: {e}")