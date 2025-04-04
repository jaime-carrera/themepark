import random
from utils.helpers import format_time
import simpy

class TicketOffice:
    def __init__(self, env, ticket_counter_capacity, turnstile_capacity, entry_price, data_collector):
        """
        Manages the ticketing and entry process of the theme park.

        Args:
            env (simpy.Environment): Simulation environment.
            ticket_counter_capacity (int): Number of ticket booths.
            turnstile_capacity (int): Number of turnstiles.
            entry_price (float): Ticket price for entry.
            data_collector (DataCollector): Collector for all visitor-related data.
        """
        if not isinstance(ticket_counter_capacity, int) or ticket_counter_capacity <= 0:
            raise ValueError("Ticket counter capacity must be a positive integer.")
        if not isinstance(turnstile_capacity, int) or turnstile_capacity <= 0:
            raise ValueError("Turnstile capacity must be a positive integer.")
        if not isinstance(entry_price, (int, float)) or entry_price < 0:
            raise ValueError("Entry price must be a positive number.")
        if data_collector is None:
            raise ValueError("Data collector cannot be None.")
        
        self.env = env  # Simulation environment
        self.entry_price = entry_price  # Price of the entry ticket
        self.ticket_booths = simpy.Resource(env, capacity=ticket_counter_capacity)  # Resource for ticket booths
        self.turnstiles = simpy.Resource(env, capacity=turnstile_capacity)  # Resource for turnstiles
        self.revenue = 0  # Total revenue from ticket sales
        self.data_collector = data_collector  # Data collector instance for tracking visitor data

    def purchase(self, visitor, start_time):
        """
        Handles a visitor's entry process including ticket booth and turnstile access.

        Args:
            visitor (dict): Contains visitor information including type, satisfaction, and ticket method.
            start_time (int): The opening time of the park in minutes.

        Returns:
            bool: Whether the visitor was able to enter the park.
        """
        try:
            # If the visitor has an online ticket
            if visitor.get("online", False):
                self.data_collector.register_online_sale(used=True)  # Register the online sale as used

                with self.turnstiles.request() as turn_req:  # Request access to a turnstile
                    yield turn_req  # Wait for turnstile access
                    yield self.env.timeout(random.uniform(0.2, 1.0))  # Simulate time taken to enter
                    print(f"[{format_time(self.env.now, start_time)}] Visitor {visitor['id']} entered through turnstile.")
                return True  # Visitor successfully entered

            # If the queue at the ticket booth is too long
            if len(self.ticket_booths.queue) > 10:
                visitor["satisfaction"] -= 20  # Decrease visitor satisfaction due to long wait
                if visitor["satisfaction"] < 30:  # If satisfaction drops below threshold
                    self.data_collector.register_failure()  # Register a failed entry
                    self.data_collector.register_visitor({
                        "id": visitor["id"],
                        "type": visitor["type"],
                        "ticket_type": "ticket_office",
                        "attractions_visited": 0,
                        "total_time": 0,
                        "avg_wait": 0,
                        "avg_usage": 0,
                        "final_satisfaction": visitor["satisfaction"],
                        "entered_park": False
                    })
                    print(f"[{format_time(self.env.now, start_time)}] Visitor {visitor['id']} left due to long queue at ticket booth.")
                    return False  # Visitor could not enter

            start_time = self.env.now  # Record the current time for ticket purchase
            with self.ticket_booths.request() as booth_req:  # Request access to a ticket booth
                yield booth_req  # Wait for booth access
                yield self.env.timeout(random.uniform(0.5, 2.0))  # Simulate time taken to purchase ticket
                wait_time = self.env.now - start_time  # Calculate wait time
                self.data_collector.register_ticket_time(wait_time)  # Log the wait time
                self.revenue += self.entry_price  # Increase revenue by ticket price
                print(f"[{format_time(self.env.now, start_time)}] Visitor {visitor['id']} purchased ticket at ticket booth.")

            with self.turnstiles.request() as turn_req:  # Request access to a turnstile
                yield turn_req  # Wait for turnstile access
                yield self.env.timeout(random.uniform(0.2, 1.0))  # Simulate time taken to enter
                print(f"[{format_time(self.env.now, start_time)}] Visitor {visitor['id']} entered through turnstile.")
            return True  # Visitor successfully entered
        except Exception as e:
            print(f"Error during ticket purchase: {e}")  # Log the error for debugging purposes
            return False  # Visitor could not enter