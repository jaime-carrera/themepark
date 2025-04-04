import simpy
import random
from utils.helpers import format_time

class Attraction:
    """
    Represents an attraction in the theme park, managing visitor interactions and maintenance.

    Attributes:
        env (simpy.Environment): The simulation environment.
        name (str): The name of the attraction.
        capacity_per_module (int): The capacity of each module of the attraction.
        time_per_turn (float): The time taken for one complete turn of the attraction.
        allowed_public (list): Types of visitors allowed to use the attraction.
        resource (simpy.Resource): Resource for managing visitor access to the attraction.
        staff (simpy.Resource): Resource for managing staff access to the attraction.
        visitors (int): Count of visitors who have used the attraction.
        wait_times (list): List of wait times for visitors.
        usage_times (list): List of usage times for the attraction.
        popularity (int): Popularity score based on visitor usage.
        status (str): Current operational status of the attraction.
        maintenance_time (int): Random time taken for maintenance.
        usage_for_maintenance (int): Number of visitors after which maintenance is required.
    """
    
    def __init__(self, env: simpy.Environment, name: str, num_modules: int, capacity_per_module: int, time_per_turn: float, allowed_public: list) -> None:
        """Initializes the Attraction with its parameters and resources.

        Args:
            env (simpy.Environment): The simulation environment.
            name (str): The name of the attraction.
            num_modules (int): Number of modules available for the attraction.
            capacity_per_module (int): Capacity of each module.
            time_per_turn (float): Time taken for one complete turn of the attraction.
            allowed_public (list): Types of visitors allowed to use the attraction.
        """
        if num_modules <= 0 or capacity_per_module <= 0 or time_per_turn <= 0:
            raise ValueError("num_modules, capacity_per_module, and time_per_turn must be positive values.")
        
        self.env = env  # Simulation environment
        self.name = name  # Name of the attraction
        self.capacity_per_module = capacity_per_module  # Capacity per module
        self.time_per_turn = time_per_turn  # Time taken for one complete turn
        self.allowed_public = allowed_public  # Allowed visitor types
        self.resource = simpy.Resource(env, capacity=num_modules)  # Resource for visitor access
        self.staff = simpy.Resource(env, capacity=num_modules)  # Resource for staff access
        self.visitors = 0  # Count of visitors who have used the attraction
        self.wait_times = []  # List to store wait times
        self.usage_times = []  # List to store usage times
        self.popularity = 0  # Popularity score
        self.status = "operational"  # Current status of the attraction
        self.maintenance_time = random.randint(100, 500)  # Random maintenance time
        self.usage_for_maintenance = random.randint(400, 600)  # Visitors count for maintenance trigger

    def use(self, visitor, start_time):
        """
        Simulates the use of the attraction by a visitor.

        Args:
            visitor (dict): Visitor data including id and satisfaction level.
            start_time (int): Start time of the park in minutes.

        Returns:
            dict: Information about the attraction usage including wait and usage times.
        """
        try:
            # Check if the attraction is operational and if the visitor is allowed
            if self.status != "operational" or visitor['type'] not in self.allowed_public:
                return None  # Not allowed or under maintenance

            arrival_time = self.env.now  # Record the arrival time of the visitor

            # Request access to the attraction and staff resources
            with self.resource.request() as req, self.staff.request() as staff:
                yield req & staff  # Wait until both resources are available
                wait_time = max(0, self.env.now - arrival_time) # Calculate wait time
                self.wait_times.append(wait_time)  # Log the wait time

                # Adjust visitor satisfaction based on wait time
                if wait_time > 5:
                    decrement = int(wait_time // 5) * 2  # Decrease for each 5-minute block over 5 minutes
                    visitor['satisfaction'] = max(0, visitor['satisfaction'] - decrement)

                # Boarding and instructions
                boarding_time = random.uniform(0.5, 1.5)  # Random boarding time
                yield self.env.timeout(boarding_time)  # Simulate boarding time

                # Actual ride
                yield self.env.timeout(self.time_per_turn)  # Simulate the ride duration
                usage_time = max(0, self.time_per_turn)  # Record usage time
                self.usage_times.append(usage_time)  # Log the usage time

                self.visitors += 1  # Increment visitor count
                self.popularity += 1  # Increment popularity score

                # Log visitor enjoyment
                print(f"[{format_time(self.env.now, start_time)}] Visitor {visitor['id']} enjoyed {self.name}")

                # Check if maintenance is needed after a certain number of visitors
                if self.visitors % self.usage_for_maintenance == 0:
                    self.status = "maintenance"  # Set status to maintenance
                    print(f"[{format_time (self.env.now, start_time)}] {self.name} under maintenance.")
                    yield self.env.timeout(self.maintenance_time)  # Simulate maintenance time
                    print(f"[{format_time(self.env.now, start_time)}] {self.name} is back in operation.")
                    self.status = "operational"  # Restore operational status

                return {
                    'attraction': self.name,
                    'wait': wait_time,
                    'usage': usage_time
                }
        except Exception as e:
            print(f"Error during usage of {self.name} by visitor {visitor['id']}: {e}")
            return None  # Handle error as needed

    def statistics(self) -> dict:
        """Calculates and returns statistics about the attraction's usage.

        Returns:
            dict: A dictionary containing the attraction's name, visitor count, average wait time, average usage time, popularity, and status.
        """
        try:
            avg_wait = sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0
            avg_usage = sum(self.usage_times) / len(self.usage_times) if self.usage_times else 0
            return {
                'name': self.name,
                'visitors': self.visitors,
                'avg_wait': avg_wait,
                'avg_usage': avg_usage,
                'popularity': self.popularity,
                'status': self.status
            }
        except Exception as e:
            print(f"Error calculating statistics for {self.name}: {e}")
            return {
                'name': self.name,
                'visitors': self.visitors,
                'avg_wait': 0,
                'avg_usage': 0,
                'popularity': self.popularity,
                'status': self.status
            }