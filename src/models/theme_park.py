import random

class ThemePark:
    def __init__(self, env, attractions, ticket_office, data_collector):
        self.env = env
        self.attractions = attractions
        self.ticket_office = ticket_office
        self.data_collector = data_collector

    def visit(self, visitor):
        """
        Simulates the experience of a single visitor in the park:
        - Buys ticket (if needed)
        - Passes through a turnstile
        - Visits attractions while they still have energy and are satisfied
        """
        # Intentar entrar al parque (taquilla + torno)
        access = yield self.env.process(self.ticket_office.purchase_and_enter(visitor))
        if not access:
            return  # No entró al parque

        entry_time = self.env.now
        interactions = 0
        total_wait = 0
        total_usage = 0

        # Simulación de recorrido por atracciones
        while visitor['fatigue'] < 10 and visitor['satisfaction'] > 30:
            available_attractions = [
                a for a in self.attractions
                if visitor['type'] in a.allowed_public and a.status == "operational"
            ]
            if not available_attractions:
                break  # No hay atracciones disponibles

            attraction = random.choice(available_attractions)
            result = yield self.env.process(attraction.use(visitor))
            if result:
                interactions += 1
                total_wait += result['wait']
                total_usage += result['usage']

            visitor['fatigue'] += 1
            visitor['satisfaction'] -= random.randint(5, 15)
            yield self.env.timeout(random.randint(1, 3))

        exit_time = self.env.now
        self.data_collector.register_visitor({
            'id': visitor['id'],
            'type': visitor['type'],
            'attractions_used': interactions,
            'total_time': exit_time - entry_time,
            'avg_wait': total_wait / interactions if interactions else 0,
            'avg_usage': total_usage / interactions if interactions else 0,
            'final_satisfaction': visitor['satisfaction']
        })
