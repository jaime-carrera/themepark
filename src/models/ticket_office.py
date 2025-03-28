import simpy
import random
from utils.helpers import format_time

class TicketOffice:
    def __init__(self, env, ticket_counter_capacity, turnstile_capacity, entry_price, data_collector):
        self.env = env
        self.entry_price = entry_price
        self.ticket_counters = simpy.Resource(env, capacity=ticket_counter_capacity)
        self.turnstiles = simpy.Resource(env, capacity=turnstile_capacity)
        self.revenue = 0
        self.data_collector = data_collector
        self.turn_ids = list(range(1, turnstile_capacity + 1))

    def purchase_and_enter(self, visitor):
        # Si necesita comprar entrada
        if not visitor['online']:
            with self.ticket_counters.request() as ticket_req:
                yield ticket_req
                yield self.env.timeout(random.uniform(0.5, 2))

                if len(self.ticket_counters.queue) > 10:
                    visitor['satisfaction'] -= 20
                    if visitor['satisfaction'] < 30:
                        self.data_collector.register_failure()
                        print(f"[{format_time(self.env.now)}] Visitor {visitor['id']} abandoned due to ticket queue.")
                        return False

                self.revenue += self.entry_price
                self.data_collector.register_ticket_time(self.env.now)
                self.data_collector.successful_sales += 1
                print(f"[{format_time(self.env.now)}] Visitor {visitor['id']} bought ticket at counter.")

        # Ahora intenta entrar por un torno
        with self.turnstiles.request() as turn_req:
            yield turn_req
            yield self.env.timeout(random.uniform(0.3, 1))  # control de acceso
            turn_id = random.choice(self.turn_ids)
            print(f"[{format_time(self.env.now)}] Visitor {visitor['id']} entered through turnstile {turn_id}.")
            return True


