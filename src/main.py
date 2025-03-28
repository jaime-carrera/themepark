import simpy
from config.park_configuration import ParkConfiguration
from data.data_collector import DataCollector
from models.attraction import Attraction
from models.ticket_office import TicketOffice
from models.theme_park import ThemePark
from utils.helpers import generate_visitors
from utils.helpers import print_summary

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


if __name__ == "__main__":
    csv_file = "themepark_project/src/themepark1_large.csv"
    config = ParkConfiguration(csv_file)

    weekly_collectors = []
    weekly_attractions = []

    for day_index in range(7):
        day_name = DAYS_OF_WEEK[day_index]
        print(f"\n Simulating Day {day_index + 1} ({day_name})")

        env = simpy.Environment()
        daily_collector = DataCollector()
        attractions = [Attraction(env, **a) for a in config.attractions]

        ticket_office = TicketOffice(
            env,
            ticket_counter_capacity=config.ticket_counter_capacity,
            turnstile_capacity=config.turnstile_capacity,
            entry_price=config.entry_price,
            data_collector=daily_collector
        )

        park = ThemePark(env, attractions, ticket_office, daily_collector)

        env.process(generate_visitors(env, park, config.arrival_rate))
        env.run(until=480)

        # Print attraction statistics
        print("\n Attraction Statistics:")
        for attraction in attractions:
            stats = attraction.statistics()
            print(f"{stats['name']} → Visitors: {stats['visitors']} | "
                  f"Avg Wait: {stats['avg_wait']:.2f} | "
                  f"Avg Usage: {stats['avg_usage']:.2f} | "
                  f"Popularity: {stats['popularity']}")

        # Daily summary
        print_summary(day_name, daily_collector, ticket_office)

        # Accumulate for weekly report
        weekly_collectors.append(daily_collector)
        weekly_attractions.append(attractions)

    # Combine data from all 7 days
    print("\n WEEKLY SUMMARY ")
    combined_collector = DataCollector.combine_collectors(weekly_collectors)

    print_summary("the whole week", combined_collector, ticket_office)  # Uses last ticket office instance just for revenue
