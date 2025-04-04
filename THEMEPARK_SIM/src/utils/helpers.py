import random

def format_time(minutes, start_time=600):
    """
    Converts simulation minutes into HH:MM format.
    Optionally shifts time based on start_time in minutes (default is 600 = 10:00 AM).
   
    Args:
        minutes (int): The number of minutes to convert.
        start_time (int): The starting time in minutes (default is 600, which represents 10:00 AM).
   
    Returns:
        str: The formatted time in HH:MM format.
    """
    total_minutes = int(minutes + start_time)  # Calculate total minutes by adding simulation minutes to start time
    hours = total_minutes // 60  # Calculate hours
    mins = total_minutes % 60  # Calculate remaining minutes
    return f"{hours:02d}:{mins:02d}"  # Return formatted time as a string

def print_summary(day_name, collector, ticket_office):
    """
    Prints a summary of the day's statistics including sales and visitor data.
   
    Args:
        day_name (str): The name of the day being summarized.
        collector (DataCollector): The data collector instance containing visitor statistics.
        ticket_office (TicketOffice): The ticket office instance to access entry price.
    """
    avg_wait = (
        sum(collector.ticket_times) / len(collector.ticket_times)  # Calculate average wait time if there are recorded times
        if collector.ticket_times else 0  # If no wait times, set average wait to 0
    )

    # Print summary information
    print(f"\n Summary for {day_name}")  # Print day summary header with an icon
    print(f"Online sales: {collector.online_sales}")  # Print total online sales
    print(f"Ticket office sales: {collector.successful_sales}")  # Print total ticket office sales
    print(f"Total sales: {collector.successful_sales + collector.online_sales}")  # Print total sales
    print(f"Used online entries: {collector.online_entries_used}")  # Print count of used online entries
    print(f"Unused online entries: {collector.online_sales - collector.online_entries_used}")  # Print count of unused online entries
    print(f"Visitors who did not enter: {collector.failed_sales}")  # Print count of visitors who failed to enter
    print(f"Average wait at ticket office: {avg_wait:.2f} minutes")  # Print average wait time formatted to two decimal places
    print(f"Revenue for the day: ${collector.successful_sales * ticket_office.entry_price:.2f}")  # Print total revenue for the day

def generate_visitors(env, park, base_arrival_rate, park_open_time, park_close_time):
    """
    Generates visitors at the park according to the specified arrival rate that varies throughout the day.
   
    Args:
        env (simpy.Environment): The simulation environment.
        park (ThemePark): The theme park instance where visitors will be generated.
        base_arrival_rate (float): The base arrival rate for visitors.
        park_open_time (int): The opening time of the park in minutes.
        park_close_time (int): The closing time of the park in minutes.
    """
    visitor_id = 0  # Initialize visitor ID
    while True:  # Infinite loop to continuously generate visitors
        current_time = env.now  # Get the current time in the simulation

        # Calculate the arrival rate based on the current time
        if current_time < park_open_time + 60:  # First hour after opening
            arrival_rate = base_arrival_rate * 2  # Double the rate
        elif current_time < park_open_time + 120:  # Second hour after opening
            arrival_rate = base_arrival_rate * 1.5  # 1.5 times the base rate
        elif current_time > park_close_time - 120:  # Last two hours before closing
            arrival_rate = base_arrival_rate * 0.2  # Reduce to 20% of the base rate
        else:
            arrival_rate = base_arrival_rate  # Normal rate

        visitor = {
            "id": f"V{visitor_id:04d}",  # Generate a unique visitor ID in the format V0000
            "type": random.choice(["adult", "child", "teen"]),  # Randomly assign a visitor type
            "satisfaction": 100,  # Initialize satisfaction level
            "fatigue": 0,  # Initialize fatigue level
            "online": random.random() < 0.4  # Randomly determine if the visitor has an online ticket (40% chance)
        }

        env.process(park.visit(visitor))  # Process the visitor's visit to the park
        yield env.timeout(random.expovariate(arrival_rate))  # Wait for the next visitor based on the adjusted arrival rate
        visitor_id += 1  # Increment visitor ID for the next visitor