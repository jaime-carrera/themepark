import simpy
import random
from utils.helpers import format_time

class Attraction:
    def __init__(self, env: simpy.Environment, name: str, num_modules: int, capacity_per_module: int, time_per_turn: float, allowed_public: list) -> None:
        self.env = env
        self.name = name
        self.capacity_per_module = capacity_per_module
        self.time_per_turn = time_per_turn
        self.allowed_public = allowed_public
        self.resource = simpy.Resource(env, capacity=num_modules)
        self.staff = simpy.Resource(env, capacity=num_modules)
        self.visitors = 0
        self.wait_times = []
        self.usage_times = []
        self.popularity = 0
        self.status = "operational"
        self.maintenance_time = random.randint(100, 500)
        self.usage_for_maintenance = random.randint(400, 600)

    def use(self, visitor: dict):
        if self.status != "operational" or visitor['type'] not in self.allowed_public:
            return None
        arrival_time = self.env.now
        with self.resource.request() as req, self.staff.request() as staff:
            yield req & staff
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)
            if wait_time > 5:
                visitor['satisfaction'] -= int(wait_time // 5) * 2
            yield self.env.timeout(self.time_per_turn)
            usage_time = self.time_per_turn
            self.usage_times.append(usage_time)
            self.visitors += 1
            self.popularity += 1
            print(f"[{format_time(self.env.now)}] Visitor {visitor['id']} enjoyed {self.name}")
            if self.visitors % self.usage_for_maintenance == 0:
                self.status = "maintenance"
                yield self.env.timeout(self.maintenance_time)
                self.status = "operational"
            return {'attraction': self.name, 'wait': wait_time, 'usage': usage_time}

    def statistics(self) -> dict:
        return {
            'name': self.name,
            'visitors': self.visitors,
            'avg_wait': sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0,
            'avg_usage': sum(self.usage_times) / len(self.usage_times) if self.usage_times else 0,
            'popularity': self.popularity,
            'status': self.status
        }
