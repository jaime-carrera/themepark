import csv

class DataCollector:
    def __init__(self):
        self.visitor_data = []
        self.successful_sales = 0
        self.failed_sales = 0
        self.online_sales = 0
        self.online_entries_used = 0
        self.ticket_times = []

    def register_visitor(self, data):
        self.visitor_data.append(data)
        self.successful_sales += 1

    def register_failure(self):
        self.failed_sales += 1

    def register_online_sale(self, used):
        self.online_sales += 1
        if used:
            self.online_entries_used += 1

    def register_ticket_time(self, time):
        self.ticket_times.append(time)

    def export_to_csv(self, filename="visitor_data.csv"):
        if not self.visitor_data:
            print("No data to export.")
            return

        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.visitor_data[0].keys())
            writer.writeheader()
            writer.writerows(self.visitor_data)
        print(f"\nVisitor data exported to {filename}")

    def summary(self):
        avg_wait = sum(self.ticket_times) / len(self.ticket_times) if self.ticket_times else 0
        print(f"\nSummary:")
        print(f"Online sales: {self.online_sales}")
        print(f"Ticket office sales: {self.successful_sales}")
        print(f"Total sales: {self.successful_sales + self.online_sales}")
        print(f"Used online entries: {self.online_entries_used}")
        print(f"Unused online entries: {self.online_sales - self.online_entries_used}")
        print(f"Visitors who did not enter: {self.failed_sales}")
        print(f"Average wait time at ticket office: {avg_wait:.2f} minutes")

    @staticmethod
    def combine_collectors(collectors):
        """Combine multiple DataCollector instances into one."""
        combined = DataCollector()
        for collector in collectors:
            combined.visitor_data.extend(collector.visitor_data)
            combined.successful_sales += collector.successful_sales
            combined.failed_sales += collector.failed_sales
            combined.online_sales += collector.online_sales
            combined.online_entries_used += collector.online_entries_used
            combined.ticket_times.extend(collector.ticket_times)
        return combined