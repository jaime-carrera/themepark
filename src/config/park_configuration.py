import csv

class ParkConfiguration:
    """
    Loads and stores park configuration settings and attraction definitions from a CSV file.

    Attributes:
        attractions (list): List of attraction configurations.
        ticket_capacity (int): Number of ticket booths (used as default if specific value not present).
        entry_price (float): Price of ticket.
        arrival_rate (float): Visitor arrival rate.
        ticket_counter_capacity (int): Number of ticket sale counters (new).
        turnstile_capacity (int): Number of turnstiles for entry (new).
    """
    def __init__(self, path_csv: str) -> None:
        self.attractions = []
        self.ticket_capacity = 0
        self.entry_price = 0
        self.arrival_rate = 0
        self.ticket_counter_capacity = 0
        self.turnstile_capacity = 0

        with open(path_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Name'] == 'CONFIG':
                    self.ticket_capacity = int(row['Num_Modules'])
                    self.entry_price = float(row['Capacity_per_Module'])
                    self.arrival_rate = float(row['Time_per_Turn'])
                    self.ticket_counter_capacity = int(row.get('Ticket_Counters', 2))
                    self.turnstile_capacity = int(row.get('Turnstiles', 4))

                else:
                    self.attractions.append({
                        'name': row['Name'],
                        'num_modules': int(row['Num_Modules']),
                        'capacity_per_module': int(row['Capacity_per_Module']),
                        'time_per_turn': float(row['Time_per_Turn']),
                        'allowed_public': row['Allowed_Public'].split(',')
                    })