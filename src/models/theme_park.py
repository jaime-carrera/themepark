import random

class ThemePark:
    def __init__(self, env, attractions, ticket_office, data_collector, day_name, start_time):
        """
        Theme park simulator that manages visitor interactions.

        Args:
            env (simpy.Environment): Simulation environment.
            attractions (list): List of Attraction instances.
            ticket_office (TicketOffice): Manages ticket logic.
            data_collector (DataCollector): Tracks visitor stats.
            day_name (str): Name of the day for logging purposes.
            start_time (int): Park opening time in minutes.
        """
        if not isinstance(attractions, list) or not attractions:
            raise ValueError("Attractions must be a non-empty list.")
        if ticket_office is None:
            raise ValueError("Ticket office cannot be None.")
        if data_collector is None:
            raise ValueError("Data collector cannot be None.")
        if not isinstance(day_name, str) or not day_name:
            raise ValueError("Day name must be a non-empty string.")
        if not isinstance(start_time, (int, float)) or start_time < 0:
            raise ValueError("Start time must be a non-negative number.")
        
        self.env = env  # Simulation environment
        self.attractions = attractions  # List of attractions in the park
        self.ticket_office = ticket_office  # Ticket office instance for managing ticket purchases
        self.data_collector = data_collector  # Data collector instance for tracking visitor statistics
        self.day = day_name  # Name of the day for logging purposes
        self.start_time = start_time  # Park opening time in minutes

    def visit(self, visitor):
        """
        Manages the full visit flow for a single visitor.

        Args:
            visitor (dict): Includes id, type, satisfaction, fatigue, and ticket type.
        """
        try:
            # Process the ticket purchase for the visitor
            entered = yield self.env.process(self.ticket_office.purchase(visitor, self.start_time))

            if not entered:
                return  # Exit if the visitor could not enter the park

            # Mark online entry as used if applicable
            if visitor.get("online", False):
                self.data_collector.mark_online_entry_used()

            entry_time = self.env.now  # Record the entry time of the visitor
            visitor["entry_time"] = entry_time  # Store entry time in visitor data

            attractions_visited = 0  # Counter for attractions visited
            total_wait = 0  # Total wait time for attractions
            total_usage = 0  # Total usage time for attractions

            # Loop until the visitor is fatigued or satisfaction drops below a threshold
            while visitor["fatigue"] < 10 and visitor["satisfaction"] > 30:
                # Filter available attractions based on visitor type and operational status
                available_attractions = [
                    a for a in self.attractions
                    if visitor["type"] in a.allowed_public and a.status == "operational"
                ]
                if not available_attractions:
                    break  # Exit if no attractions are available

                # Randomly select an attraction from the available ones
                attraction = random.choice(available_attractions)
                result = yield self.env.process(attraction.use(visitor, self.start_time))  # Simulate using the attraction

                if result:
                    attractions_visited += 1  # Increment attractions visited counter
                    total_wait += result["wait"]  # Accumulate total wait time
                    total_usage += result["usage"]  # Accumulate total usage time

                    # Log the event of the visit
                    self.data_collector.log_event({
                        "id": visitor["id"],
                        "type": visitor["type"],
                        "ticket_type": "online" if visitor.get("online") else "ticket_office",
                        "attraction": result["attraction"],
                        "wait_at_attraction": round(result["wait"], 2),
                        "ride_duration": round(result["usage"], 2),
                        "satisfaction_status": visitor["satisfaction"],
                        "fatigue": visitor["fatigue"],
                        "time": round(self.env.now, 2),
                        "day": self.day,
                        "time_of_entry": round(entry_time, 2),
                        "time_left": None,  # to be filled later
                        "entered_park": True,
                        "attractions_visited_so_far": attractions_visited
                    })

                # Update visitor's fatigue and satisfaction
                visitor["fatigue"] += 1
                visitor["satisfaction"] -= random.randint(5, 15)  # Randomly decrease satisfaction
                yield self.env.timeout(random.randint(1, 3))  # Simulate time spent between attractions

            exit_time = self.env.now  # Record the exit time of the visitor

            # Update the "time_left" field in previous logs for this visitor
            for entry in self.data_collector.journey_log:
                if entry["id"] == visitor["id"] and entry["time_left"] is None:
                    entry["time_left"] = round(exit_time, 2)  # Fill in the exit time

            # Save the final summary of the visitor's experience
            self.data_collector.register_visitor({
                "id": visitor["id"],
                "type": visitor["type"],
                "ticket_type": "online" if visitor.get("online") else "ticket_office",
                "attractions_visited": attractions_visited,
                "total_time": round(exit_time - entry_time, 2),  # Total time spent in the park
                "avg_wait": round(total_wait / attractions_visited, 2) if attractions_visited else 0,  # Average wait time
                "avg_usage": round(total_usage / attractions_visited, 2) if attractions_visited else 0,  # Average usage time
                "final_satisfaction": visitor["satisfaction"],  # Final satisfaction level
                "entered_park": True
            })
        except Exception as e:
            print(f"Error during visitor's experience: {e}")  # Log the error for debugging purposes