import csv

class ParkConfiguration:
    """
    Loads and stores park configuration settings and attraction definitions from a CSV file.

    Attributes:
        attractions (list): List of attraction configurations.
        ticket_capacity (int): Number of ticket booths (used as default if specific value not present).
        entry_price (float): Price of ticket.
        base_arrival_rate (float): Base visitor arrival rate.
        ticket_counter_capacity (int): Number of ticket sale counters (new).
        turnstile_capacity (int): Number of turnstiles for entry (new).
        sim_duration (int): Duration of the simulation in minutes.
        start_hour (int): Opening hour of the park (e.g. 10 for 10:00 AM).
        end_hour (int): Closing hour of the park (e.g. 18 for 6:00 PM).
        start_time (int): Opening time in minutes.
        end_time (int): Closing time in minutes.
    """
   
    def __init__(self, path_csv: str) -> None:
        """Initializes the ParkConfiguration with default values and loads settings from a CSV file.

        Args:
            path_csv (str): Path to the CSV file containing park configuration.
        """
        self.attractions = []  # List to store attraction configurations
        self.ticket_capacity = 0  # Default ticket booth capacity
        self.entry_price = 0.0  # Default entry price
        self.base_arrival_rate = 0.0  # Default visitor arrival rate
        self.ticket_counter_capacity = 0  # Default ticket counter capacity
        self.turnstile_capacity = 0  # Default turnstile capacity
        self.sim_duration = 480  # Default simulation duration in minutes
        self.start_hour = 10  # Default opening hour (10:00 AM)
        self.end_hour = 18  # Default closing hour (6:00 PM)
        self.start_time = self.start_hour * 60  # Opening time in minutes
        self.end_time = self.end_hour * 60  # Closing time in minutes

        # Load configuration from the specified CSV file
        with open(path_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)  # Read the CSV file as a dictionary
            for row in reader:
                if row['Name'] == 'CONFIG':  # Check if the row is for configuration
                    self.ticket_capacity = int(row['Num_Modules'])  # Set ticket booth capacity
                    self.entry_price = float(row['Capacity_per_Module'])  # Set entry price
                    self.base_arrival_rate = float(row['Base_Arrival_Rate'])  # Set base visitor arrival rate
                    self.ticket_counter_capacity = int(row.get('Ticket_Counters', 2))  # Set ticket counter capacity, default to 2
                    self.turnstile_capacity = int(row.get('Turnstiles', 4))  # Set turnstile capacity, default to 4
                    self.sim_duration = int(row.get('Sim_Duration', 480))  # Set simulation duration, default to 480 minutes

                    # Read opening and closing hours if they exist
                    if row.get('Start_Hour'):
                        self.start_hour = int(row['Start_Hour'])  # Set opening hour
                    if row.get('End_Hour'):
                        self.end_hour = int(row['End_Hour'])  # Set closing hour

                    # Update opening and closing times in minutes
                    self.start_time = self.start_hour * 60
                    self.end_time = self.end_hour * 60

                else:  # If the row is not a configuration, it is an attraction
                    self.attractions.append({
                        'name': row['Name'],  # Name of the attraction
                        'num_modules': int(row['Num_Modules']),  # Number of modules for the attraction
                        'capacity_per_module': int(row['Capacity_per_Module']),  # Capacity per module
                        'time_per_turn': float(row['Time_per_Turn']),  # Time taken for one turn
                        'allowed_public': row['Allowed_Public'].split(',') if row['Allowed_Public'] else []  # Allowed public types
                    })