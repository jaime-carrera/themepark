import simpy
import random
import numpy as np
import os
from config.park_configuration import ParkConfiguration
from data.data_collector import DataCollector
from models.attraction import Attraction
from models.ticket_office import TicketOffice
from models.theme_park import ThemePark
from utils.helpers import generate_visitors, print_summary

# Days of the week for simulation
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

#Set a fixef seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)


if __name__ == "__main__":
    try:
        # Load park configuration from CSV file
        csv_file = os.path.join(os.path.dirname(__file__), "./altontowers.csv")
        config = ParkConfiguration(csv_file)  # Initialize park configuration

        # Create a data collector to track visitor statistics for the week
        weekly_collector = DataCollector()

        # Simulate each day of the week
        for day_index in range(7):
            day_name = DAYS_OF_WEEK[day_index]  # Get the name of the current day
            print(f"\nSimulating Day {day_index + 1} ({day_name})")

            env = simpy.Environment()  # Create a new simulation environment
            
            # Initialize attractions based on the configuration
            attractions = []
            for a in config.attractions:
                try:
                    attractions.append(Attraction(env, **a))
                except Exception as e:
                    print(f"Error initializing attraction {a['name']}: {e}")
                    continue  # Skip this attraction if there's an error

            # Initialize the ticket office with the specified capacities and entry price
            try:
                ticket_office = TicketOffice(
                    env,
                    ticket_counter_capacity=config.ticket_counter_capacity,
                    turnstile_capacity=config.turnstile_capacity,
                    entry_price=config.entry_price,
                    data_collector=weekly_collector
                )
            except Exception as e:
                print(f"Error initializing ticket office: {e}")
                continue  # Skip this day if there's an error

            # Create the theme park instance
            try:
                park = ThemePark(
                    env,
                    attractions,
                    ticket_office,
                    weekly_collector,
                    day_name,
                    start_time=config.start_time
                )
            except Exception as e:
                print(f"Error initializing theme park: {e}")
                continue  # Skip this day if there's an error

            # Generate visitors for the day based on the arrival rate
            base_arrival_rate = config.base_arrival_rate
            park_open_time = config.start_time
            park_close_time = config.start_time + config.sim_duration
            
            env.process(generate_visitors(env, park, base_arrival_rate, park_open_time, park_close_time))
            env.run(until=config.sim_duration)  # Run the simulation until the specified duration

            # Print statistics for each attraction after the day's simulation
            print("\nAttraction Statistics:")
            print(f"{'Name':<20} {'Visitors':>9} {'Avg Wait':>10} {'Avg Usage':>11} {'Popularity':>12}")
            print("-" * 65)
            for attraction in attractions:
                stats = attraction.statistics()
                print(f"{stats['name']:<20} {stats['visitors']:>9} {stats['avg_wait']:>10.2f} {stats['avg_usage']:>11.2f} {stats['popularity']:>12}")


            # Print a summary of the day's visitor data
            print_summary(day_name, weekly_collector, ticket_office)

        # Export all journey logs at once to a CSV file
        weekly_collector.export_journey_log(filename="weekly_visitors.csv")

    except FileNotFoundError:
        print(f"Error: The configuration file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")