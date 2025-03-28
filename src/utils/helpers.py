import datetime
import random

def format_time(minutes: int) -> str:
    base_time = datetime.datetime(2023, 1, 1, 10, 0)
    sim_time = base_time + datetime.timedelta(minutes=minutes)
    return sim_time.strftime("%H:%M")


def generate_visitors(env, park, base_rate):
    visitor_id = 0
    while True:
        # Tasa adaptada por hora
        current_minute = env.now
        if current_minute >= 420:
            rate = base_rate * 0.1
        elif current_minute >= 360:
            rate = base_rate * 0.3
        elif current_minute >= 300:
            rate = base_rate * 0.6
        else:
            rate = base_rate

        yield env.timeout(random.expovariate(rate))

        online = random.random() < 0.2
        if online and random.random() < 0.1:
            # No se presenta
            park.data_collector.register_online_sale(used=False)
            continue

        visitor_type = random.choice(["child", "adult", "senior"])
        visitor = {
            "id": f"{'OV' if online else 'V'}{visitor_id}",
            "type": visitor_type,
            "fatigue": 0,
            "satisfaction": 100,
            "online": online
        }

        if online:
            park.data_collector.register_online_sale(used=True)

        visitor_id += 1
        env.process(park.visit(visitor))
        
def print_summary(day_name, collector, ticket_office):
    print(f"\n📊 Summary for {day_name}:")
    print(f"Online sales: {collector.online_sales}")
    print(f"Ticket office sales: {collector.successful_sales}")
    print(f"Total sales: {collector.online_sales + collector.successful_sales}")
    print(f"Used online entries: {collector.online_entries_used}")
    print(f"Unused online entries: {collector.online_sales - collector.online_entries_used}")
    print(f"Visitors who did not enter: {collector.failed_sales}")
    print(f"Total revenue: {ticket_office.revenue:.2f} €")
    if collector.ticket_times:
        avg_wait = sum(collector.ticket_times) / len(collector.ticket_times)
        print(f"Average wait time at ticket office: {avg_wait:.2f} minutes")
    else:
        print("Average wait time at ticket office: N/A")

